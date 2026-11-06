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
    
    // BLOCK SPLITTING LOGIC (Label vs Payload)
    let label_str = if objects.is_empty() {
        String::new() // Anticipate if the developer calls smf.printd() empty
    } else {
        // Extract the index argument [0] as a label
        object_to_string(&objects[0])?
    };

    let payload_str = if objects.len() > 1 {
        // Take from index [1] to the end of the array, then merge
        let mut payloads = Vec::with_capacity(objects.len() - 1);
        for obj in &objects[1..] {
            payloads.push(object_to_string(obj)?);
        }
        payloads.join(" ")
    } else {
        String::new() // Leave blank if there is no additional data
    };

    // Time Extract
    let timestamp = SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .unwrap()
        .as_secs_f64();

    // FFI Traceback Caller
    let caller_info = match py.import("sys").and_then(|sys| sys.getattr("_getframe")) {
        Ok(getframe) => {
            if let Ok(frame) = getframe.call1((1,)) {
                if let Ok(f_code) = frame.getattr("f_code") {
                    let lineno = frame.getattr("f_lineno");
                    let filename = f_code.getattr("co_filename");
                    let funcname = f_code.getattr("co_name");
                
                    if let (Ok(f), Ok(func), Ok(l)) = (filename, funcname, lineno) {
                        let file_str = f.extract::<String>().unwrap_or_else(|_| "UnknownLocation".to_string());
                        let func_str = func.extract::<String>().unwrap_or_else(|_| "unknown_func".to_string());
                        let line_num = l.extract::<usize>().unwrap_or(0);
                        format!("{}:{} -> [function: {}]", file_str, line_num, func_str)
                    } else {
                        "UnknownLocation".to_string()
                    }
                } else {
                    "UnknownLocation".to_string()
                }
            } else {
                "UnknownFrame".to_string()
            }
        },
        Err(_) => "SysModuleError".to_string(),
    };

    // FFI Traceback Location
    let location_info = match py.import("sys").and_then(|sys| sys.getattr("_getframe")) {
        Ok(getframe) => {
            if let Ok(frame) = getframe.call1((0,)) {
                if let Ok(f_code) = frame.getattr("f_code") {
                    let lineno = frame.getattr("f_lineno");
                    let filename = f_code.getattr("co_filename");
                    let funcname = f_code.getattr("co_name");
                
                    if let (Ok(f), Ok(func), Ok(l)) = (filename, funcname, lineno) {
                        let file_str = f.extract::<String>().unwrap_or_else(|_| "UnknownLocation".to_string());
                        let func_str = func.extract::<String>().unwrap_or_else(|_| "unknown_func".to_string());
                        let line_num = l.extract::<usize>().unwrap_or(0);
                        format!("{}:{} -> [function: {}]", file_str, line_num, func_str)
                    } else {
                        "UnknownLocation".to_string()
                    }
                } else {
                    "UnknownLocation".to_string()
                }
            } else {
                "UnknownFrame".to_string()
            }
        },
        Err(_) => "SysModuleError".to_string(),
    };

    // Taking Traceback if there is an active Exception
    let traceback_info = match py.import("traceback").and_then(|tb| tb.getattr("format_exc")) {
        Ok(format_exc) => {
            if let Ok(tb_obj) = format_exc.call0() {
                let tb_str = tb_obj.extract::<String>().unwrap_or_default();
                // format_exc() returns "NoneType: None" if there are no active errors
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

    // Database Initialization
    let conn = get_db_connection(py)?;

    // Injection into Structured Database
    let _ = insert_log(&conn, timestamp, level, &label_str, &payload_str, &caller_info, &location_info, &traceback_info);

    Ok(())
}
