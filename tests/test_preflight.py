"""linkml-preflight.sh always ends on its summary line and exits 0, whatever the host lacks.

It runs on a bare directory, tells a sidecar from a project elsewhere, a
configuration-only .linkml/ and a schema file found by content, names the
tools that run on each, counts the people in the schema folder's history,
reads a KTL bundle's floor and base IRI, warns about
a Pages collision, a workflow name clash, a uv workspace and a nested
repository, says which steps a missing uv disables, and refuses to run under
sh.
"""

from __future__ import annotations

import os
import re

import pytest

from conftest import PREFLIGHT, REPO, WORKFLOW, Git, add_lokf, bash, make_host, matches, read, run, write

OURS = "_commit: v0.5.0\n_src_path: gh:linkml/linkml-project-copier\n"
SCHEMA = "id: https://w3id.org/acme/demo\nname: demo\nimports:\n  - linkml:types\nclasses:\n  Thing:\n"


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


def test_tells_an_empty_a_half_made_and_a_nested_dot_linkml_apart(tmp_path):
    host = make_host(tmp_path)
    (host / ".linkml").mkdir()
    result = preflight(host)
    assert result and matches(result.out, r"^info    sidecar    \.linkml/ is empty") and matches(result.out, r"^missing sidecar"), result.out
    write(host / ".linkml" / "justfile", "lint:\n")
    result = preflight(host)
    assert result and matches(result.out, r"^warn    sidecar    \.linkml/ holds justfile but no \.copier-answers\.yml or config\.public\.mk"), result.out
    write(host / ".linkml" / ".copier-answers.yml", "_commit: v0.5.0\n")
    (host / ".linkml" / ".git").mkdir()
    result = preflight(host)
    assert result and matches(result.out, r"^ok      sidecar    \.linkml/ from") and matches(result.out, r"^warn    sidecar .*\.linkml/\.git exists"), result.out


def test_configuration_files_in_dot_linkml_are_reported_and_hide_nothing(tmp_path):
    host = make_host(tmp_path)
    write(host / ".linkml" / "upstream.toml", "[linkml]\n")
    result = preflight(host)
    assert result and matches(result.out, r"^info    sidecar    \.linkml/ holds configuration files \(upstream\.toml\) and no project; linkml-sidecar installs around them"), result.out
    assert matches(result.out, r"^missing sidecar") and not matches(result.out, r"^warn    sidecar"), result.out
    # The same .linkml/ beside a project at the root: the project is found, and nothing warns.
    write(host / ".copier-answers.yml", OURS + "project_slug: demo\n")
    write(host / "src" / "demo" / "schema" / "demo.yaml", SCHEMA)
    result = preflight(host)
    assert result and matches(result.out, r"^info    sidecar    this repository is itself a LinkML schema project \(copier answers: gh:linkml/linkml-project-copier at v0\.5\.0\)"), result.out
    assert matches(result.out, r"^ok      project    schema src/demo/schema/demo\.yaml"), result.out
    assert not matches(result.out, r"^(warn|missing) +sidecar") and not matches(result.out, r"^info    doorway"), result.out


def test_names_a_project_elsewhere_without_claiming_it_and_ignores_another_template(tmp_path):
    host = make_host(tmp_path)
    write(host / "linkml" / ".copier-answers.yml", OURS)
    result = preflight(host)
    assert result and matches(result.out, r"^info    sidecar    linkml/ is a LinkML schema project \(copier answers"), result.out
    (host / "linkml" / ".copier-answers.yml").unlink()
    write(host / ".copier-answers.yml", OURS)
    result = preflight(host)
    assert result and matches(result.out, r"^info    sidecar    this repository is itself a LinkML schema project"), result.out
    write(host / ".copier-answers.yml", "_commit: v1.0.0\n_src_path: gh:acme/python-service-template\n")
    result = preflight(host)
    assert result and matches(result.out, r"^missing sidecar"), result.out


def test_names_a_cookiecutter_project_and_its_make_targets(tmp_path):
    host = make_host(tmp_path)
    write(host / "config.public.mk", 'LINKML_SCHEMA_NAME="demo"\nLINKML_SCHEMA_SOURCE_DIR="src/demo/schema"\n')
    write(host / "Makefile", "lint:\n\tlinkml-lint src/demo/schema\n")
    write(host / "src" / "demo" / "schema" / "demo.yaml", SCHEMA)
    result = preflight(host)
    assert result and matches(result.out, r"^info    sidecar    this repository is itself a LinkML schema project \(config\.public\.mk\)"), result.out
    assert matches(result.out, r"^ok      project    schema src/demo/schema/demo\.yaml") and matches(result.out, r"^info    tools      make -C \. <target>"), result.out


def test_finds_a_project_one_level_down_and_where_it_was_started(tmp_path):
    host = make_host(tmp_path)
    write(host / "model" / ".copier-answers.yml", OURS + "project_slug: demo\n")
    write(host / "model" / "src" / "demo" / "schema" / "demo.yaml", SCHEMA)
    result = preflight(host)
    # No config.public.mk: the answers' project_slug names the schema.
    assert result and matches(result.out, r"^info    sidecar    model/ is a LinkML schema project \(copier answers") and matches(result.out, r"^ok      project    schema model/src/demo/schema/demo\.yaml"), result.out
    assert matches(result.out, r"^info    tools      uv run --project model/ linkml-lint"), result.out
    deep = host / "packages" / "deep"
    write(deep / "config.public.mk", 'LINKML_SCHEMA_NAME="deep"\nLINKML_SCHEMA_SOURCE_DIR="src/deep/schema"\n')
    write(deep / "justfile", "lint:\n")
    write(deep / "src" / "deep" / "schema" / "deep.yaml", SCHEMA)
    result = preflight(cwd=deep)
    assert result and matches(result.out, r"^info    sidecar    packages/deep/ is a LinkML schema project \(config\.public\.mk\)"), result.out
    assert matches(result.out, r"^info    sidecar    also a LinkML schema project: model/"), result.out
    assert matches(result.out, r"^info    tools      just --justfile packages/deep/justfile <recipe>"), result.out


def test_finds_schema_files_by_content_and_names_the_tools(tmp_path):
    host = make_host(tmp_path)
    write(host / "schema" / "demo.yaml", SCHEMA)
    write(host / "docs" / "schema" / "demo.yaml", SCHEMA)
    write(host / ".github" / "workflows" / "release.yaml", "on: push\nenv:\n  BASE: https://w3id.org/linkml/\njobs: {}\n")
    write(host / "data" / "config.yaml", "prefix: https://w3id.org/linkml/\n")
    result = preflight(host)
    assert result and matches(result.out, r"^info    sidecar    no sidecar or project; 1 LinkML schema file\(s\) found by content"), result.out
    assert matches(result.out, r"^ok      schema     schema/demo\.yaml$") and result.out.count("schema/demo.yaml") == 1, result.out
    assert matches(result.out, r"^info    tools      uvx --from linkml linkml-lint <schema>") and not matches(result.out, r"^missing sidecar"), result.out
    write(host / "pyproject.toml", '[project]\nname = "demo"\ndependencies = ["linkml>=1.9"]\n')
    write(host / "uv.lock", "version = 1\n")
    result = preflight(host)
    assert result and matches(result.out, r"^info    tools      uv run linkml-lint <schema>"), result.out
    (host / "uv.lock").unlink()
    write(host / "poetry.lock", "")
    result = preflight(host)
    assert result and matches(result.out, r"^info    tools      poetry run linkml-lint <schema>"), result.out


def test_an_adopted_schema_is_named_where_it_lives(tmp_path):
    host = make_host(tmp_path)
    write(host / ".linkml" / ".copier-answers.yml", OURS + "project_slug: demo\n")
    write(host / ".linkml" / "config.public.mk", 'LINKML_SCHEMA_NAME="demo"\nLINKML_SCHEMA_SOURCE_DIR="../schema"\n')
    write(host / "schema" / "demo.yaml", SCHEMA)
    result = preflight(host)
    assert result and matches(result.out, r"^ok      project    schema schema/demo\.yaml; no \.venv"), result.out
    assert matches(result.out, r"^info    doorway    no linkml_schema doorway: the adopted schema is already visible at schema/"), result.out


def test_a_root_project_gets_no_sidecar_hints(tmp_path):
    host = make_host(tmp_path)
    write(host / ".copier-answers.yml", OURS + "project_slug: demo\n")
    write(host / "src" / "demo" / "schema" / "demo.yaml", SCHEMA)
    Git(host)("branch", "gh-pages")
    write(host / ".github" / "workflows" / "deploy.yaml", "name: docs\non: push\njobs: {}\n# mkdocs gh-deploy\n")
    write(host / "pyproject.toml", "[tool.uv.workspace]\nmembers = []\n")
    result = preflight(host)
    assert result and not matches(result.out, r"^warn    pages") and not matches(result.out, r"^warn    workspace"), result.out
    assert matches(result.out, r"^info    workflows  1 workflow\(s\) in \.github/workflows/; the project's own are its gate"), result.out


def test_offers_to_move_the_generators_settings_and_warns_when_both_files_exist(tmp_path):
    root = make_host(tmp_path / "root")
    write(root / ".copier-answers.yml", OURS + "project_slug: demo\n")
    write(root / "config.public.mk", 'LINKML_SCHEMA_NAME="demo"\nLINKML_GENERATORS_CONFIG_YAML=config.yaml\n')
    write(root / "config.yaml", "excludes: []\n")
    result = preflight(root)
    assert result and matches(result.out, r"^info    generators config\.yaml holds the generators' settings; linkml-sidecar --repair generators\.yaml moves it to \.linkml/generators\.yaml"), result.out
    side = make_host(tmp_path / "side")
    write(side / ".linkml" / ".copier-answers.yml", OURS + "project_slug: demo\n")
    write(side / ".linkml" / "config.public.mk", 'LINKML_SCHEMA_NAME="demo"\nLINKML_GENERATORS_CONFIG_YAML=generators.yaml\n')
    write(side / ".linkml" / "generators.yaml", "excludes: []\n")
    result = preflight(side)
    assert result and not matches(result.out, r"^\w+ +generators"), result.out
    write(side / ".linkml" / "config.yaml", "excludes: []\n")
    result = preflight(side)
    assert result and matches(result.out, r"^warn    generators \.linkml/config\.yaml exists beside generators\.yaml, which the recipes read"), result.out


def commit_as(host, name, email, message, path=None, text="x\n"):
    """One commit by the given author; path is a file to write first, or none for an empty commit."""
    if path is not None:
        write(host / path, text)
        Git(host)("add", "-A")
    done = run(["git", "-C", host, *Git.OPTIONS, "commit", "-q", "--allow-empty", "-m", message], env={"GIT_AUTHOR_NAME": name, "GIT_AUTHOR_EMAIL": email})
    assert done, done.out


def test_counts_the_people_in_the_schema_folders_history(tmp_path):
    host = make_host(tmp_path / "host")  # the session fixture makes every author "Test <test@example.invalid>"
    commit_as(host, "Test", "test@example.invalid", "schema", "schema/demo.yaml", SCHEMA)
    commit_as(host, "two", "Two@example.invalid", "more", "schema/demo.yaml", SCHEMA + "  Other:\n")
    commit_as(host, "dependabot[bot]", "49699333+dependabot[bot]@users.noreply.github.com", "bump", "schema/demo.yaml", SCHEMA + "  Other:\n  Third:\n")
    commit_as(host, "four", "four@example.invalid", "readme", "README.md", "# Demo\n\nChanged.\n")
    result = preflight(host)
    assert result and matches(result.out, r"""^info    authors    schema folder schema/: 2 people, 2 commits \("Test", "two"\), and 1 bot commit; git shortlog -sne --no-merges HEAD -- 'schema' for the detail$"""), result.out
    write(host / ".mailmap", "<test@example.invalid> <two@example.invalid>\n")
    result = preflight(host)
    assert result and matches(result.out, r"""^info    authors    schema folder schema/: 1 person, 2 commits \("Test", "two"\), and 1 bot commit;"""), result.out
    bare = make_host(tmp_path / "bare", git=False)
    write(bare / "schema" / "demo.yaml", SCHEMA)
    result = preflight(bare)
    assert result and matches(result.out, r"^ok      schema     schema/demo\.yaml") and not matches(result.out, r"^info    authors"), result.out
    side = make_host(tmp_path / "side")
    write(side / ".linkml" / ".copier-answers.yml", OURS + "project_slug: demo\n")
    write(side / ".linkml" / "config.public.mk", 'LINKML_SCHEMA_NAME="demo"\nLINKML_SCHEMA_SOURCE_DIR="src/demo/schema"\n')
    write(side / ".linkml" / "src" / "demo" / "schema" / "demo.yaml", SCHEMA)
    result = preflight(side)
    assert result and not matches(result.out, r"^info    authors"), result.out
    Git(side)("add", "-A")
    Git(side)("commit", "-q", "-m", "sidecar")
    result = preflight(side)
    assert result and matches(result.out, r"""^info    authors    schema folder \.linkml/src/demo/schema/: 1 person, 1 commit \("Test"\);"""), result.out


def test_the_authors_line_survives_awkward_names_folders_and_bots(tmp_path):
    host = make_host(tmp_path / "host")
    folder = "my schema"
    commit_as(host, "3", "three@example.invalid", "a", f"{folder}/demo.yaml", SCHEMA)
    for i in range(2):
        commit_as(host, "3", "three@example.invalid", f"b{i}", f"{folder}/demo.yaml", SCHEMA + f"  C{i}:\n")
    commit_as(host, "1 Direction", "one@example.invalid", "c", f"{folder}/demo.yaml", SCHEMA + "  D:\n")
    commit_as(host, "Ann Lee", "Ann@Example.org", "d", f"{folder}/demo.yaml", SCHEMA + "  E:\n")
    commit_as(host, "Ann Lee", "ann@example.org", "e", f"{folder}/demo.yaml", SCHEMA + "  F:\n")
    commit_as(host, "Mary Abbott", "mary.abbott@example.org", "f", f"{folder}/demo.yaml", SCHEMA + "  G:\n")
    commit_as(host, "Eve\x1b[2K\rok", "eve@example.org", "g", f"{folder}/demo.yaml", SCHEMA + "  H:\n")
    commit_as(host, "IBM Open Source Bot", "66631603+ibm-open-source-bot@users.noreply.github.com", "h", f"{folder}/demo.yaml", SCHEMA + "  I:\n")
    commit_as(host, "Renovate", "renovate@example.org", "i", f"{folder}/demo.yaml", SCHEMA + "  J:\n")
    result = preflight(host)
    # Ann's two emails differ only by case, so she is one person; the names
    # are cut after the count, so "3" and "1 Direction" survive whole; the
    # escape is stripped; two bots are counted apart; the hint quotes the folder.
    assert result and matches(result.out, r"""^info    authors    schema folder my schema/: 5 people, 8 commits \("3", "Ann Lee", "1 Direction", "Eve\[2Kok", "Mary Abbott"\), and 2 bot commits; git shortlog -sne --no-merges HEAD -- 'my schema' for the detail$"""), result.out
    assert "\x1b" not in result.out and "\r" not in result.out, repr(result.out)
    commit_as(host, "Zed", "zed@example.org", "j", f"{folder}/demo.yaml", SCHEMA + "  K:\n")
    result = preflight(host)
    assert result and matches(result.out, r"""^info    authors    schema folder my schema/: 6 people, 9 commits \("3", "Ann Lee", "1 Direction", "Eve\[2Kok", and 2 more\)"""), result.out


def test_a_folder_only_bots_touched_and_a_pathspec_lookalike(tmp_path):
    host = make_host(tmp_path / "host")
    commit_as(host, "dependabot[bot]", "49699333+dependabot[bot]@users.noreply.github.com", "bump", "schema/demo.yaml", SCHEMA)
    result = preflight(host)
    assert result and matches(result.out, r"^info    authors    schema folder schema/: no person, only 1 bot commit;"), result.out
    magic = make_host(tmp_path / "magic")
    commit_as(magic, "Ann", "ann@example.org", "schema", ":!x/demo.yaml", SCHEMA)
    commit_as(magic, "Bob", "bob@example.org", "readme", "README.md", "# Demo\n\nChanged.\n")
    result = preflight(magic)
    # Read literally, ":!x" is a folder; as pathspec magic it would exclude itself and count everyone.
    assert result and matches(result.out, r"""^info    authors    schema folder :!x/: 1 person, 1 commit \("Ann"\);"""), result.out


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
    assert result and matches(result.out, r"^ok      workflows  \.github/workflows/linkml-sidecar\.yaml present"), result.out


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
    assert result and matches(result.out, r"^ok      workflows  \.github/workflows/linkml-sidecar\.yaml present"), result.out
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


# The index, lock and network lines read uv's settings from the environment
# and a user uv.toml, so these tests run with neither, and with an empty
# configuration folder, whatever the machine running them sets.
NO_INDEX = ("UV_DEFAULT_INDEX", "UV_INDEX_URL", "LINKML_TEMPLATE_SRC")


def preflight_at(host, tmp_path, env=None, unset=NO_INDEX):
    return run(["bash", PREFLIGHT, host], env={"XDG_CONFIG_HOME": tmp_path / "config", **(env or {})}, unset=unset)


def sidecar_with_lock(tmp_path, registry):
    host = make_host(tmp_path / "host")
    write(host / ".linkml" / ".copier-answers.yml", OURS + "project_slug: demo\n")
    write(host / ".linkml" / "config.public.mk", 'LINKML_SCHEMA_NAME="demo"\nLINKML_SCHEMA_SOURCE_DIR="src/demo/schema"\n')
    write(host / ".linkml" / "src" / "demo" / "schema" / "demo.yaml", "id: x\n")
    write(host / ".linkml" / "uv.lock", f'[[package]]\nname = "linkml"\nsource = {{ registry = "{registry}" }}\n')
    return host


def test_warns_when_the_lock_was_made_against_another_index(tmp_path):
    host = sidecar_with_lock(tmp_path, "https://pypi.org/simple")
    result = preflight_at(host, tmp_path, env={"UV_DEFAULT_INDEX": "https://reader:s3cret@nexus.example:8443/repository/pypi/simple"})
    assert result and matches(result.out, r"^warn    lock       \.linkml/uv\.lock was made against pypi\.org, and uv here reads nexus\.example - just install rewrites it"), result.out
    assert "s3cret" not in result.out and "reader" not in result.out, result.out
    result = preflight_at(host, tmp_path)
    assert result and not matches(result.out, r"^warn    lock"), result.out


def test_reads_the_default_index_from_a_user_uv_toml(tmp_path):
    host = sidecar_with_lock(tmp_path, "https://mirror.example/simple")
    toml = '[[index]]\nname = "extra"\nurl = "https://extra.example/simple"\n\n[[index]]\nname = "corp"\nurl = "https://mirror.example/simple"\ndefault = true\n'
    write(tmp_path / "config" / "uv" / "uv.toml", toml)
    result = preflight_at(host, tmp_path)
    assert result and not matches(result.out, r"^warn    lock") and "packages from mirror.example" in result.out, result.out
    write(tmp_path / "config" / "uv" / "uv.toml", 'index-url = "https://old.example/simple"\n')
    result = preflight_at(host, tmp_path)
    assert result and matches(result.out, r"^warn    lock .* made against mirror\.example, and uv here reads old\.example "), result.out


def test_the_network_line_names_the_template_and_the_index_it_would_ask(tmp_path):
    host = make_host(tmp_path / "host")
    result = preflight_at(host, tmp_path)
    assert result and "the template from github.com and packages from pypi.org" in result.out, result.out
    result = preflight_at(host, tmp_path, env={"LINKML_TEMPLATE_SRC": "https://git.example/mirror/linkml-project-copier.git"}, unset=NO_INDEX[:2])
    assert result and "the template from git.example" in result.out, result.out
    rule = write(tmp_path / "gitconfig", '[url "https://copy.example/linkml-project-copier.git"]\n\tinsteadOf = https://github.com/linkml/linkml-project-copier.git\n')
    result = preflight_at(host, tmp_path, env={"GIT_CONFIG_GLOBAL": rule})
    assert result and "the template from copy.example" in result.out, result.out


def stubs(tmp_path, uvx_says="", curl_rc=0):
    """uv, uvx and curl stand-ins first on PATH: uvx fails with uvx_says, curl exits curl_rc."""
    bindir = tmp_path / "bin"
    write(bindir / "uv", '#!/bin/sh\ncase "$1" in --version) echo "uv 0.12.11" ;; python) echo /usr/bin/python3 ;; esac\n')
    write(bindir / "uvx", f'#!/bin/sh\necho "{uvx_says}" >&2\nexit 1\n')
    write(bindir / "curl", f"#!/bin/sh\nexit {curl_rc}\n")
    for stub in bindir.iterdir():
        stub.chmod(0o755)
    return {"PATH": f"{bindir}:/usr/bin:/bin"}


@pytest.mark.parametrize(
    "uv_says, why",
    [
        ("hint: Consider enabling use of system TLS certificates with the `--system-certs` command-line flag", "uv does not trust this network's certificates - set UV_SYSTEM_CERTS=true"),
        ("error: No interpreter found for Python >=3.9 in virtual environments, managed installations, or search path", "uv finds no Python that copier runs on"),
        ("Caused by: dns error: failed to lookup address information", "uv cannot reach the package index pypi.org"),
    ],
)
def test_says_why_uvx_cannot_run_copier(tmp_path, uv_says, why):
    result = preflight_at(make_host(tmp_path / "host"), tmp_path, env=stubs(tmp_path, uv_says), unset=NO_INDEX + ("LINKML_PREFLIGHT_OFFLINE",))
    assert result and matches(result.out, rf"^missing copier     {re.escape(why)}"), result.out


def test_names_what_it_cannot_reach(tmp_path):
    result = preflight_at(make_host(tmp_path / "host"), tmp_path, env=stubs(tmp_path, curl_rc=7), unset=NO_INDEX + ("LINKML_PREFLIGHT_OFFLINE",))
    assert result and matches(result.out, r"^warn    network    github\.com unreachable - copier cannot fetch the template; a company copy goes in LINKML_TEMPLATE_SRC"), result.out
    assert matches(result.out, r"^warn    network    pypi\.org unreachable - uv cannot install copier, just or linkml; a company mirror goes in UV_DEFAULT_INDEX"), result.out


def test_on_forgejo_names_the_one_workflow_folder_it_reads(tmp_path):
    host = make_host(tmp_path / "host")
    Git(host)("remote", "add", "origin", "https://codeberg.org/acme/demo.git")
    result = preflight(host)
    assert result and matches(result.out, r"^info    workflows  no workflow folder yet; on Forgejo, Step 5 lays down \.forgejo/workflows/linkml-sidecar\.yaml"), result.out
    write(host / ".github" / "workflows" / "ci.yaml", "name: ci\n")
    result = preflight(host)
    assert result and matches(result.out, r"^info    workflows  1 workflow\(s\) in \.github/workflows/, none for the sidecar"), result.out
    write(host / ".forgejo" / "workflows" / "linkml-sidecar.yaml", "defaults:\n  run:\n    working-directory: .linkml\n")
    result = preflight(host)
    assert result and matches(result.out, r"^ok      workflows  \.forgejo/workflows/linkml-sidecar\.yaml present"), result.out
