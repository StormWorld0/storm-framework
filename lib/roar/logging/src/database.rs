use pyo3::prelude::*;
use rusqlite::Connection;
use std::fs;
use std::path::PathBuf;
use crate::errors::PrintResult;

pub fn get_db_connection(py: Python<'_>) -> PrintResult<Connection> {
    // Extract Path from Python (Borrowing python's GIL for a moment)
    let rootmap_mod = PyModule::import(py, "rootmap")?;
    let root_py = rootmap_mod.getattr("ROOT")?;
    let root_path_str: String = root_py.call_method0("__str__")?.extract()?;
    let root_path = PathBuf::from(root_path_str);

    // Arrange Directory Paths
    // Results: ROOT/lib/sqlite/logging
    let output_dir = root_path.join("lib").join("sqlite").join("logging");
    
    // Complete File Path Arrangement
    // Results: ROOT/lib/sqlite/logging/log.db
    let file_path = output_dir.join("log.db");

    // Ensure Directory is Available (Pre-flight check)
    if !output_dir.exists() {
        // We catch the IO error and convert it to PrintResult (via ? operator)
        fs::create_dir_all(&output_dir)?;
    }

    // Open SQLite Connection (Automatically create log.db file if it doesn't exist)
    // ? operator here will be thrown as SqliteError to PrintResult
    let conn = Connection::open(file_path)?;
    
    // High-Performance Database Engine Configuration
    conn.execute_batch(
        "PRAGMA journal_mode = WAL;
         PRAGMA synchronous = NORMAL;
         PRAGMA temp_store = MEMORY;
         PRAGMA busy_timeout = 5000;
         
         CREATE TABLE IF NOT EXISTS system_logs (
             id INTEGER PRIMARY KEY AUTOINCREMENT,
             timestamp REAL,
             level TEXT,
             label TEXT,
             payload TEXT,
             caller TEXT,
             location TEXT,
             traceback TEXT
         );
         CREATE INDEX IF NOT EXISTS idx_system_logs_timestamp ON system_logs(timestamp);
         ",
    )?;
    
    Ok(conn)
}

pub fn insert_log(
    conn: &Connection, 
    timestamp: f64, 
    level: &str, 
    label: &str, 
    payload: &str,
    caller: &str,
    location: &str,
    traceback: &str
) -> PrintResult<()> {
    // Transaction Immediate: Explicitly lock the database before writing.
    // This isolates Rust INSERT/DELETE so that Python doesn't read a half-finished B-Tree.
    let tx = conn.unchecked_transaction()?;
    
    tx.execute(
        "INSERT INTO system_logs (timestamp, level, label, payload, caller, location, traceback) VALUES (?1, ?2, ?3, ?4, ?5, ?6, ?7)",
        (timestamp, level, label, payload, caller, location, traceback),
    )?;

    let should_cleanup = rand::random::<u8>() < 3; // Probability ~1% (requires crate `rand`)
    
    if should_cleanup {
        // Calculate cutoff directly from f64 `timestamp`
        let retention_seconds = (3 * 24 * 60 * 60) as f64; // 3Day
        let cutoff_timestamp = timestamp - retention_seconds;
        
        // Delete by time
        tx.execute(
            "DELETE FROM system_logs
             WHERE timestamp < ?1",
            [cutoff_timestamp],
        )?;

        //  O(1) Safe Clean-up 10.000 rows limit
        tx.execute(
            "DELETE FROM system_logs 
             WHERE id <= (
                 SELECT id FROM system_logs 
                 ORDER BY id DESC 
                 LIMIT 1 OFFSET 10000
             )",
            [],
        )?;
    }
    
    tx.commit()?;
    Ok(())
}
