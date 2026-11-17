// -- https://github.com/StormWorld0/storm-framework
// -- SMF License
use pyo3::prelude::*;
use std::io::{self, Write};
use crate::errors::{PrintError, PrintResult};

// Enums now store Bound pointer entities that are intrinsically 
// carries a lifetime GIL token ('py).
pub enum OutputDestination<'py> {
    Stdout,
    Stderr,
    File(Bound<'py, PyAny>),
}

impl<'py> OutputDestination<'py> {
    // Signature accepts a reference to a Bound object
    pub fn from_py_object(obj: Option<&Bound<'py, PyAny>>, _py: Python<'py>) -> PrintResult<Self> {
        match obj {
            None => Ok(OutputDestination::Stdout),
            Some(o) => {
                // Safe attribute checking in Bound context
                if o.hasattr("write")? {
                    // .clone() on Bound does not deep-copy Python data!
                    // It only executes the C-API `Py_INCREF` operation (O(1) complexity) 
                    // to safely duplicate pointers and store them in an Enum.
                    Ok(OutputDestination::File(o.clone()))
                } else {
                    Err(PrintError::TypeError("Object lacks write method".into()))
                }
            }
        }
    }

    pub fn write(&self, data: &str) -> PrintResult<()> {
        match self {
            OutputDestination::Stdout => {
                let stdout = io::stdout();
                let mut handle = stdout.lock(); // Efficiency: Manual lock
                handle.write_all(data.as_bytes())?;
            }
            OutputDestination::Stderr => {
                let stderr = io::stderr();
                let mut handle = stderr.lock();
                handle.write_all(data.as_bytes())?;
            }
            OutputDestination::File(obj) => {
                // Python::with_gil removal!
                // The Rust compiler knows that 'obj' (Bound) only exists if the GIL is valid.
                // call_method1 can now be called directly without additional FFI context switch.
                obj.call_method1("write", (data,))?;
            }
        }
        Ok(())
    }

    pub fn flush(&self) -> PrintResult<()> {
        match self {
            OutputDestination::Stdout => io::stdout().flush()?,
            OutputDestination::Stderr => io::stderr().flush()?,
            OutputDestination::File(obj) => {
                // Python::with_gil removal
                obj.call_method0("flush")?;
            }
        }
        Ok(())
    }
}
