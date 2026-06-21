use std::ptr::NonNull;
use std::sync::Arc;

use arrow::array::{make_array, ArrayData, ArrayRef, Int64Array};
use arrow::buffer::Buffer;
use arrow::datatypes::{DataType, Field, Schema};
use arrow::record_batch::RecordBatch;
use pyo3::exceptions::PyValueError;
use pyo3::prelude::*;

#[derive(Debug, PartialEq)]
struct ArrowRecordBatchSummary {
    rows: usize,
    columns: usize,
    column_name: String,
    sum: i64,
    values_buffer_ptr: usize,
}

#[derive(Debug)]
struct BorrowedArrowValuesBuffer;

/// Formats the sum of two numbers as string.
#[pyfunction]
fn sum_as_string(a: usize, b: usize) -> PyResult<String> {
    Ok((a + b).to_string())
}

unsafe fn build_i64_record_batch_from_raw(
    values_ptr: usize,
    row_count: usize,
) -> Result<(RecordBatch, usize), String> {
    if row_count > 0 && values_ptr == 0 {
        return Err(
            "values pointer must be non-null when row_count is greater than zero".to_string(),
        );
    }

    let schema = Arc::new(Schema::new(vec![Field::new(
        "values",
        DataType::Int64,
        false,
    )]));

    if row_count == 0 {
        let array: ArrayRef = Arc::new(Int64Array::from(Vec::<i64>::new()));
        let batch = RecordBatch::try_new(schema, vec![array]).map_err(|error| error.to_string())?;
        return Ok((batch, 0));
    }

    if !values_ptr.is_multiple_of(std::mem::align_of::<i64>()) {
        return Err("values pointer must be aligned for i64 Arrow values".to_string());
    }

    let byte_len = row_count
        .checked_mul(std::mem::size_of::<i64>())
        .ok_or_else(|| "row_count overflows Arrow values buffer length".to_string())?;
    let values_buffer = Buffer::from_custom_allocation(
        NonNull::new(values_ptr as *mut u8)
            .ok_or_else(|| "values pointer must be non-null".to_string())?,
        byte_len,
        Arc::new(BorrowedArrowValuesBuffer),
    );
    let data = ArrayData::try_new(
        DataType::Int64,
        row_count,
        None,
        0,
        vec![values_buffer],
        vec![],
    )
    .map_err(|error| error.to_string())?;
    let array = make_array(data);
    let batch = RecordBatch::try_new(schema, vec![array]).map_err(|error| error.to_string())?;

    Ok((batch, values_ptr))
}

unsafe fn summarize_i64_record_batch_from_raw(
    values_ptr: usize,
    row_count: usize,
) -> Result<ArrowRecordBatchSummary, String> {
    let (batch, values_buffer_ptr) = build_i64_record_batch_from_raw(values_ptr, row_count)?;
    let column = batch
        .column_by_name("values")
        .ok_or_else(|| "values column missing from Arrow record batch".to_string())?;
    let values = column
        .as_any()
        .downcast_ref::<Int64Array>()
        .ok_or_else(|| "values column is not an Int64 Arrow array".to_string())?;

    let sum = values.values().iter().copied().sum();

    Ok(ArrowRecordBatchSummary {
        rows: batch.num_rows(),
        columns: batch.num_columns(),
        column_name: batch.schema().field(0).name().clone(),
        sum,
        values_buffer_ptr,
    })
}

#[pyfunction]
fn arrow_i64_record_batch_summary(values_ptr: usize, row_count: usize) -> PyResult<String> {
    let summary = unsafe { summarize_i64_record_batch_from_raw(values_ptr, row_count) }
        .map_err(PyValueError::new_err)?;
    let zero_copy = row_count == 0 || summary.values_buffer_ptr == values_ptr;

    Ok(format!(
        "column={} rows={} sum={} zero_copy={}",
        summary.column_name, summary.rows, summary.sum, zero_copy
    ))
}

/// A Python module implemented in Rust. The name of this function must match
/// the `lib.name` in Cargo.toml.
#[pymodule]
fn rulespec_nz(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(sum_as_string, m)?)?;
    m.add_function(wrap_pyfunction!(arrow_i64_record_batch_summary, m)?)?;
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn sum_as_string_returns_decimal_sum() {
        assert_eq!(sum_as_string(40, 2).unwrap(), "42");
    }

    #[test]
    fn arrow_i64_record_batch_uses_source_values_buffer() {
        let values = vec![10_i64, 20, 30];
        let summary = unsafe {
            summarize_i64_record_batch_from_raw(values.as_ptr() as usize, values.len()).unwrap()
        };

        assert_eq!(summary.rows, 3);
        assert_eq!(summary.columns, 1);
        assert_eq!(summary.column_name, "values");
        assert_eq!(summary.sum, 60);
        assert_eq!(summary.values_buffer_ptr, values.as_ptr() as usize);
    }

    #[test]
    fn arrow_i64_record_batch_rejects_null_pointer_with_rows() {
        let error = unsafe { summarize_i64_record_batch_from_raw(0, 1) }.unwrap_err();

        assert!(error.contains("non-null"));
    }

    #[test]
    fn py_arrow_i64_record_batch_summary_is_registered() {
        let values = vec![4_i64, 5, 6];
        let summary =
            arrow_i64_record_batch_summary(values.as_ptr() as usize, values.len()).unwrap();

        assert_eq!(summary, "column=values rows=3 sum=15 zero_copy=true");
    }
}
