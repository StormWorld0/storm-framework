// File: src/database.rs
use pyo3::prelude::*;
use rusqlite::Connection;
use std::fs;
use std::path::PathBuf;
use crate::errors::PrintResult;

pub fn get_db_connection(py: Python<'_>) -> PrintResult<Connection> {
    // 1. Ekstrak Path dari Python (Butuh GIL Token)
    let rootmap_mod = PyModule::import(py, "rootmap")?;
    let root_py = rootmap_mod.getattr("ROOT")?;
    let root_path_str: String = root_py.call_method0("__str__")?.extract()?;
    let root_path = PathBuf::from(root_path_str);

    // 2. Susun Path Direktori
    // Hasil: ROOT/lib/sqlite/logging
    let output_dir = root_path.join("lib").join("sqlite").join("logging");
    
    // 3. Susun Path File Lengkap
    // Hasil: ROOT/lib/sqlite/logging/log.db
    let file_path = output_dir.join("log.db");

    // 4. Pastikan Direktori Tersedia (Pre-flight check)
    if !output_dir.exists() {
        // Kita tangkap error IO dan ubah menjadi PrintResult (via ? operator)
        fs::create_dir_all(&output_dir)?;
    }

    // 5. Buka Koneksi SQLite (Otomatis membuat file log.db jika belum ada)
    // ? operator di sini akan dilempar sebagai SqliteError ke PrintResult
    let conn = Connection::open(file_path)?;

    // Hapus otomatis database dalam rentang waktu 7 hari
    let retention_period_seconds = 7 * 24 * 60 * 60;
    
    // 6. Konfigurasi Mesin Database High-Performance
    conn.execute_batch(&format!(
        "PRAGMA journal_mode = WAL;
         PRAGMA synchronous = NORMAL;
         CREATE TABLE IF NOT EXISTS system_logs (
             id INTEGER PRIMARY KEY AUTOINCREMENT,
             timestamp REAL,
             level TEXT,
             label TEXT,
             payload TEXT,
             caller_info TEXT
         );
         DELETE FROM system_logs WHERE timestamp < (strftime('%s', 'now') - {});",
         retention_period_seconds
    ))?;
    
    Ok(conn)
}

pub fn insert_log(
    conn: &Connection, 
    timestamp: f64, 
    level: &str, 
    label: &str, 
    payload: &str, 
    caller_info: &str
) -> PrintResult<()> {
    conn.execute(
        "INSERT INTO system_logs (timestamp, level, label, payload, caller_info) VALUES (?1, ?2, ?3, ?4, ?5)",
        (timestamp, level, label, payload, caller_info),
    )?;
    Ok(())
}
