"""The scaffold, on throwaway hosts: what it lays down, what it refuses, and what it leaves alone.

The fast tests run it against tests/fake_copier.py, which renders the few
template files the scaffold touches, so no network is needed. The slow tests
(LINKML_SIDECAR_SLOW=1) run the real copier against a clone of the pinned
template and then the gate the skill's Step 4 names.
"""

from __future__ import annotations

import os
import re

import pytest

from conftest import FACTS, SCAFFOLD, TEMPLATES, Git, add_lokf, bash, have, make_host, matches, pin, read, run, scaffold, template_src, tokens_left, write

MARKER = "linkml-sidecar: the linkml_schema doorway"


def test_a_plain_host_gets_the_whole_layout(tmp_path):
    host = make_host(tmp_path)
    result = scaffold(host)
    assert result, result.out
    ref, _ = pin()
    side = host / ".linkml"
    answers = read(side / ".copier-answers.yml")
    assert f"_commit: {ref}" in answers and "add_example: false" in answers and "gh_action_pypi: false" in answers
    schema = read(side / "src" / "demo" / "schema" / "demo.yaml")
    assert "id: https://w3id.org/acme/demo\n" in schema and "name: demo\n" in schema and "  demo: https://w3id.org/acme/demo/\n" in schema
    assert "PersonStatus" in schema and "      alive:\n" in schema
    assert (side / "tests" / "data" / "valid" / "Person-001.yaml").is_file() and (side / "tests" / "data" / "invalid" / "Person-002.yaml").is_file()
    assert "import demo.datamodel.demo" in read(side / "tests" / "test_data.py")
    assert read(side / "LICENSE") == read(host / "LICENSE")
    readme = read(side / "README.md")
    assert readme.startswith("# `.linkml/`: demo's schema sidecar") and f"template {ref}" in readme
    assert os.access(side / "scripts" / "linkml-preflight.sh", os.X_OK)
    mkdocs = read(side / "mkdocs.yml")
    assert "site_url: https://acme.github.io/demo/linkml/\n" in mkdocs and "repo_url: https://github.com/acme/demo\n" in mkdocs
    assert read(side / "project.justfile").count(MARKER) == 1
    assert not (side / ".git").exists()
    assert not (side / ".linkmllint.yaml").exists()
    assert tokens_left(side) == []
    assert matches(result.out, r"^handoff: ") and matches(result.out, r"^next: just --justfile \.linkml/justfile install")


def test_the_root_pointers_are_added_once_and_left_alone_after(tmp_path):
    host = make_host(tmp_path)
    assert scaffold(host), "scaffold"
    readme = read(host / "README.md")
    assert readme.index("A demo host.") < readme.index("**The data model is a sidecar.**") < readme.index("## Usage")
    assert ".linkml/src/demo/schema/demo.yaml" in readme
    llms = read(host / "llms.txt")
    assert llms.startswith("# demo\n\n> A demo host.\n") and "## Schema" in llms and "lokf validate" not in llms
    assert os.readlink(host / "linkml_schema") == ".linkml/src/demo/schema"
    before = {p: read(p) for p in (host / "README.md", host / "llms.txt")}
    again = scaffold(host, "--pointers-only")
    assert again, again.out
    assert {p: read(p) for p in before} == before
    assert "already names .linkml/" in again.out and "already present" in again.out
    assert tokens_left(host / "llms.txt") == [] and tokens_left(host / "README.md") == []


def test_a_readme_without_a_section_gets_the_aside_at_the_end_and_no_readme_gets_none(tmp_path):
    host = make_host(tmp_path / "a")
    write(host / "README.md", "# Demo\n\nJust an intro.\n")
    assert scaffold(host)
    assert read(host / "README.md").rstrip().endswith("the code it describes.")
    bare = make_host(tmp_path / "b", readme=False)
    result = scaffold(bare)
    assert result and "no README.md at the root" in result.out and not (bare / "README.md").exists()


def test_a_host_without_a_license_gets_the_stub_and_a_handoff_line(tmp_path):
    host = make_host(tmp_path, license_file=False)
    result = scaffold(host, facts={**FACTS, "LICENSE_ID": "LicenseRef-Custom"})
    assert result, result.out
    assert "No license file was found at the root of the demo repository" in read(host / ".linkml" / "LICENSE")
    assert matches(result.out, r"^handoff: no LICENSE at the host root")


def test_gitignored_mode_adds_the_two_lines_once(tmp_path):
    host = make_host(tmp_path)
    write(host / ".gitignore", "node_modules/\n")
    assert scaffold(host, "--gitignored")
    assert scaffold(host, "--pointers-only", "--gitignored")
    ignore = read(host / ".gitignore")
    assert ignore.count(".linkml/\n") == 1 and ignore.count("linkml_schema\n") == 1 and ignore.startswith("node_modules/\n")


def test_dry_run_writes_nothing(tmp_path):
    host = make_host(tmp_path)
    before = sorted(str(p.relative_to(host)) for p in host.rglob("*") if ".git" not in p.parts)
    result = scaffold(host, "--dry-run")
    assert result, result.out
    after = sorted(str(p.relative_to(host)) for p in host.rglob("*") if ".git" not in p.parts)
    assert before == after
    assert "would run in" in result.out and 'answer project_name: "demo"' in result.out


@pytest.mark.parametrize(
    ("shape", "needle"),
    [("dot", ".linkml/ already exists"), ("visible", "visible linkml/ sidecar"), ("root", "itself a copier project")],
)
def test_an_existing_project_is_refused_and_nothing_is_written(tmp_path, shape, needle):
    host = make_host(tmp_path)
    if shape == "dot":
        write(host / ".linkml" / ".copier-answers.yml", "_commit: v0.5.0\n")
    elif shape == "visible":
        write(host / "linkml" / ".copier-answers.yml", "_commit: v0.5.0\n")
    else:
        write(host / ".copier-answers.yml", "_commit: v0.5.0\n")
    before = sorted(str(p) for p in host.rglob("*"))
    result = scaffold(host)
    assert result.rc == 3 and needle in result.out, result.out
    assert sorted(str(p) for p in host.rglob("*")) == before


def test_a_missing_fact_stops_before_anything_is_written(tmp_path):
    host = make_host(tmp_path)
    result = scaffold(host, facts={k: v for k, v in FACTS.items() if k != "SCHEMA_ID"})
    assert result.rc == 2 and "SCHEMA_ID is not set" in result.out
    assert not (host / ".linkml").exists()


def test_a_failed_copier_run_exits_4_and_a_nested_repository_exits_5(tmp_path):
    host = make_host(tmp_path / "a")
    result = scaffold(host, env={"FAKE_COPIER_FAIL": "1"})
    assert result.rc == 4 and "copier failed" in result.out, result.out
    host = make_host(tmp_path / "b")
    result = scaffold(host, env={"FAKE_COPIER_GIT": "1"})
    assert result.rc == 5 and ".linkml/.git appeared" in result.out, result.out


def test_a_ktl_host_gets_the_lokf_dummy_the_lint_config_and_the_wired_justfile(tmp_path):
    host = make_host(tmp_path)
    add_lokf(host)
    result = scaffold(host)
    assert result, result.out
    side = host / ".linkml"
    schema = read(side / "src" / "demo" / "schema" / "demo.yaml")
    assert "  - ../../../../.lokf/lokf\n" in schema and "ExampleConcept:\n    is_a: Concept" in schema
    valid = read(side / "tests" / "data" / "problem" / "valid" / "ExampleConcept-001.yaml")
    assert not (side / "tests" / "data" / "valid" / "ExampleConcept-001.yaml").exists()
    assert "id: https://fixture.example/knowledge/examples/example-concept\n" in valid and "type: ExampleConcept\n" in valid
    assert "SchemaView" in read(side / "tests" / "test_data.py")
    lint = read(side / ".linkmllint.yaml")
    assert "exclude: [isPartOf, hasPart, dependsOn]" in lint
    assert 'LINKML_GENERATORS_DOC_ARGS="--render-imports"' in read(side / "config.public.mk")
    justfile = read(host / ".lokf" / "justfile")
    assert 'schema := "../.linkml/src/demo/schema/demo.yaml"' in justfile
    assert justfile.count("--schema {{ file_name(schema) }}") == 2 and "cd {{ parent_directory(schema) }}" in justfile
    assert "--check-refs --schema" in justfile
    assert "lokf validate" in read(host / "llms.txt")
    assert matches(result.out, r"^handoff: \.lokf/justfile wired") and "BASE_IRI=https://fixture.example/knowledge/" in result.out
    assert tokens_left(side) == []


def test_mode_plain_overrides_a_ktl_host(tmp_path):
    host = make_host(tmp_path)
    add_lokf(host)
    assert scaffold(host, "--mode", "plain")
    assert "Person" in read(host / ".linkml" / "src" / "demo" / "schema" / "demo.yaml")
    assert "schema :=" not in read(host / ".lokf" / "justfile")


def test_a_ktl_justfile_that_differs_is_not_patched_but_told(tmp_path):
    host = make_host(tmp_path)
    add_lokf(host)
    write(host / ".lokf" / "justfile", 'bundle := "knowledge"\nlokf-validate:\n    uv run lokf validate --strict {{ bundle }}\n')
    result = scaffold(host)
    assert result, result.out
    assert "does not hold the ktl-sidecar template's lines" in result.out
    assert "schema :=" not in read(host / ".lokf" / "justfile")


def test_a_ktl_justfile_that_carries_the_variable_gets_only_that_line_set(tmp_path):
    host = make_host(tmp_path)
    add_lokf(host)
    write(host / ".lokf" / "justfile", 'bundle := "knowledge"\nschema := ""\nlokf-validate:\n    uv run lokf validate {{ schema_flag }} {{ bundle }}\n')
    result = scaffold(host)
    assert result, result.out
    justfile = read(host / ".lokf" / "justfile")
    assert 'schema := "../.linkml/src/demo/schema/demo.yaml"' in justfile and "parent_directory" not in justfile
    assert "the template's own recipes take it from there" in result.out


def test_repair_relays_one_owned_file_from_the_sidecars_own_facts(tmp_path):
    host = make_host(tmp_path)
    assert scaffold(host)
    readme = host / ".linkml" / "README.md"
    original = read(readme)
    write(readme, "broken\n")
    result = bash(SCAFFOLD, "--host", str(host), "--repair", ".linkml/README.md", env={"LINKML_TEMPLATE_SKIP_PIN_CHECK": "1"})
    assert result, result.out
    assert read(readme) == original
    bad = bash(SCAFFOLD, "--host", str(host), "--repair", "justfile", env={"LINKML_TEMPLATE_SKIP_PIN_CHECK": "1"})
    assert bad.rc == 2 and "not a file this skill owns" in bad.out


@pytest.mark.skipif(not have("just"), reason="just not installed locally")
def test_the_doorway_recipe_creates_refuses_and_is_a_no_op(tmp_path):
    host = make_host(tmp_path)
    assert scaffold(host)
    link = host / "linkml_schema"
    link.unlink()
    just = ["just", "--justfile", host / ".linkml" / "justfile", "linkml-link"]
    result = run(just, cwd=host)
    assert result and os.readlink(link) == ".linkml/src/demo/schema", result.out
    result = run(just, cwd=host)
    assert result and "already present" in result.out, result.out
    link.unlink()
    link.mkdir()
    result = run(just, cwd=host)
    assert result.rc == 1 and "not a link" in result.out, result.out


def test_every_template_token_is_one_the_scaffold_knows():
    """A template may carry only tokens the scaffold substitutes, so none can survive a run."""
    known = set(re.findall(r'"([A-Z_]+)",', (TEMPLATES.parent / "scripts" / "linkml-scaffold.py").read_text(encoding="utf-8").split("TOKENS = (")[1].split(")")[0]))
    found = set()
    for path in TEMPLATES.rglob("*"):
        if path.is_file():
            found |= set(re.findall(r"<([A-Z][A-Z_]+)>", read(path)))
    assert found <= known, found - known


# ---- the slow tests: the real copier, then the gate -------------------------


def slow_host(tmp_path, with_lokf):
    src = template_src()
    if src is None:
        pytest.skip("no template clone: set LINKML_TEMPLATE_SRC or clone the pinned tag into .template-cache/linkml-project-copier")
    for tool in ("uv", "just"):
        if not have(tool):
            pytest.skip(f"{tool} not installed")
    host = make_host(tmp_path)
    if with_lokf:
        add_lokf(host, stub_schema=False)
    facts = dict(FACTS)
    if with_lokf:
        facts["BASE_IRI"] = "https://fixture.example/knowledge/"
    result = scaffold(host, facts=facts, env={"LINKML_TEMPLATE_SRC": src}, fake=False)
    assert result, result.out
    return host


def gate(host, recipe):
    return run(["just", "--justfile", host / ".linkml" / "justfile", recipe], cwd=host)


@pytest.mark.slow
def test_the_real_template_passes_the_gate_on_a_plain_host(tmp_path):
    host = slow_host(tmp_path, with_lokf=False)
    ref, _ = pin()
    assert f"_commit: {ref}" in read(host / ".linkml" / ".copier-answers.yml")
    for recipe in ("install", "lint", "test", "site"):
        result = gate(host, recipe)
        assert result, f"just {recipe} failed:\n{result.out[-3000:]}"
    assert (host / ".linkml" / "uv.lock").is_file()
    # copier refuses a dirty destination, so the sidecar is committed first, as Step 4 says.
    git = Git(host)
    git("add", "-A")
    git("commit", "-q", "-m", "scaffolded")
    update = run(["uvx", "--from", "copier>=9.4.0,<10", "--with", "jinja2-time", "copier", "update", "--trust", "--skip-answered", "--quiet"], cwd=host / ".linkml")
    assert update, update.out[-2000:]
    assert git("status", "--porcelain") == "", "copier update at the same pin changed something"


@pytest.mark.slow
def test_the_real_template_passes_both_gates_on_a_ktl_host(tmp_path):
    host = slow_host(tmp_path, with_lokf=True)
    assert (host / ".lokf" / "lokf.yaml").is_file()
    for recipe in ("install", "lint", "test", "site"):
        result = gate(host, recipe)
        assert result, f"just {recipe} failed:\n{result.out[-3000:]}"
    for recipe in ("lokf-install", "lokf-validate", "lokf-check-refs"):
        result = run(["just", recipe], cwd=host / ".lokf")
        assert result, f"just {recipe} failed:\n{result.out[-3000:]}"
