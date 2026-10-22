// -- https://github.com/StormWorld0/storm-framework
// -- SMF License
use pyo3::prelude::*;
use crate::converters::object_to_string;
use crate::writer::OutputDestination;
use crate::errors::PrintResult;

pub fn core_print(
    _py: Python<'_>,
    objects: &[Bound<'_, PyAny>], // Slice contains Bound objects, not legacy GIL references
    sep: &str,
    end: &str,
    file: Option<&Bound<'_, PyAny>>, // Option that wraps a reference to a Bound object
    flush: bool,
) -> PrintResult<()> {
    // Initialize destination (Stdout or Python file object)
    // The 'file' parameter is now of type Option<&Bound<'_, PyAny>>
    let dest = OutputDestination::from_py_object(file, _py)?;
    
    // Optimization: Write directly to buffer (Streaming)
    for (idx, obj) in objects.iter().enumerate() {
        // Due to iteration on &[Bound<'_, PyAny>], the variable 'obj' here
        // automatically of type &Bound<'_, PyAny>.
        let s = object_to_string(obj)?;
        dest.write(&s)?;
        
        // Write separator if not the last element
        if idx < objects.len() - 1 {
            dest.write(sep)?;
        }
    }
    
    // Write the closing character (end)
    dest.write(end)?;
    
    // Flush if requested
    if flush {
        dest.flush()?;
    }
    
    Ok(())
}
