"""The hoisted workflow template holds what the sidecar needs: every step in .linkml/, pinned actions, a locked install, and a docs job that never touches the host's Pages root."""

from __future__ import annotations

import re

import yaml

from conftest import WORKFLOW, read

TEXT = read(WORKFLOW)
DOC = yaml.safe_load(TEXT)
JOBS = DOC["jobs"]


def test_every_action_is_pinned_to_a_commit_with_its_version_beside_it():
    for line in TEXT.splitlines():
        if re.match(r"\s*-?\s*uses:", line):
            assert re.search(r"@[0-9a-f]{40} # v[0-9]+\.[0-9]+\.[0-9]+$", line), line


def test_every_step_runs_in_the_sidecar_and_installs_from_the_lock():
    assert DOC["defaults"]["run"]["working-directory"] == ".linkml"
    for job in JOBS.values():
        for step in job["steps"]:
            if "cache-dependency-glob" in step.get("with", {}):
                assert step["with"]["cache-dependency-glob"] == ".linkml/uv.lock"
    runs = [step["run"] for job in JOBS.values() for step in job["steps"] if "run" in step]
    assert any("uv sync --locked --group dev" in r for r in runs)
    assert any(r.strip() == "just lint" for r in runs) and any(r.strip() == "just test" for r in runs)
    assert not any("gh-deploy" in r or "just deploy" in r or "just setup" in r for r in runs)


def test_it_triggers_on_the_sidecar_and_the_pinned_core_schema():
    triggers = DOC[True] if True in DOC else DOC["on"]
    for event in ("pull_request", "push"):
        assert ".linkml/**" in triggers[event]["paths"] and ".lokf/lokf.yaml" in triggers[event]["paths"]
    assert "workflow_dispatch" in triggers


def test_permissions_are_empty_at_the_top_and_write_only_where_publishing_happens():
    assert DOC["permissions"] == {}
    assert JOBS["lint-and-test"]["permissions"] == {"contents": "read"}
    assert JOBS["docs"]["permissions"] == {"contents": "read"}
    assert JOBS["publish-docs"]["permissions"] == {"contents": "write"}


def test_publishing_is_gated_by_the_variable_and_scoped_to_the_subpath():
    publish = JOBS["publish-docs"]
    assert "vars.LINKML_DOCS_ENABLED == 'true'" in publish["if"] and "pull_request" in publish["if"]
    assert publish["needs"] == "docs"
    pages = [s for s in publish["steps"] if "peaceiris/actions-gh-pages" in s.get("uses", "")]
    assert len(pages) == 1
    assert pages[0]["with"]["destination_dir"] == "linkml" and pages[0]["with"]["keep_files"] is True
    artifact = [s for s in JOBS["docs"]["steps"] if "upload-artifact" in s.get("uses", "")]
    assert artifact and artifact[0]["with"]["path"] == ".linkml/site"
