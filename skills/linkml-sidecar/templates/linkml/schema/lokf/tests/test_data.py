"""Data test for a schema that imports LOKF's core schema.

Every file under tests/data/valid and tests/data/problem/valid validates
against the class its name starts with, and every file under
tests/data/invalid fails to. The schema is loaded through SchemaView, which
resolves its relative import of .lokf/lokf.yaml from the schema file;
linkml.validator.validate() given a path resolved it from the working
directory instead before linkml 1.12.0 (PR 3855).

The generated dataclasses are not imported, and valid examples live under
problem/valid: LOKF has a slot named `from`, which linkml's Python generator
writes as a field name, so the dataclass module does not compile, and the
template's example runner (`just test`) instantiates every example under
data/valid through those same dataclasses. problem/valid is the folder the
runner skips. linkml 1.12.0 escapes the field as `from_` (PR 3317), but its
loaders still reject data that uses `from` (PR 4083 is open). Move the
examples to data/valid once a release loads it; the Pydantic models compile
meanwhile.
"""

import glob
import os
from pathlib import Path

import pytest
import yaml
from linkml.validator import validate
from linkml_runtime import SchemaView

HERE = Path(__file__).parent
SCHEMA = HERE.parent / "src" / "<PROJ_SLUG>" / "schema" / "<PROJ_SLUG>.yaml"
DATA_DIR_VALID = HERE / "data" / "valid"
DATA_DIR_PROBLEM_VALID = HERE / "data" / "problem" / "valid"
DATA_DIR_INVALID = HERE / "data" / "invalid"

VALID_EXAMPLE_FILES = sorted(
    glob.glob(os.path.join(DATA_DIR_VALID, "*.yaml")) + glob.glob(os.path.join(DATA_DIR_PROBLEM_VALID, "*.yaml"))
)
INVALID_EXAMPLE_FILES = sorted(glob.glob(os.path.join(DATA_DIR_INVALID, "*.yaml")))


@pytest.fixture(scope="module")
def schema():
    return SchemaView(str(SCHEMA)).schema


def target_class(filepath):
    return Path(filepath).stem.split("-")[0]


def load(filepath):
    with open(filepath, encoding="utf-8") as handle:
        return yaml.safe_load(handle)


@pytest.mark.parametrize("filepath", VALID_EXAMPLE_FILES)
def test_valid_data_files(schema, filepath):
    """Every valid example validates against its class."""
    report = validate(load(filepath), schema, target_class(filepath))
    assert not report.results, [result.message for result in report.results]


@pytest.mark.parametrize("filepath", INVALID_EXAMPLE_FILES)
def test_invalid_data_files(schema, filepath):
    """Every counter-example fails against its class."""
    report = validate(load(filepath), schema, target_class(filepath))
    assert report.results, f"{filepath} validated, and must not"
