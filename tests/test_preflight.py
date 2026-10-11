"""linkml-preflight.sh always ends on its summary line and exits 0, whatever the host lacks.

It runs on a bare directory, names each sidecar shape, reads a KTL bundle's
floor and base IRI, warns about a Pages collision, a workflow name clash, a
uv workspace and a nested repository, says which steps a missing uv disables,
and refuses to run under sh.
"""

from __future__ import annotations

import os

import pytest

from conftest import PREFLIGHT, REPO, WORKFLOW, Git, add_lokf, bash, make_host, matches, read, run, write


def preflight(*args, cwd=None, env=None):
    return bash(PREFLIGHT, *args, cwd=cwd, env=env)


def test_runs_on_this_repository_and_ends_on_its_summary_line():
    result = preflight(".", cwd=REPO)
    assert result and matches(result.out, r"^Preflight: ") and matches(result.out, r"^missing sidecar"), result.out


def test_copes_with_a_bare_directory(tmp_path):
    result = preflight(cwd=tmp_path)
    assert result and matches(result.out, r"^info    git ") and matches(result.out, r"^missing sidecar") and matches(result.out, r"^Preflight: "), result.out


def test_says_which_steps_a_missing_uv_disables(tmp_path):
    result = preflight(tmp_path, env={"PATH": "/usr/bin:/bin"})
    assert result and matches(result.out, r"^missing uv ") and "Steps 1, 4 and 5" in result.out, result.out


def test_names_a_finished_sidecar_with_its_pin(tmp_path):
    host = make_host(tmp_path)
    write(host / ".linkml" / ".copier-answers.yml", "_commit: v0.5.0\n_src_path: gh:linkml/linkml-project-copier\nproject_slug: demo\n")
    write(host / ".linkml" / "config.public.mk", 'LINKML_SCHEMA_NAME="demo"\nLINKML_SCHEMA_SOURCE_DIR="src/demo/schema"\n')
    write(host / ".linkml" / "src" / "demo" / "schema" / "demo.yaml", "id: x\n")
    result = preflight(host)
    assert result and matches(result.out, r"^ok      sidecar .*gh:linkml/linkml-project-copier at v0\.5\.0") and matches(result.out, r"^ok      project .*\.linkml/src/demo/schema/demo\.yaml"), result.out
    assert matches(result.out, r"^info    doorway .*ln -s \.linkml/src/demo/schema linkml_schema"), result.out


def test_warns_about_a_half_made_sidecar_and_a_nested_repository(tmp_path):
    host = make_host(tmp_path)
    (host / ".linkml").mkdir()
    result = preflight(host)
    assert result and matches(result.out, r"^warn    sidecar .*no \.copier-answers\.yml"), result.out
    write(host / ".linkml" / ".copier-answers.yml", "_commit: v0.5.0\n")
    (host / ".linkml" / ".git").mkdir()
    result = preflight(host)
    assert result and matches(result.out, r"^warn    sidecar .*\.linkml/\.git exists"), result.out


def test_names_a_visible_sidecar_and_a_root_project_without_claiming_them(tmp_path):
    host = make_host(tmp_path)
    write(host / "linkml" / ".copier-answers.yml", "_commit: v0.5.0\n")
    result = preflight(host)
    assert result and matches(result.out, r"^info    sidecar .*visible linkml/ sidecar"), result.out
    (host / "linkml" / ".copier-answers.yml").unlink()
    write(host / ".copier-answers.yml", "_commit: v0.5.0\n")
    result = preflight(host)
    assert result and matches(result.out, r"^info    sidecar .*itself a copier project"), result.out


def test_reads_a_ktl_bundle_and_warns_without_a_base_iri(tmp_path):
    host = make_host(tmp_path)
    add_lokf(host)
    result = preflight(host)
    assert result and matches(result.out, r"^ok      lokf .*with-KTL mode; lokf floor >=0\.8\.0; \.lokf/lokf\.yaml pinned; \.lokf/justfile schema not wired; base_iri https://fixture\.example/knowledge/"), result.out
    write(host / ".lokf" / "knowledge" / "index.md", "---\ntitle: no base\n---\n")
    result = preflight(host)
    assert result and matches(result.out, r"^warn    lokf .*no base_iri"), result.out


def test_warns_about_a_pages_collision_a_workflow_clash_and_a_uv_workspace(tmp_path):
    host = make_host(tmp_path)
    Git(host)("branch", "gh-pages")
    write(host / ".github" / "workflows" / "linkml-sidecar.yaml", "name: something else\n")
    write(host / "pyproject.toml", "[tool.uv.workspace]\nmembers = []\n")
    result = preflight(host)
    assert result and matches(result.out, r"^warn    pages .*gh-pages"), result.out
    assert matches(result.out, r"^warn    workflows .*not the sidecar's hoisted workflow"), result.out
    assert matches(result.out, r"^warn    workspace "), result.out


def test_reports_the_hoisted_workflow_when_present(tmp_path):
    host = make_host(tmp_path)
    write(host / ".github" / "workflows" / "linkml-sidecar.yaml", "defaults:\n  run:\n    working-directory: .linkml\n")
    result = preflight(host)
    assert result and matches(result.out, r"^ok      workflows  linkml-sidecar\.yaml present"), result.out


def test_notes_gitignored_mode(tmp_path):
    host = make_host(tmp_path)
    write(host / ".gitignore", ".linkml/\nlinkml_schema\n")
    result = preflight(host)
    assert result and matches(result.out, r"^info    gitignore .*gitignored mode"), result.out


@pytest.mark.skipif(bool(run(["sh", "-c", "echo ${BASH_VERSION:-}"]).out.strip()), reason="sh is bash here, which the guard accepts")
def test_refuses_sh():
    result = run(["sh", PREFLIGHT])
    assert result.rc == 2 and "run this with bash" in result.out, result.out


@pytest.mark.skipif(os.name != "posix", reason="symlinks")
def test_sees_the_doorway(tmp_path):
    host = make_host(tmp_path)
    (host / ".linkml" / "src" / "demo" / "schema").mkdir(parents=True)
    os.symlink(".linkml/src/demo/schema", host / "linkml_schema")
    result = preflight(host)
    assert result and matches(result.out, r"^ok      doorway    linkml_schema -> \.linkml/src/demo/schema"), result.out


def test_the_sidecars_own_workflow_is_no_pages_collision(tmp_path):
    host = make_host(tmp_path)
    write(host / ".github" / "workflows" / "linkml-sidecar.yaml", read(WORKFLOW))
    result = preflight(host)
    assert result and matches(result.out, r"^ok      workflows  linkml-sidecar\.yaml present"), result.out
    assert not matches(result.out, r"^warn    pages "), result.out


def test_a_ktl_justfile_with_an_empty_schema_variable_is_not_wired(tmp_path):
    host = make_host(tmp_path)
    add_lokf(host)
    write(host / ".lokf" / "justfile", 'bundle := "knowledge"\nschema := ""\n')
    result = preflight(host)
    assert result and "schema not wired" in result.out, result.out
    write(host / ".lokf" / "justfile", 'bundle := "knowledge"\nschema := "../.linkml/src/demo/schema/demo.yaml"\n')
    result = preflight(host)
    assert result and "schema wired (../.linkml/src/demo/schema/demo.yaml)" in result.out, result.out


def test_warns_below_the_repository_root(tmp_path):
    host = make_host(tmp_path)
    (host / "sub").mkdir()
    result = preflight(host / "sub")
    assert result and matches(result.out, r"^warn    git +this directory is sub/ inside its repository"), result.out
    result = preflight(host)
    assert result and not matches(result.out, r"^warn    git "), result.out
