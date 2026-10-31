// -- https://github.com/StormWorld0/storm-framework
// -- SMF License
use pyo3::prelude::*;
use pyo3::exceptions::{PyTypeError, PyValueError, PyOSError, PyRuntimeError}; 
use std::fmt;
use rusqlite;

#[derive(Debug)]
pub enum PrintError {
    TypeError(String),
    ValueError(String),
    IOError(std::io::Error),
    PythonError(PyErr),
    SqliteError(rusqlite::Error),
}

impl fmt::Display for PrintError {
    fn fmt(&self, f: &mut std::fmt::Formatter) -> std::fmt::Result {
        match self {
            PrintError::TypeError(msg) => write!(f, "Type Error: {}", msg),
            PrintError::ValueError(msg) => write!(f, "Value Error: {}", msg),
            PrintError::IOError(err) => write!(f, "I/O System Error: {}", err),
            PrintError::PythonError(err) => write!(f, "Python Internal Error: {}", err),
            PrintError::SqliteError(err) => write!(f, "SQLite DB Error: {}", err),
        }
    }
}

impl std::error::Error for PrintError {
    // Provides access to the root cause of the error if required by the debugger.
    fn source(&self) -> Option<&(dyn std::error::Error + 'static)> {
        match self {
            PrintError::IOError(err) => Some(err),
            _ => None,
        }
    }
}

// Conversion implementation of rusqlite::Error
impl From<rusqlite::Error> for PrintError {
    fn from(err: rusqlite::Error) -> Self {
        PrintError::SqliteError(err)
    }
}

// Automatic conversion implementation of std::io::Error
impl From<std::io::Error> for PrintError {
    fn from(err: std::io::Error) -> Self {
        PrintError::IOError(err)
    }
}

// Automatic conversion implementation of PyErr (for PyO3)
impl From<PyErr> for PrintError {
    fn from(err: PyErr) -> Self {
        PrintError::PythonError(err)
    }
}

// Crucial Part: Converting back to Python Exception
impl std::convert::From<PrintError> for PyErr {
    fn from(err: PrintError) -> PyErr {
        match err {
            PrintError::TypeError(msg) => PyTypeError::new_err(msg),
            PrintError::ValueError(msg) => PyValueError::new_err(msg),
            // Converts std::io::Error directly to an accurate PyOSError
            PrintError::IOError(err) => PyOSError::new_err(err.to_string()),
            PrintError::PythonError(err) => err,
            PrintError::SqliteError(err) => PyRuntimeError::new_err(format!("Internal SQLite Log Error: {}", err)),
        }
    }
}

pub type PrintResult<T> = Result<T, PrintError>;

