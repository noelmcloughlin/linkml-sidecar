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
OURS = "_commit: v0.5.0\n_src_path: gh:linkml/linkml-project-copier\n"
SCHEMA = "id: https://w3id.org/acme/demo\nname: demo\nprefixes:\n  linkml: https://w3id.org/linkml/\nimports:\n  - linkml:types\nclasses:\n  Thing:\n    attributes:\n      name:\n"


def staging_left(host):
    return sorted(p.name for p in host.glob(".linkml-staging-*"))


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
    ("path", "content", "needle"),
    [
        (".linkml/.copier-answers.yml", "_commit: v0.5.0\n", ".linkml/ already holds a sidecar"),
        ("linkml/.copier-answers.yml", OURS, "linkml/ is a LinkML schema project already (copier answers)"),
        (".copier-answers.yml", OURS, "this repository is itself a LinkML schema project already (copier answers)"),
        ("config.public.mk", 'LINKML_SCHEMA_NAME="demo"\n', "this repository is itself a LinkML schema project already (config.public.mk)"),
        ("model/config.public.mk", 'LINKML_SCHEMA_NAME="demo"\n', "model/ is a LinkML schema project already (config.public.mk)"),
        (".linkml/justfile", "lint:\n", ".linkml/ holds justfile but no .copier-answers.yml"),
    ],
)
def test_an_existing_project_is_refused_and_nothing_is_written(tmp_path, path, content, needle):
    host = make_host(tmp_path)
    write(host / path, content)
    before = sorted(str(p) for p in host.rglob("*"))
    result = scaffold(host)
    assert result.rc == 3 and needle in result.out, result.out
    assert sorted(str(p) for p in host.rglob("*")) == before


def test_answers_of_another_template_at_the_root_are_no_project(tmp_path):
    host = make_host(tmp_path)
    write(host / ".copier-answers.yml", "_commit: v1.0.0\n_src_path: gh:acme/python-service-template\n")
    result = scaffold(host)
    assert result and (host / ".linkml" / ".copier-answers.yml").is_file(), result.out


def test_configuration_files_in_dot_linkml_are_installed_around(tmp_path):
    host = make_host(tmp_path)
    write(host / ".linkml" / "upstream.toml", "[linkml]\nkept = true\n")
    failed = scaffold(host, env={"FAKE_COPIER_FAIL": "1"})
    assert failed.rc == 4 and "removed the staging directory; .linkml/ was not touched" in failed.out, failed.out
    assert sorted(p.name for p in (host / ".linkml").iterdir()) == ["upstream.toml"] and staging_left(host) == []
    result = scaffold(host)
    assert result, result.out
    assert "holds 1 file(s) and no project (upstream.toml)" in result.out and "moved the sidecar into .linkml/ around the files already there" in result.out
    assert read(host / ".linkml" / "upstream.toml") == "[linkml]\nkept = true\n"
    assert (host / ".linkml" / ".copier-answers.yml").is_file() and (host / ".linkml" / "src" / "demo" / "schema" / "demo.yaml").is_file()
    assert staging_left(host) == [] and tokens_left(host / ".linkml") == []


def test_a_file_both_hold_is_a_clash_and_nothing_is_written(tmp_path):
    host = make_host(tmp_path)
    write(host / ".linkml" / "README.md", "the host's own notes\n")
    result = scaffold(host)
    assert result.rc == 3 and "already holds 1 of the files the sidecar writes (README.md)" in result.out, result.out
    assert sorted(p.name for p in (host / ".linkml").iterdir()) == ["README.md"] and read(host / ".linkml" / "README.md") == "the host's own notes\n"
    assert staging_left(host) == [] and "rm -rf" not in result.out


def test_gitignored_mode_is_refused_when_dot_linkml_holds_tracked_files(tmp_path):
    host = make_host(tmp_path)
    write(host / ".linkml" / "upstream.toml", "[linkml]\n")
    git = Git(host)
    git("add", "-A")
    git("commit", "-q", "-m", "config")
    result = scaffold(host, "--gitignored")
    assert result.rc == 2 and "holds files git tracks (.linkml/upstream.toml)" in result.out, result.out
    assert not (host / ".linkml" / ".copier-answers.yml").exists() and staging_left(host) == []


def test_a_missing_fact_stops_before_anything_is_written(tmp_path):
    host = make_host(tmp_path)
    result = scaffold(host, facts={k: v for k, v in FACTS.items() if k != "SCHEMA_ID"})
    assert result.rc == 2 and "SCHEMA_ID is not set" in result.out
    assert not (host / ".linkml").exists()


def test_a_failed_copier_run_exits_4_and_a_nested_repository_exits_5(tmp_path):
    host = make_host(tmp_path / "a")
    result = scaffold(host, env={"FAKE_COPIER_FAIL": "1"})
    assert result.rc == 4 and "copier failed" in result.out, result.out
    # Everything was staged, so the failure leaves no .linkml/ and no staging directory, and the next run is not refused.
    assert not (host / ".linkml").exists() and staging_left(host) == [] and "removed the staging directory" in result.out
    assert scaffold(host), "a second run after the failure"
    host = make_host(tmp_path / "b")
    result = scaffold(host, env={"FAKE_COPIER_GIT": "1"})
    assert result.rc == 5 and ".linkml/.git appeared" in result.out, result.out
    assert not (host / ".linkml").exists() and staging_left(host) == []


# ---- a schema the host already holds ----------------------------------------


def test_a_schema_the_host_holds_is_refused_until_adopted_or_the_dummy_is_asked_for(tmp_path):
    host = make_host(tmp_path)
    write(host / "schema" / "demo.yaml", SCHEMA)
    result = scaffold(host)
    assert result.rc == 3 and "already holds a LinkML schema: schema/demo.yaml" in result.out and "--adopt <path>" in result.out, result.out
    assert not (host / ".linkml").exists() and staging_left(host) == []
    result = scaffold(host, "--dummy")
    assert result and "Person" in read(host / ".linkml" / "src" / "demo" / "schema" / "demo.yaml"), result.out


def test_an_adopted_schema_stays_where_it_is_and_the_sidecar_points_at_it(tmp_path):
    host = make_host(tmp_path)
    write(host / "schema" / "demo.yaml", SCHEMA)
    write(host / "schema" / "demo_terms.yaml", "id: https://w3id.org/acme/demo/terms\nname: demo_terms\nimports:\n  - linkml:types\n")
    before = {p: read(p) for p in (host / "README.md", host / "schema" / "demo.yaml")}
    facts = {k: v for k, v in FACTS.items() if k not in ("PROJ_SLUG", "SCHEMA_ID")}
    result = scaffold(host, "--adopt", "schema/demo.yaml", facts=facts)
    assert result, result.out
    side = host / ".linkml"
    assert 'LINKML_SCHEMA_SOURCE_DIR="../schema"' in read(side / "config.public.mk") and 'LINKML_SCHEMA_NAME="demo"' in read(side / "config.public.mk")
    assert not (side / "src" / "demo" / "schema" / "demo.yaml").exists()
    assert "schema/demo.yaml" in read(side / "src" / "demo" / "schema" / "README.md")
    assert not (side / "tests" / "data" / "valid" / "Person-001.yaml").exists() and "import demo.datamodel.demo" in read(side / "tests" / "test_data.py")
    readme = read(side / "README.md")
    assert "## Where the schema is" in readme and "`schema/demo.yaml`" in readme and "src/demo/schema/README.md" in readme and "the one file to edit" not in readme
    assert MARKER not in read(side / "project.justfile") and not (host / "linkml_schema").exists() and not (host / "llms.txt").exists()
    assert {p: read(p) for p in before} == before
    assert matches(result.out, r"^handoff: SCHEMA_ID=https://w3id\.org/acme/demo$") and matches(result.out, r"^handoff: adopted schema/demo\.yaml: config\.public\.mk names its folder \(LINKML_SCHEMA_SOURCE_DIR=\.\./schema\)")
    assert matches(result.out, r"^handoff: no example data was laid down") and matches(result.out, r"^handoff: no README aside, llms\.txt section or linkml_schema doorway")
    assert matches(result.out, r'^handoff: Step 5\'s workflow runs on \.linkml/\*\* only; add "schema/\*\*"')
    assert tokens_left(side) == [] and staging_left(host) == []
    again = scaffold(host, "--pointers-only")
    assert again and not (host / "linkml_schema").exists() and not (host / "llms.txt").exists(), again.out
    repaired = bash(SCAFFOLD, "--host", str(host), "--repair", ".linkml/src/demo/schema/README.md", env={"LINKML_TEMPLATE_SKIP_PIN_CHECK": "1"})
    assert repaired and "schema/demo.yaml" in read(side / "src" / "demo" / "schema" / "README.md"), repaired.out


def test_a_schema_at_the_root_is_adopted_from_one_level_up(tmp_path):
    host = make_host(tmp_path)
    write(host / "demo.yaml", SCHEMA)
    result = scaffold(host, "--adopt", "demo.yaml", facts={k: v for k, v in FACTS.items() if k != "PROJ_SLUG"})
    assert result, result.out
    assert 'LINKML_SCHEMA_SOURCE_DIR=".."' in read(host / ".linkml" / "config.public.mk")
    assert "`./demo.yaml`" in read(host / ".linkml" / "src" / "demo" / "schema" / "README.md")


@pytest.mark.parametrize(
    ("path", "content", "args", "facts", "needle"),
    [
        ("schema/demo.yml", SCHEMA, (), {}, "must be renamed first"),
        ("schema/my-model.yaml", SCHEMA, (), {}, "is not a slug"),
        ("schema/demo.yaml", SCHEMA, (), {"PROJ_SLUG": "other"}, "PROJ_SLUG='other', but the adopted schema file is demo.yaml"),
        ("schema/demo.yaml", "name: demo\nclasses: {}\n", (), {}, "does not read as a LinkML schema"),
        ("schema/demo.yaml", SCHEMA, ("--mode", "lokf"), {}, "--adopt and --mode lokf do not go together"),
        (".linkml/demo.yaml", SCHEMA, (), {}, "is inside .linkml/"),
    ],
)
def test_adoption_checks_the_file_before_anything_is_written(tmp_path, path, content, args, facts, needle):
    host = make_host(tmp_path)
    write(host / path, content)
    before = sorted(str(p) for p in host.rglob("*"))
    result = scaffold(host, "--adopt", path, *args, facts={**{k: v for k, v in FACTS.items() if k != "PROJ_SLUG"}, **facts})
    assert result.rc == 2 and needle in result.out, result.out
    assert sorted(str(p) for p in host.rglob("*")) == before


def test_an_adopted_schema_beside_a_bundle_is_left_unwired(tmp_path):
    host = make_host(tmp_path)
    add_lokf(host)
    write(host / "schema" / "demo.yaml", SCHEMA)
    original = read(host / ".lokf" / "justfile")
    result = scaffold(host, "--adopt", "schema/demo.yaml", facts={k: v for k, v in FACTS.items() if k != "PROJ_SLUG"})
    assert result, result.out
    assert "plain mode" in result.out and matches(result.out, r"^handoff: \.lokf/ is present and not wired")
    assert read(host / ".lokf" / "justfile") == original and not (host / ".linkml" / ".linkmllint.yaml").exists()



WORKFLOWS_HANDOFF = (
    r"^handoff: make the validate step of knowledge-registrar\.yaml, knowledge-librarian\.yaml and knowledge-release\.yaml "
    r"run `uvx --from rust-just==1\.47\.0 just lokf-check-refs`"
)


def test_a_ktl_host_gets_the_lokf_dummy_the_lint_config_and_the_wired_justfile(tmp_path):
    host = make_host(tmp_path)
    add_lokf(host, before_schema=True)
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
    # The template's workflows still validate inline, so all three are named, with the line the runners can run.
    assert matches(result.out, WORKFLOWS_HANDOFF), result.out
    assert tokens_left(side) == []


def test_mode_plain_overrides_a_ktl_host(tmp_path):
    host = make_host(tmp_path)
    add_lokf(host)
    original = read(host / ".lokf" / "justfile")
    assert scaffold(host, "--mode", "plain")
    assert "Person" in read(host / ".linkml" / "src" / "demo" / "schema" / "demo.yaml")
    assert read(host / ".lokf" / "justfile") == original


def test_a_ktl_justfile_that_differs_is_not_patched_but_told(tmp_path):
    host = make_host(tmp_path)
    add_lokf(host)
    write(host / ".lokf" / "justfile", 'bundle := "knowledge"\nlokf-validate:\n    uv run lokf validate --strict {{ bundle }}\n')
    result = scaffold(host)
    assert result, result.out
    assert "does not hold the ktl-sidecar template's lines" in result.out
    assert matches(result.out, WORKFLOWS_HANDOFF), result.out
    assert "schema :=" not in read(host / ".lokf" / "justfile")


def test_a_ktl_justfile_that_carries_the_variable_gets_only_that_line_set(tmp_path):
    host = make_host(tmp_path)
    add_lokf(host)
    original = read(host / ".lokf" / "justfile")
    result = scaffold(host)
    assert result, result.out
    justfile = read(host / ".lokf" / "justfile")
    # Exactly one line changes, the variable; the template's recipes are left as they are.
    assert justfile.replace('schema := "../.linkml/src/demo/schema/demo.yaml"', 'schema := ""') == original
    assert "the template's own recipes take it from there" in result.out
    # That template's workflows run the recipe already, so they need no telling.
    assert not matches(result.out, WORKFLOWS_HANDOFF), result.out


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



@pytest.mark.parametrize(
    ("fact", "value", "needle"),
    [
        ("SCHEMA_ID", "https://w3id.org/acme/demo/", "SCHEMA_ID must not end with /"),
        ("PROJ_SLUG", "d", "PROJ_SLUG 'd' must be"),
        ("SCHEMA_ID", "https://acme.github.io/demo/linkml/", "names a code host"),
    ],
)
def test_a_fact_the_template_would_reject_stops_before_anything_is_written(tmp_path, fact, value, needle):
    host = make_host(tmp_path)
    result = scaffold(host, facts={**FACTS, fact: value})
    assert result.rc == 2 and needle in result.out, result.out
    assert not (host / ".linkml").exists()


def test_no_license_file_requires_the_custom_license_id(tmp_path):
    host = make_host(tmp_path, license_file=False)
    result = scaffold(host)
    assert result.rc == 2 and "LICENSE_ID must be LicenseRef-Custom" in result.out, result.out
    assert not (host / ".linkml").exists()


def test_a_backslash_in_a_url_is_written_as_text(tmp_path):
    host = make_host(tmp_path)
    result = scaffold(host, facts={**FACTS, "DOCS_URL": "https://acme.example/docs\\1/"})
    assert result, result.out
    assert "site_url: https://acme.example/docs\\1/\n" in read(host / ".linkml" / "mkdocs.yml")


def test_the_aside_skips_fenced_code_and_leads_a_readme_that_opens_with_a_section(tmp_path):
    host = make_host(tmp_path / "a")
    write(host / "README.md", "# Demo\n\nIntro.\n\n```md\n## not a heading\n```\n\n## Usage\n")
    assert scaffold(host)
    readme = read(host / "README.md")
    assert readme.index("## not a heading") < readme.index("**The data model is a sidecar.**") < readme.index("## Usage")
    host = make_host(tmp_path / "b")
    write(host / "README.md", "## Usage\n\nRun it.\n")
    assert scaffold(host)
    readme = read(host / "README.md")
    assert readme.startswith("> ") or readme.startswith("**"), readme[:80]
    assert readme.index("**The data model is a sidecar.**") < readme.index("## Usage")


def test_an_anchored_gitignore_line_is_not_added_twice(tmp_path):
    host = make_host(tmp_path)
    write(host / ".gitignore", "/.linkml/\n/linkml_schema\n")
    result = scaffold(host, "--gitignored")
    assert result and "already names the sidecar and the doorway" in result.out, result.out
    assert read(host / ".gitignore") == "/.linkml/\n/linkml_schema\n"


def test_the_doorway_recipe_names_the_slug(tmp_path):
    host = make_host(tmp_path)
    assert scaffold(host)
    block = read(host / ".linkml" / "project.justfile")
    assert "mklink /J linkml_schema .linkml\\src\\demo\\schema" in block and "<PROJ_SLUG>" not in block


def test_dry_run_prints_the_same_handoff_lines(tmp_path):
    host = make_host(tmp_path)
    result = scaffold(host, "--dry-run")
    assert result and matches(result.out, r"^handoff: the inert file") and matches(result.out, r"^handoff: CODE_OF_CONDUCT\.md"), result.out


def test_dry_run_on_a_ktl_host_without_a_toolkit_fails_as_the_real_run_would(tmp_path):
    host = make_host(tmp_path)
    add_lokf(host)
    (host / ".lokf" / "lokf.yaml").unlink()
    (host / ".lokf" / "pyproject.toml").unlink()
    result = scaffold(host, "--dry-run")
    assert result.rc == 2 and "has no pyproject.toml" in result.out, result.out


def test_repair_relays_the_lint_config_and_the_doorway_recipe(tmp_path):
    host = make_host(tmp_path)
    add_lokf(host)
    assert scaffold(host)
    env = {"LINKML_TEMPLATE_SKIP_PIN_CHECK": "1"}
    lint = host / ".linkml" / ".linkmllint.yaml"
    original = read(lint)
    lint.unlink()
    result = bash(SCAFFOLD, "--host", str(host), "--repair", ".linkml/.linkmllint.yaml", env=env)
    assert result and read(lint) == original, result.out
    justfile = host / ".linkml" / "project.justfile"
    with_block = read(justfile)
    write(justfile, with_block[: with_block.index("# ---- linkml-sidecar")])
    result = bash(SCAFFOLD, "--host", str(host), "--repair", str(justfile), env=env)
    assert result and read(justfile).count(MARKER) == 1, result.out
    again = bash(SCAFFOLD, "--host", str(host), "--repair", "project.justfile", env=env)
    assert again and read(justfile).count(MARKER) == 1 and "already carries the doorway recipe" in again.out


def test_repair_refuses_the_lint_config_on_a_plain_host(tmp_path):
    host = make_host(tmp_path)
    assert scaffold(host)
    result = bash(SCAFFOLD, "--host", str(host), "--repair", ".linkmllint.yaml", env={"LINKML_TEMPLATE_SKIP_PIN_CHECK": "1"})
    assert result.rc == 2 and "KTL mode only" in result.out, result.out


def test_pointers_only_refuses_a_sidecar_that_records_no_slug(tmp_path):
    host = make_host(tmp_path)
    assert scaffold(host)
    side = host / ".linkml"
    answers = read(side / ".copier-answers.yml")
    write(side / ".copier-answers.yml", re.sub(r"(?m)^project_slug:.*$", "project_slug: ''", answers))
    write(side / "config.public.mk", re.sub(r'(?m)^LINKML_SCHEMA_NAME=.*$', 'LINKML_SCHEMA_NAME=""', read(side / "config.public.mk")))
    (host / "linkml_schema").unlink()
    result = bash(SCAFFOLD, "--host", str(host), "--pointers-only", env={"LINKML_TEMPLATE_SKIP_PIN_CHECK": "1"})
    assert result.rc == 2 and "records no project_slug" in result.out, result.out
    assert not (host / "linkml_schema").is_symlink()


def test_the_scaffold_runs_on_python_3_8_syntax_and_library():
    """Path.write_text(newline=) is 3.10; the scaffold promises 3.8."""
    assert "write_text(" not in read(SCAFFOLD.with_suffix(".py")).split("def write(", 1)[1].split("\ndef ", 1)[0]


# ---- the slow tests: the real copier, then the gate -------------------------


def slow_host(tmp_path, with_lokf, adopt=None):
    # LINKML_SIDECAR_SLOW=1 asks for these tests, so a missing clone or tool
    # fails them: a skip would let a broken clone step in CI pass green.
    src = template_src()
    if src is None:
        pytest.fail("no template clone: set LINKML_TEMPLATE_SRC or clone the pinned tag into .template-cache/linkml-project-copier")
    for tool in ("uv", "just"):
        if not have(tool):
            pytest.fail(f"{tool} not installed")
    host = make_host(tmp_path)
    if with_lokf:
        add_lokf(host, stub_schema=False)
    facts = dict(FACTS)
    if with_lokf:
        facts["BASE_IRI"] = "https://fixture.example/knowledge/"
    args = ("--adopt", adopt) if adopt else ()
    result = scaffold(host, *args, facts=facts, env={"LINKML_TEMPLATE_SRC": src}, fake=False)
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
def test_the_real_template_passes_the_gate_on_an_adopted_schema(tmp_path):
    """The dummy schema, placed in the host before the sidecar exists, adopted where it lies: every recipe reads it through config.public.mk."""
    rendered = read(TEMPLATES / "linkml" / "schema" / "plain" / "schema.yaml")
    for token, value in {**FACTS, "TEMPLATE_REF": pin()[0]}.items():
        rendered = rendered.replace(f"<{token}>", value)
    write(tmp_path / "schema" / "demo.yaml", rendered)
    host = slow_host(tmp_path, with_lokf=False, adopt="schema/demo.yaml")
    assert 'LINKML_SCHEMA_SOURCE_DIR="../schema"' in read(host / ".linkml" / "config.public.mk")
    for recipe in ("install", "lint", "test", "site"):
        result = gate(host, recipe)
        assert result, f"just {recipe} failed:\n{result.out[-3000:]}"
    assert (host / ".linkml" / "src" / "demo" / "datamodel" / "demo.py").is_file(), "gen-project read the adopted schema"
    assert read(host / "schema" / "demo.yaml") == rendered, "the adopted schema was changed"
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
