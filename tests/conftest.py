"""Shared helpers for the behavioural tests of the two skills' scripts.

These tests exercise skills/linkml-sidecar/scripts/ and templates/ on
throwaway hosts. The fast ones run the scaffold against tests/fake_copier.py,
which renders the few template files the scaffold touches without the
network, and a stub `.lokf/` under tests/fixtures/; the preflight runs with
LINKML_PREFLIGHT_OFFLINE=1, so they make no network call. The slow ones, switched
on by LINKML_SIDECAR_SLOW=1, run the real copier against a local clone of the
pinned template (LINKML_TEMPLATE_SRC, or .template-cache/linkml-project-copier
under the repository), then `just install`, `lint` and `test`, and need uv,
just and the network.

Run them from the repository root:

    uv run --no-project --with-requirements tests/requirements.txt pytest
    LINKML_SIDECAR_SLOW=1 uv run --no-project --with-requirements tests/requirements.txt pytest -m slow

Every subprocess runs under an isolated git config, so a global
`commit.gpgsign=true` signs no fixture commit, and under a TMPDIR of pytest's
own, so a script's temporary files are removed with the test's.
"""

from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
TESTS = Path(__file__).resolve().parent
SIDECAR = REPO / "skills" / "linkml-sidecar"
TEMPLATES = SIDECAR / "templates"
SCAFFOLD = SIDECAR / "scripts" / "linkml-scaffold.sh"
SCAFFOLD_PY = SIDECAR / "scripts" / "linkml-scaffold.py"
PREFLIGHT = TEMPLATES / "scripts" / "linkml-preflight.sh"
WORKFLOW = TEMPLATES / "github" / "linkml-sidecar.yaml"
FAKE_COPIER = TESTS / "fake_copier.py"
FIXTURES = TESTS / "fixtures"
FACTS = {
    "PROJ_NAME": "demo",
    "PROJ_SLUG": "demo",
    "PROJ_DESC": "A demo host.",
    "GITHUB_ORG": "acme",
    "REPO_URL": "https://github.com/acme/demo",
    "FULL_NAME": "Test Person",
    "EMAIL": "t@example.invalid",
    "LICENSE_ID": "Apache-2.0",
    "SCHEMA_ID": "https://w3id.org/acme/demo",
    "DOCS_URL": "https://acme.github.io/demo/linkml/",
}
TOKENS = ("<PROJ_", "<SCHEMA_ID>", "<DOCS_URL>", "<BASE_IRI>", "<LICENSE_ID>", "<TODAY>", "<REPO_URL>", "<TEMPLATE_REF>")


def have(tool: str) -> bool:
    return shutil.which(tool) is not None


def pin() -> tuple[str, str]:
    """The template pin the scaffold driver holds: (tag, commit)."""
    text = SCAFFOLD.read_text(encoding="utf-8")
    ref = re.search(r'LINKML_TEMPLATE_REF:=(v[0-9]+\.[0-9]+\.[0-9]+)', text)
    sha = re.search(r"LINKML_TEMPLATE_SHA:=([0-9a-f]{40})", text)
    assert ref and sha, "the scaffold driver holds no pin"
    return ref.group(1), sha.group(1)


def template_src() -> str | None:
    """A local clone of the pinned template for the slow tests, or None."""
    env = os.environ.get("LINKML_TEMPLATE_SRC")
    if env:
        return env
    cache = REPO / ".template-cache" / "linkml-project-copier"
    return str(cache) if (cache / "copier.yaml").is_file() else None


@dataclass
class Result:
    rc: int
    out: str

    def __bool__(self) -> bool:
        return self.rc == 0


def run(args, cwd=None, env=None, stdin=None, unset=()) -> Result:
    full_env = dict(os.environ)
    for name in unset:
        full_env.pop(name, None)
    if env:
        full_env.update({k: str(v) for k, v in env.items()})
    done = subprocess.run(
        [str(a) for a in args],
        cwd=str(cwd) if cwd else None,
        env=full_env,
        input=stdin,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    return Result(done.returncode, done.stdout.rstrip("\n"))


def bash(script, *args, cwd=None, env=None) -> Result:
    return run(["bash", script, *args], cwd=cwd, env=env)


class Git:
    OPTIONS = ("-c", "init.defaultBranch=main", "-c", "user.name=contract", "-c", "user.email=contract@example.invalid", "-c", "commit.gpgsign=false")

    def __init__(self, repo: Path):
        self.repo = Path(repo)

    def __call__(self, *args, check=True) -> str:
        result = run(["git", "-C", self.repo, *self.OPTIONS, *args])
        if check and result.rc != 0:
            raise RuntimeError(f"git {' '.join(str(a) for a in args)} failed in {self.repo}: {result.out}")
        return result.out

    def init(self) -> None:
        self("init", "-q")


def write(path: Path, content: str) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="")
    return path


def read(path: Path) -> str:
    return Path(path).read_text(encoding="utf-8", errors="replace")


def matches(text: str, pattern: str) -> bool:
    return re.search(pattern, text, re.M) is not None


def tokens_left(root: Path) -> list[str]:
    """Every line under root (skipping .venv and .git) that still holds a placeholder token."""
    hits = []
    for path in sorted(Path(root).rglob("*")):
        if not path.is_file() or ".venv" in path.parts or ".git" in path.parts:
            continue
        try:
            text = read(path)
        except OSError:
            continue
        for number, line in enumerate(text.splitlines(), start=1):
            if any(token in line for token in TOKENS):
                hits.append(f"{path}:{number}: {line.strip()}")
    return hits


def make_host(root: Path, readme=True, license_file=True, git=True) -> Path:
    """A minimal host repository: a README with an intro and a section, a LICENSE, one commit."""
    root.mkdir(parents=True, exist_ok=True)
    if readme:
        write(root / "README.md", "# Demo\n\nA demo host.\n\n## Usage\n\nRun it.\n")
    if license_file:
        shutil.copy(REPO / "LICENSE", root / "LICENSE")
    if git:
        g = Git(root)
        g.init()
        g("add", "-A")
        g("commit", "-q", "--allow-empty", "-m", "init")
    return root


def add_lokf(root: Path, stub_schema=True, before_schema=False) -> Path:
    """A `.lokf/` from the fixture: ktl-sidecar's justfile and pyproject, a bundle header, and the stub core schema unless the slow tests want the real one pinned.

    before_schema takes the justfile of a ktl-sidecar release from before the
    `schema` variable, whose lines the scaffold patches by exact match.
    """
    target = root / ".lokf"
    shutil.copytree(FIXTURES / "lokf", target, dirs_exist_ok=True)
    if before_schema:
        shutil.copy(FIXTURES / "lokf-before-schema" / "justfile", target / "justfile")
    if not stub_schema:
        (target / "lokf.yaml").unlink()
    return target


def scaffold(host: Path, *args, facts=None, env=None, fake=True) -> Result:
    """Run the scaffold on host with the standard facts; the fake copier unless fake=False."""
    full = dict(FACTS if facts is None else facts)
    if fake:
        full["LINKML_COPIER"] = f"{sys.executable} {FAKE_COPIER}"
        full["LINKML_TEMPLATE_SRC"] = "gh:linkml/linkml-project-copier"
    full["LINKML_TEMPLATE_SKIP_PIN_CHECK"] = "1"
    if env:
        full.update(env)
    return bash(SCAFFOLD, "--host", str(host), *args, env=full)


def load_scaffold_module():
    """The scaffold's Python half as a module, for unit tests of its pure functions."""
    import importlib.util

    spec = importlib.util.spec_from_file_location("linkml_scaffold", SCAFFOLD_PY)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="session", autouse=True)
def _isolated_environment(tmp_path_factory):
    patch = pytest.MonkeyPatch()
    patch.setenv("GIT_CONFIG_GLOBAL", "/dev/null")
    patch.setenv("GIT_CONFIG_SYSTEM", "/dev/null")
    patch.setenv("TMPDIR", str(tmp_path_factory.getbasetemp()))
    # An identity for every git call, even one that does not go through Git:
    # without it git builds one from the host's FQDN, a 15 s DNS wait on a
    # machine whose hostname does not resolve.
    for kind in ("AUTHOR", "COMMITTER"):
        patch.setenv(f"GIT_{kind}_NAME", "Test")
        patch.setenv(f"GIT_{kind}_EMAIL", "test@example.invalid")
    patch.setenv("LINKML_PREFLIGHT_OFFLINE", "1")
    for name in FACTS:
        patch.delenv(name, raising=False)
    for name in (
        "LINKML_COPIER", "LINKML_TEMPLATE_REF", "LINKML_TEMPLATE_SHA", "LINKML_TEMPLATE_SKIP_PIN_CHECK",
        "LINKML_MODE", "BASE_IRI", "COPYRIGHT_YEAR", "TODAY", "FAKE_COPIER_FAIL", "FAKE_COPIER_GIT", "GIT_DIR", "GIT_WORK_TREE",
    ):
        patch.delenv(name, raising=False)
    yield
    patch.undo()


def pytest_collection_modifyitems(config, items):
    if os.environ.get("LINKML_SIDECAR_SLOW") == "1":
        return
    skip = pytest.mark.skip(reason="slow: set LINKML_SIDECAR_SLOW=1 (needs uv, just, the network and a template clone)")
    for item in items:
        if "slow" in item.keywords:
            item.add_marker(skip)
