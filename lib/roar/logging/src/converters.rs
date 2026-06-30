// -- https://github.com/StormWorld0/storm-framework
// -- SMF License
use pyo3::prelude::*;
use pyo3::types::{PyString, PyBytes};
use crate::errors::{PrintError, PrintResult};

// 1. UBAH: Parameter menerima Bound object reference
pub fn object_to_string(obj: &Bound<'_, PyAny>) -> PrintResult<String> {
    // 1. Jalur Cepat (Fast-path): Jika objek secara native adalah PyString.
    // downcast() pada Bound akan mengembalikan Result<&Bound<'_, PyString>, DowncastError>.
    if let Ok(s) = obj.cast::<PyString>() {
        return Ok(s.to_string_lossy().into_owned());
    }
    
    // 2. Handling None (Singleton)
    // is_none() sekarang beroperasi secara aman di atas Bound smart pointer.
    if obj.is_none() {
        return Ok("None".to_string());
    }

    // 3. Handling Bytes (Bypass konversi encoding, inspeksi memori secara langsung)
    // as_bytes() meminjam pointer internal PyBytes langsung ke buffer C/Rust.
    if let Ok(b) = obj.cast::<PyBytes>() {
        return Ok(format!("b'{}'", escape_bytes(b.as_bytes())));
    }
    
    // 4. Jalur Standar: FFI call ke slot __str__ atau __repr__ objek Python.
    // Method .str() dan .repr() sekarang mengalokasikan string baru di sisi Python
    // dan mengembalikannya terbungkus dalam Bound<'_, PyString>.
    match obj.str() {
        Ok(s) => Ok(s.to_string_lossy().into_owned()),
        Err(_) => {
            // Fallback: Resolusi ke representasi debugging.
            match obj.repr() {
                Ok(r) => Ok(r.to_string_lossy().into_owned()),
                Err(_) => {
                    // .get_type() mereturn Bound<'_, PyType>.
                    // .name() secara aman mengekstrak identifier tanpa alokasi tak perlu (mengembalikan Cow<str>).
                    Err(PrintError::TypeError(format!(
                        "Object of type {} is not string-convertible", 
                        obj.get_type().name()?
                    )))
                }
            }
        }
    }
}

// FUNGSI INI TIDAK BERUBAH: Operasi pure-Rust, nol intervensi FFI PyO3.
fn escape_bytes(bytes: &[u8]) -> String {
    // Pre-allocate memori untuk mengurangi re-alokasi saat string tumbuh
    let mut result = String::with_capacity(bytes.len());
    for &b in bytes {
        match b {
            b'\n' => result.push_str("\\n"),
            b'\r' => result.push_str("\\r"),
            b'\t' => result.push_str("\\t"),
            b'\\' => result.push_str("\\\\"),
            b'\'' => result.push_str("\\'"),
            // ASCII Graphic: karakter yang bisa diprint (32-126)
            0x20..=0x7E => result.push(b as char),
            _ => {
                // Format hex untuk karakter non-ASCII
                result.push_str(&format!("\\x{:02x}", b));
            }
        }
    }
    result
}
