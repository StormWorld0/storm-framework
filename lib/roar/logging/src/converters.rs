// -- https://github.com/StormWorld0/storm-framework
// -- SMF License
use pyo3::prelude::*;
use pyo3::types::{PyString, PyBytes};
use crate::errors::{PrintError, PrintResult};

// The parameter accepts a Bound object reference
pub fn object_to_string(obj: &Bound<'_, PyAny>) -> PrintResult<String> {
    // Fast-path: If the object is natively a PyString.
    // downcast() on Bound will return Result<&Bound<'_, PyString>, DowncastError>.
    if let Ok(s) = obj.cast::<PyString>() {
        return Ok(s.to_string_lossy().into_owned());
    }
    
    // Handling None (Singleton)
    // is_none() now operates safely on Bound smart pointers.
    if obj.is_none() {
        return Ok("None".to_string());
    }

    // Handling Bytes (Bypass encoding conversion, direct memory inspection)
    // as_bytes() borrows PyBytes' internal pointer directly to the Rust buffer.
    if let Ok(b) = obj.cast::<PyBytes>() {
        return Ok(format!("b'{}'", escape_bytes(b.as_bytes())));
    }
    
    // Standard Path: FFI call to the __str__ or __repr__ slot of a Python object.
    // The .str() and .repr() methods now allocate new strings on the Python side.
    // and returns it wrapped in a Bound<'_, PyString>.
    match obj.str() {
        Ok(s) => Ok(s.to_string_lossy().into_owned()),
        Err(_) => {
            // Fallback: Resolution to debugging representation.
            match obj.repr() {
                Ok(r) => Ok(r.to_string_lossy().into_owned()),
                Err(_) => {
                    // .get_type() returns Bound<'_, PyType>.
                    // .name() safely extracts the identifier without unnecessary allocation (returns Cow<str>).
                    Err(PrintError::TypeError(format!(
                        "Object of type {} is not string-convertible", 
                        obj.get_type().name()?
                    )))
                }
            }
        }
    }
}

// Pure-Rust operation, zero FFI PyO3 intervention.
fn escape_bytes(bytes: &[u8]) -> String {
    // Pre-allocate memory to reduce reallocation as strings grow.
    let mut result = String::with_capacity(bytes.len());
    for &b in bytes {
        match b {
            b'\n' => result.push_str("\\n"),
            b'\r' => result.push_str("\\r"),
            b'\t' => result.push_str("\\t"),
            b'\\' => result.push_str("\\\\"),
            b'\'' => result.push_str("\\'"),
            // ASCII Graphic: printable characters (32-126)
            0x20..=0x7E => result.push(b as char),
            _ => {
                // Hex format for non-ASCII characters
                result.push_str(&format!("\\x{:02x}", b));
            }
        }
    }
    result
}
