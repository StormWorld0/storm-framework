// -- https://github.com/StormWorld0/storm-framework
// -- SMF License
mod core;
mod writer;
mod converters;
mod errors;
mod database;
mod telemetry;

use pyo3::prelude::*;
use pyo3::types::{PyModule, PyTuple};

#[pyfunction]
#[pyo3(signature = (*args, sep=" ", end="\n", file=None, flush=false))]
fn printf(
    py: Python<'_>,
    args: &Bound<'_, PyTuple>,
    sep: &str,
    end: &str,
    file: Option<&Bound<'_, PyAny>>,
    flush: bool,
) -> PyResult<()> {
    
    // Convert tuple iterator to Vec<Bound> with O(1) allocation
    let objects: Vec<Bound<'_, PyAny>> = args.iter().collect();

    // Routing to sequential memory (Fast-path)
    // PrintResult is automatically converted to PyResult (PyErr) thanks to the From implementation in errors.rs
    core::core_print(py, &objects, sep, end, file, flush)?;
    
    Ok(())
}

#[pyfunction]
#[pyo3(signature = (*args, level="DEBUG"))] 
fn printd(
    py: Python<'_>,
    args: &Bound<'_, PyTuple>,
    level: &str,
) -> PyResult<()> {
    
    // Extract all user messages without truncation
    let objects: Vec<Bound<'_, PyAny>> = args.iter().collect();
    
    // Navigate to Telemetry Engine
    // Just like printf, internal errors (like SQLite error/IO error) 
    // will automatically throw to Python in case of fatal failure.
    telemetry::execute_telemetry(py, level, &objects)?;
    
    Ok(())
}

#[pymodule]
fn smf(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(printf, m)?)?;
    m.add_function(wrap_pyfunction!(printd, m)?)?;
    Ok(())
}
