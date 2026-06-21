#[cfg(feature = "python")]
use std::ptr::NonNull;
#[cfg(feature = "python")]
use std::sync::Arc;

#[cfg(feature = "python")]
use arrow::array::{make_array, ArrayData, ArrayRef, Int64Array};
#[cfg(feature = "python")]
use arrow::buffer::Buffer;
#[cfg(feature = "python")]
use arrow::datatypes::{DataType, Field, Schema};
#[cfg(feature = "python")]
use arrow::record_batch::RecordBatch;
#[cfg(feature = "python")]
use pyo3::exceptions::PyValueError;
#[cfg(feature = "python")]
use pyo3::prelude::*;
#[cfg(feature = "wasm")]
use wasm_bindgen::prelude::*;

#[cfg(feature = "python")]
#[derive(Debug, PartialEq)]
struct ArrowRecordBatchSummary {
    rows: usize,
    columns: usize,
    column_name: String,
    sum: i64,
    values_buffer_ptr: usize,
}

#[cfg(feature = "python")]
#[derive(Debug)]
struct BorrowedArrowValuesBuffer;

pub fn add_usize(a: usize, b: usize) -> usize {
    a + b
}

#[derive(Debug, PartialEq, Eq)]
pub struct ArrowFlightContract {
    pub transport: &'static str,
    pub endpoint_uri: &'static str,
    pub stream_name: &'static str,
    pub schema_fields: [&'static str; 1],
    pub zero_copy_values_buffer: bool,
    pub live_transport_validated: bool,
    pub validation_scope: &'static str,
}

pub fn arrow_flight_contract() -> ArrowFlightContract {
    ArrowFlightContract {
        transport: "arrow_flight",
        endpoint_uri: "flight://rulespec-nz/local/record-batches",
        stream_name: "rulespec_nz_i64_record_batches",
        schema_fields: ["values:int64:not_null"],
        zero_copy_values_buffer: true,
        live_transport_validated: false,
        validation_scope: "repository_contract_only_until_live_arrow_flight_endpoint_exists",
    }
}

#[cfg_attr(feature = "wasm", wasm_bindgen)]
#[cfg(feature = "wasm")]
pub fn wasm_sum(a: usize, b: usize) -> usize {
    add_usize(a, b)
}

/// Formats the sum of two numbers as string.
#[cfg(feature = "python")]
#[pyfunction]
fn sum_as_string(a: usize, b: usize) -> PyResult<String> {
    Ok(add_usize(a, b).to_string())
}

#[cfg(feature = "python")]
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

#[cfg(feature = "python")]
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

#[cfg(all(test, feature = "python"))]
fn summarize_polars_i64_series_zero_copy(
    series: &polars::prelude::Series,
) -> Result<ArrowRecordBatchSummary, String> {
    let values = series
        .i64()
        .map_err(|error| error.to_string())?
        .cont_slice()
        .map_err(|error| error.to_string())?;
    let mut summary =
        unsafe { summarize_i64_record_batch_from_raw(values.as_ptr() as usize, values.len()) }?;
    summary.column_name = series.name().to_string();
    Ok(summary)
}

#[cfg(feature = "python")]
#[pyfunction]
fn arrow_i64_record_batch_summary(values: Vec<i64>) -> PyResult<String> {
    let values_ptr = values.as_ptr() as usize;
    let summary = unsafe { summarize_i64_record_batch_from_raw(values_ptr, values.len()) }
        .map_err(PyValueError::new_err)?;
    let zero_copy = values.is_empty() || summary.values_buffer_ptr == values_ptr;

    Ok(format!(
        "column={} rows={} sum={} zero_copy={}",
        summary.column_name, summary.rows, summary.sum, zero_copy
    ))
}

/// A Python module implemented in Rust. The name of this function must match
/// the `lib.name` in Cargo.toml.
#[cfg(feature = "python")]
#[pymodule]
fn rulespec_nz(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(sum_as_string, m)?)?;
    m.add_function(wrap_pyfunction!(arrow_i64_record_batch_summary, m)?)?;
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;
    #[cfg(feature = "python")]
    use polars::prelude::NamedFrom;

    #[test]
    fn add_usize_returns_sum() {
        assert_eq!(add_usize(40, 2), 42);
    }

    #[cfg(feature = "python")]
    #[test]
    fn sum_as_string_returns_decimal_sum() {
        assert_eq!(sum_as_string(40, 2).unwrap(), "42");
    }

    #[cfg(feature = "python")]
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

    #[cfg(feature = "python")]
    #[test]
    fn arrow_i64_record_batch_rejects_null_pointer_with_rows() {
        let error = unsafe { summarize_i64_record_batch_from_raw(0, 1) }.unwrap_err();

        assert!(error.contains("non-null"));
    }

    #[cfg(feature = "python")]
    #[test]
    fn py_arrow_i64_record_batch_summary_is_registered() {
        let summary = arrow_i64_record_batch_summary(vec![4_i64, 5, 6]).unwrap();

        assert_eq!(summary, "column=values rows=3 sum=15 zero_copy=true");
    }

    #[cfg(feature = "python")]
    #[test]
    fn polars_i64_series_reads_through_arrow_batch_without_copying_values() {
        let series = polars::prelude::Series::new("synthetic_income", &[100_i64, 250, 400]);
        let summary = summarize_polars_i64_series_zero_copy(&series).unwrap();
        let source_ptr = series.i64().unwrap().cont_slice().unwrap().as_ptr() as usize;

        assert_eq!(summary.rows, 3);
        assert_eq!(summary.column_name, "synthetic_income");
        assert_eq!(summary.sum, 750);
        assert_eq!(summary.values_buffer_ptr, source_ptr);
    }

    #[cfg(feature = "wasm")]
    #[test]
    fn wasm_sum_uses_core_addition() {
        assert_eq!(wasm_sum(20, 22), 42);
    }

    #[test]
    fn arrow_flight_contract_describes_repository_boundary() {
        let contract = arrow_flight_contract();

        assert_eq!(contract.transport, "arrow_flight");
        assert_eq!(
            contract.endpoint_uri,
            "flight://rulespec-nz/local/record-batches"
        );
        assert_eq!(contract.stream_name, "rulespec_nz_i64_record_batches");
        assert_eq!(contract.schema_fields, ["values:int64:not_null"]);
        assert!(contract.zero_copy_values_buffer);
        assert!(!contract.live_transport_validated);
        assert_eq!(
            contract.validation_scope,
            "repository_contract_only_until_live_arrow_flight_endpoint_exists"
        );
    }
}
