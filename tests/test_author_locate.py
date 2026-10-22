"""linkml-author finds the schema through the preflight's `sidecar`, `project` and `schema` lines, in each layout it knows."""

from __future__ import annotations

import pytest

from conftest import PREFLIGHT, bash, make_host, matches, write

OURS = "_commit: v0.5.0\n_src_path: gh:linkml/linkml-project-copier\n"
SCHEMA = "id: https://w3id.org/acme/demo\nname: demo\nimports:\n  - linkml:types\nclasses:\n  Thing:\n"


def project(host, where, answers=True, config=True):
    if answers:
        write(host / where / ".copier-answers.yml", OURS + "project_slug: demo\n")
    if config:
        write(host / where / "config.public.mk", 'LINKML_SCHEMA_NAME="demo"\nLINKML_SCHEMA_SOURCE_DIR="src/demo/schema"\n')
    write(host / where / "src" / "demo" / "schema" / "demo.yaml", SCHEMA)


@pytest.mark.parametrize(
    ("where", "sidecar_line", "project_line"),
    [
        (".linkml", r"^ok      sidecar    \.linkml/ from", r"^ok      project    schema \.linkml/src/demo/schema/demo\.yaml"),
        ("linkml", r"^info    sidecar    linkml/ is a LinkML schema project", r"^ok      project    schema linkml/src/demo/schema/demo\.yaml"),
        ("model", r"^info    sidecar    model/ is a LinkML schema project", r"^ok      project    schema model/src/demo/schema/demo\.yaml"),
        (".", r"^info    sidecar    this repository is itself a LinkML schema project", r"^ok      project    schema src/demo/schema/demo\.yaml"),
    ],
)
def test_the_preflight_names_the_project_directory_and_schema(tmp_path, where, sidecar_line, project_line):
    host = make_host(tmp_path)
    project(host, where)
    result = bash(PREFLIGHT, host)
    assert result and matches(result.out, sidecar_line) and matches(result.out, project_line), result.out


@pytest.mark.parametrize(("answers", "config"), [(False, True), (True, False)])
def test_either_signal_alone_names_the_project(tmp_path, answers, config):
    """A cookiecutter project has config.public.mk and no copier answers; a future copier project may have answers and no config.public.mk."""
    host = make_host(tmp_path)
    project(host, ".", answers=answers, config=config)
    result = bash(PREFLIGHT, host)
    assert result and matches(result.out, r"^info    sidecar    this repository is itself a LinkML schema project") and matches(result.out, r"^ok      project    schema src/demo/schema/demo\.yaml"), result.out


def test_a_schema_outside_any_project_is_named_with_the_tools_that_run_on_it(tmp_path):
    host = make_host(tmp_path)
    write(host / "schemas" / "demo.yaml", SCHEMA)
    result = bash(PREFLIGHT, host)
    assert result and matches(result.out, r"^ok      schema     schemas/demo\.yaml$") and matches(result.out, r"^info    tools      uvx --from linkml"), result.out
    assert "linkml-author works on them in place" in result.out and not matches(result.out, r"^missing sidecar"), result.out


def test_a_project_whose_schema_file_is_missing_is_reported(tmp_path):
    host = make_host(tmp_path)
    project(host, ".linkml")
    (host / ".linkml" / "src" / "demo" / "schema" / "demo.yaml").unlink()
    result = bash(PREFLIGHT, host)
    assert result and matches(result.out, r"^warn    project .*names src/demo/schema/demo\.yaml but it is not there"), result.out
