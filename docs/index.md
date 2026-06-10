---
icon: lucide/rocket
---

# rqa-validator

Data quality validation for RQA datasets in Excel format. Runs 15 checks across schema structure and data content, returning structured JSON results.

## Installation

```bash
pip install rqa-validator
```

## Quick start

```python
from pathlib import Path
from rqa_validator.orchestrator.validation_pipeline import ValidationPipeline

pipeline = ValidationPipeline()
results = pipeline.run_all(
    filepath=Path("data/jmmi_dataset.xlsx"),
    dataset_type="jmmi",
    locale="en",
)

if results["success"]:
    print("Validation passed")
else:
    for error in results["error"]:
        print(f"[{error['rule']}] {error['message']}")
```

## Output structure

`run_all` returns a dict with results grouped by severity:

```python
{
    "success": bool,
    "summary": {
        "error": int,
        "warning": int,
        "info": int,
        "passed": int,
        "admin_error": int,
        "admin_info": int,
    },
    "error":       [...],  # blocking issues
    "warning":     [...],  # non-blocking issues
    "info":        [...],
    "passed":      [...],  # rules that passed
    "admin_error": [...],  # pipeline/config errors
    "admin_info":  [...],  # diagnostic details
    "metadata": {
        "dataset_type": str,
    },
}
```

Each result entry contains `rule`, `message`, `severity`, `sheet_name`, `column_name`, and `details`.

## JMMI validation flow

``` mermaid
flowchart TD
    A(["Excel file (.xlsx)"])

    subgraph SCHEMA["JMMIDatasetSchema"]
        direction LR
        LS["loaded: raw_data · clean_data · deletion_log<br>cleaning_log · survey · choices"]
        ULS["unloaded: read_me · sampling_info · variable_tracker<br>meb_analysis · mfs_analysis · enumerator_performance_log"]
    end

    A --> LOADER["ExcelLoader<br>fuzzy sheet & column name matching"]
    SCHEMA --> LOADER

    LOADER --> PRE{"schema<br>pre-validation"}
    PRE -- "duplicate names / schema error" --> OUT
    PRE -- pass --> DATA(["ExcelLoaderData<br>mapped sheets, columns & data"])

    DATA --> SV

    subgraph SV["Schema Validation — 5 checks"]
        direction TB
        SV1["MissingSheetsCheck · UnexpectedSheetsCheck<br>DuplicateSheetMatches · MandatoryColumns · UniqueColumn"]
    end

    SV --> DV

    subgraph DV["Data Validation — 11 checks"]
        direction TB
        DV1["PiiDataCheck"]
        DV2["CrossSheetRowSumCheck<br>raw_data rows = clean_data + deletion_log"]
        DV3["CrossSheetIdCheck ×2<br>raw_data ← {clean_data, deletion_log, cleaning_log}<br>clean_data ← {cleaning_log}"]
        DV4["CleaningLogToClean · RawToCleanToLog"]
        DV5["NaNDataCheck · ConsentCheck · ColumnNameCheck<br>DataTypeCheck · SurveyChoicesCheck"]
        DV1 --> DV2 --> DV3 --> DV4 --> DV5
    end

    DV --> OUT

    subgraph OUT["Output"]
        O["success: bool · summary: counts by severity<br>error · warning · info · passed · admin_error · admin_info"]
    end
```

## Dataset types

| Type | Schema | Validators |
|------|--------|------------|
| `jmmi` | Fully defined — sheets and columns are fixed | Full validator suite |
| any other | Dynamic — schema inferred from the file | Dynamic validator selection |

## Supported languages

Pass a `locale` string to `run_all` to get validation messages in a supported language. Translations live in `locales/`.

## Next steps

- [Rules](rules/index.md) — all 15 checks with descriptions and configuration options
- [API Reference](api.md) — full API documentation
