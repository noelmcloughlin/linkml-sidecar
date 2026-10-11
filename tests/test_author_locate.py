"""linkml-author finds the project through the preflight's `sidecar` and `project` lines, in each of the three layouts."""

from __future__ import annotations

import pytest

from conftest import PREFLIGHT, bash, make_host, matches, write


def project(host, where):
    write(host / where / ".copier-answers.yml", "_commit: v0.5.0\n_src_path: gh:linkml/linkml-project-copier\n")
    write(host / where / "config.public.mk", 'LINKML_SCHEMA_NAME="demo"\nLINKML_SCHEMA_SOURCE_DIR="src/demo/schema"\n')
    write(host / where / "src" / "demo" / "schema" / "demo.yaml", "id: x\n")


@pytest.mark.parametrize(
    ("where", "sidecar_line", "project_line"),
    [
        (".linkml", r"^ok      sidecar    \.linkml/ from", r"^ok      project    schema \.linkml/src/demo/schema/demo\.yaml"),
        ("linkml", r"^info    sidecar    a visible linkml/ sidecar", r"^ok      project    schema linkml/src/demo/schema/demo\.yaml"),
        (".", r"^info    sidecar    this repository is itself a copier project", r"^ok      project    schema src/demo/schema/demo\.yaml"),
    ],
)
def test_the_preflight_names_the_project_directory_and_schema(tmp_path, where, sidecar_line, project_line):
    host = make_host(tmp_path)
    project(host, where)
    result = bash(PREFLIGHT, host)
    assert result and matches(result.out, sidecar_line) and matches(result.out, project_line), result.out


def test_a_project_whose_schema_file_is_missing_is_reported(tmp_path):
    host = make_host(tmp_path)
    project(host, ".linkml")
    (host / ".linkml" / "src" / "demo" / "schema" / "demo.yaml").unlink()
    result = bash(PREFLIGHT, host)
    assert result and matches(result.out, r"^warn    project .*names src/demo/schema/demo\.yaml but it is not there"), result.out
