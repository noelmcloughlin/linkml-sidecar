"""The Forgejo workflow template runs the GitHub template's gate, and differs only where Forgejo does.

Every step runs in .linkml/ and installs from the lock, as on GitHub. Each
action is pinned by its full address to the commit the GitHub template
pins, there is no harden-runner, and the site is built and published in one
job, under the linkml/ subpath of the Codeberg Pages site only.
"""

from __future__ import annotations

import re

import yaml

from conftest import FORGEJO_WORKFLOW, WORKFLOW, read

TEXT = read(FORGEJO_WORKFLOW)
DOC = yaml.safe_load(TEXT)
JOBS = DOC["jobs"]
TRIGGERS = DOC[True] if True in DOC else DOC["on"]


def uses(text):
    return re.findall(r"^\s*-?\s*uses:\s*(\S+)", text, re.M)


def test_every_action_is_pinned_by_its_full_address_with_its_version_beside_it():
    for line in TEXT.splitlines():
        if re.match(r"\s*-?\s*uses:", line):
            assert re.search(r"uses: https://[^/ ]+/[^@ ]+@[0-9a-f]{40} # v[0-9]+\.[0-9]+\.[0-9]+$", line), line


def test_an_action_both_templates_use_is_pinned_to_the_same_commit():
    github = {u.split("@")[0]: u.split("@")[1] for u in uses(read(WORKFLOW))}
    for full in uses(TEXT):
        name, commit = re.sub(r"^https://[^/]+/", "", full).split("@")
        if name in github:
            assert commit == github[name], full


def test_every_step_runs_in_the_sidecar_and_installs_from_the_lock():
    assert DOC["defaults"]["run"]["working-directory"] == ".linkml"
    runs = [step["run"] for job in JOBS.values() for step in job["steps"] if "run" in step]
    assert sum("uv sync --locked --group dev" in r for r in runs) == 2
    assert any(r.strip() == "just lint" for r in runs) and any(r.strip() == "just test" for r in runs)
    assert not any("gh-deploy" in r or "just deploy" in r or "just setup" in r for r in runs)


def test_it_triggers_on_the_sidecar_and_the_workflow_in_any_folder_forgejo_reads():
    for event in ("pull_request", "push"):
        paths = TRIGGERS[event]["paths"]
        assert ".linkml/**" in paths and ".lokf/lokf.yaml" in paths and "**/workflows/linkml-sidecar.yaml" in paths
        assert "branches" not in TRIGGERS[event]
    assert "workflow_dispatch" in TRIGGERS


def test_it_runs_on_codeberg_without_the_github_only_pieces():
    assert {job["runs-on"] for job in JOBS.values()} == {"codeberg-small"}
    assert "permissions" not in DOC and not any("permissions" in job for job in JOBS.values())
    for action in uses(TEXT):
        assert not any(name in action for name in ("harden-runner", "upload-artifact", "download-artifact", "peaceiris")), action


def test_the_site_is_published_from_the_default_branch_under_the_subpath_only():
    docs = JOBS["docs"]
    assert docs["needs"] == "lint-and-test" and "pull_request" in docs["if"]
    assert "github.event.repository.default_branch" in docs["if"]
    publish = [s for s in docs["steps"] if "git-pages/action" in s.get("uses", "")]
    assert len(publish) == 1 and publish[0]["if"] == "vars.LINKML_DOCS_ENABLED == 'true'"
    assert publish[0]["with"]["path"] == "linkml" and publish[0]["with"]["source"] == ".linkml/site/"
    assert publish[0]["with"]["site"].startswith("https://${{ github.repository_owner }}.codeberg.page/")
