"""Generates one docs page per validator and a rules index at docs/rules/.

Run before `zensical build`:
    uv run python docs/gen_rules.py
"""

import inspect
import sys
from pathlib import Path

RULES_DIR = Path(__file__).parent / "rules"
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from rqa_validator.validators.data_validators import (  # noqa: E402
    CleaningLogToClean,
    ConsentCheck,
    CrossSheetIdCheck,
    CrossSheetRowSumCheck,
    DataTypeCheck,
    NaNDataCheck,
    PiiDataCheck,
    RawToCleanToLog,
    SurveyChoicesCheck,
    UniqueColumn,
)
from rqa_validator.validators.schema_validators import (  # noqa: E402
    ColumnNameCheck,
    DuplicateSheetMatches,
    MandatoryColumns,
    MissingSheetsCheck,
    UnexpectedSheetsCheck,
)

SCHEMA_VALIDATORS = [
    ColumnNameCheck,
    DuplicateSheetMatches,
    MandatoryColumns,
    MissingSheetsCheck,
    UnexpectedSheetsCheck,
]

DATA_VALIDATORS = [
    CleaningLogToClean,
    ConsentCheck,
    DataTypeCheck,
    CrossSheetIdCheck,
    CrossSheetRowSumCheck,
    NaNDataCheck,
    PiiDataCheck,
    RawToCleanToLog,
    SurveyChoicesCheck,
    UniqueColumn,
]


def _first_paragraph(docstring: str | None) -> str:
    if not docstring:
        return ""
    return docstring.strip().split("\n\n")[0].replace("\n", " ").strip()


def _write_rule_page(cls: type, category: str) -> None:
    doc = inspect.getdoc(cls) or ""
    module_path = f"{cls.__module__}.{cls.__name__}"
    page_path = RULES_DIR / f"{cls.__name__}.md"

    with open(page_path, "w") as f:
        f.write(f"# {cls.__name__}\n\n")
        f.write(f"**Category:** {category}\n\n")
        if doc:
            f.write(f"{doc}\n\n")
        f.write("## API Reference\n\n")
        f.write(f"::: {module_path}\n")
        f.write("    options:\n")
        f.write("      heading_level: 3\n")
        f.write("      show_source: false\n")
        f.write("      inherited_members: false\n")


def _write_index() -> None:
    total = len(SCHEMA_VALIDATORS) + len(DATA_VALIDATORS)
    with open(RULES_DIR / "index.md", "w") as f:
        f.write("# Rules\n\n")
        f.write(f"rqa-validator performs {total} checks across two categories.\n\n")

        f.write("## Schema Validation\n\n")
        f.write("Structural checks that run before data validation.\n\n")
        f.write("| Rule | Description |\n|------|-------------|\n")
        for cls in SCHEMA_VALIDATORS:
            desc = _first_paragraph(inspect.getdoc(cls))
            f.write(f"| [{cls.__name__}]({cls.__name__}.md) | {desc} |\n")
        f.write("\n")

        f.write("## Data Validation\n\n")
        f.write("Content checks that validate data integrity across sheets.\n\n")
        f.write("| Rule | Description |\n|------|-------------|\n")
        for cls in DATA_VALIDATORS:
            desc = _first_paragraph(inspect.getdoc(cls))
            f.write(f"| [{cls.__name__}]({cls.__name__}.md) | {desc} |\n")


if __name__ == "__main__":
    RULES_DIR.mkdir(exist_ok=True)
    for cls in SCHEMA_VALIDATORS:
        _write_rule_page(cls, "Schema Validation")
    for cls in DATA_VALIDATORS:
        _write_rule_page(cls, "Data Validation")
    _write_index()
    total = len(SCHEMA_VALIDATORS) + len(DATA_VALIDATORS)
    print(f"Generated {total} rule pages → {RULES_DIR}")
