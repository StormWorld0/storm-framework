// File: src/telemetry.rs
use pyo3::prelude::*;
use std::time::{SystemTime, UNIX_EPOCH};
use crate::converters::object_to_string;
use crate::database::{get_db_connection, insert_log};
use crate::errors::PrintResult;

pub fn execute_telemetry(
    py: Python<'_>,
    level: &str,
    objects: &[Bound<'_, PyAny>],
) -> PrintResult<()> {
    
    // 1. LOGIKA PEMBELAHAN BLOK (Label vs Payload)
    let label_str = if objects.is_empty() {
        String::new() // Antisipasi jika user memanggil smf.printd() kosong
    } else {
        // Ekstrak argumen indeks [0] sebagai label
        object_to_string(&objects[0])?
    };

    let payload_str = if objects.len() > 1 {
        // Ambil dari indeks [1] sampai akhir array, lalu gabungkan
        let mut payloads = Vec::with_capacity(objects.len() - 1);
        for obj in &objects[1..] {
            payloads.push(object_to_string(obj)?);
        }
        payloads.join(" ")
    } else {
        String::new() // Kosongkan jika tidak ada data tambahan
    };

    // 2. Ekstrak Waktu
    let timestamp = SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .unwrap()
        .as_secs_f64();

    // 3. FFI Traceback Caller
    let caller_info = match py.import("sys").and_then(|sys| sys.getattr("_getframe")) {
        Ok(getframe) => {
            if let Ok(frame) = getframe.call1((1,)) {
                let filename = frame.getattr("f_code").and_then(|c| c.getattr("co_filename"));
                let lineno = frame.getattr("f_lineno");
                
                if let (Ok(f), Ok(l)) = (filename, lineno) {
                    let file_str = f.extract::<String>().unwrap_or_else(|_| "UnknownLocation".to_string());
                    format!("{}:{}", file_str, l.extract::<usize>().unwrap_or(0))
                } else {
                    "UnknownLocation".to_string()
                }
            } else {
                "UnknownFrame".to_string()
            }
        },
        Err(_) => "SysModuleError".to_string(),
    };

    // 2. Mengambil Traceback jika ada Exception aktif
    let traceback_info = match py.import("traceback").and_then(|tb| tb.getattr("format_exc")) {
        Ok(format_exc) => {
            if let Ok(tb_obj) = format_exc.call0() {
                let tb_str = tb_obj.extract::<String>().unwrap_or_default();
                // format_exc() mereturn "NoneType: None" jika tidak ada error aktif
                if !tb_str.trim().is_empty() && !tb_str.contains("NoneType: None") {
                    tb_str.trim().to_string()
                } else {
                    String::new()
                }
            } else {
                String::new()
            }
        },
        Err(_) => String::new(),
    };

    // 4. Inisialisasi Database
    let conn = get_db_connection(py)?;

    // 5. Injeksi ke Database Terstruktur
    // Masukkan label_str dan payload_str secara terpisah
    let _ = insert_log(&conn, timestamp, level, &label_str, &payload_str, &traceback_info, &caller_info);

    Ok(())
}
