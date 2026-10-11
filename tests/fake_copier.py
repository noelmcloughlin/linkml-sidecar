#!/usr/bin/env python3
"""A stand-in for copier, for the fast tests.

It takes the exact command the scaffold runs (`copy --trust --defaults
--vcs-ref REF --data-file FILE --quiet SRC DST`), reads the answers, and
renders the few template files the scaffold and the tests touch, in the
shape linkml-project-copier v0.5.0 gives them. It skips a destination file
that already exists when the template's `_skip_if_exists` would, so the
pre-seeded files are left alone as the real copier leaves them. Nothing here
needs the network.

A destination file that exists and that `_skip_if_exists` does not cover
fails the run, as the real copier does under --defaults with no terminal
("Interactive session required"), so a pre-seeded file the template would
not leave alone is caught here and not first on a real host. Under --quiet
the real copier prints nothing, and neither does this. It does not apply the
template's answer validators or write the files the scaffold never reads.

FAKE_COPIER_FAIL=1 makes it exit 1 after writing nothing, and
FAKE_COPIER_GIT=1 makes it leave a `.git` directory behind, as `just setup`
would, so the scaffold's refusals can be tested.
"""

import json
import os
import sys
from pathlib import Path

JUSTFILE = """# A stand-in for the template's justfile: the variables the recipes and the
# appended doorway recipe read, and the three recipes the gate names.
set dotenv-load := true
set dotenv-filename := x'${LINKML_ENVIRONMENT_FILENAME:-config.public.mk}'

schema_name := env_var_or_default("LINKML_SCHEMA_NAME", "_no_schema_given_")
source_schema_dir := env_var_or_default("LINKML_SCHEMA_SOURCE_DIR", "")

_default:
    @just --list

install:
    @echo "fake install"

lint:
    @echo "fake lint {{source_schema_dir}}"

test:
    @echo "fake test {{schema_name}}"

import "project.justfile"
"""

PROJECT_JUSTFILE = """## Add your own just recipes here. This is imported by the main justfile.

# Overriding recipes from the root justfile by adding a recipe with the same
# name in this file is not possible until a known issue in just is fixed,
# https://github.com/casey/just/issues/2540
"""

CONFIG_PUBLIC_MK = """# config.public.mk

# This file is public in git. No sensitive info allowed.

###### schema definition variables, used by justfile

# Note:
# - just works fine with quoted variables of dot-env files like this one
LINKML_SCHEMA_NAME="{slug}"
LINKML_SCHEMA_AUTHOR="{author}"
LINKML_SCHEMA_DESCRIPTION="{description}"
LINKML_SCHEMA_SOURCE_DIR="src/{slug}/schema"

###### linkml generator variables, used by justfile

## gen-project configuration file
LINKML_GENERATORS_CONFIG_YAML=config.yaml

## pass args if gendoc ignores config.yaml (i.e. --no-mergeimports)
LINKML_GENERATORS_DOC_ARGS=

## pass args to workaround genowl rdfs config bug (linkml#1453)
LINKML_GENERATORS_OWL_ARGS=

## pass args to pydantic generator which isn't supported by gen-project
LINKML_GENERATORS_PYDANTIC_ARGS=
"""

MKDOCS = """---
site_name: "{name}"
theme:
  name: material
nav:
  - Home: index.md
  - About: about.md
site_url: https://{org}.github.io/{name}
repo_url: https://github.com/{org}/{name}
"""

SKIP_IF_EXISTS = ("LICENSE", "README.md", "docs/index.md", "docs/about.md", "examples/README.md", "tests/test_data.py")
SKIP_PREFIXES = ("project/", "src/{slug}/datamodel/", "src/{slug}/schema/", "tests/data/")


def parse_answers(path):
    answers = {}
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        if not line or line.startswith("#") or ":" not in line:
            continue
        key, _, value = line.partition(":")
        value = value.strip()
        if value in ("true", "false"):
            answers[key.strip()] = value == "true"
        else:
            answers[key.strip()] = json.loads(value) if value.startswith('"') else value
    return answers


def main(argv):
    if os.environ.get("FAKE_COPIER_FAIL") == "1":
        print("fake copier: failing as asked", file=sys.stderr)
        return 1
    if not argv or argv[0] != "copy":
        print(f"fake copier: unexpected command {argv!r}", file=sys.stderr)
        return 2
    args = argv[1:]
    ref = args[args.index("--vcs-ref") + 1]
    answers_file = args[args.index("--data-file") + 1]
    positional = [a for i, a in enumerate(args) if not a.startswith("--") and args[i - 1] not in ("--vcs-ref", "--data-file")]
    src, dst = positional[-2], Path(positional[-1])
    answers = parse_answers(answers_file)
    slug = answers["project_slug"]
    name = answers["project_name"]
    org = answers["github_org"]
    author = f"{answers['full_name']} <{answers['email']}>"
    files = {
        ".copier-answers.yml": "# Changes here will be overwritten by Copier\n"
        + "".join(f"{k}: {json.dumps(v) if isinstance(v, bool) else v}\n" for k, v in sorted({"_commit": ref, "_src_path": src, **answers}.items())),
        "justfile": JUSTFILE,
        "project.justfile": PROJECT_JUSTFILE,
        "config.public.mk": CONFIG_PUBLIC_MK.format(slug=slug, author=author, description=answers["project_description"]),
        "config.yaml": "excludes:\n  - markdown\n",
        "mkdocs.yml": MKDOCS.format(name=name, org=org),
        "pyproject.toml": f'[project]\nname = "{slug}"\nversion = "0.0.0"\n',
        ".gitignore": "project/\n!project/README.md\ntmp/\n.venv\n/site\n",
        ".editorconfig": "root = true\n",
        ".yamllint.yaml": "extends: default\n",
        ".pre-commit-config.yaml": "repos: []\n",
        ".github/dependabot.yml": "version: 2\nupdates: []\n",
        ".github/workflows/main.yaml": "name: Build and test\non: [push]\njobs: {}\n",
        ".github/workflows/deploy-docs.yaml": "name: Deploy docs\non: [push]\njobs: {}\n",
        "CODE_OF_CONDUCT.md": "# Code of conduct\n",
        "CONTRIBUTING.md": "# Contributing\n",
        "README.md": f"# {name}\n\nThe template's README.\n",
        "LICENSE": "The template's license.\n",
        "docs/index.md": "# The template's index\n",
        "docs/about.md": "# The template's about\n",
        "docs/elements/.gitkeep": "",
        "examples/README.md": "# Examples\n",
        "project/README.md": "# Generated\n",
        f"src/{slug}/__init__.py": "",
        f"src/{slug}/_version.py": '__version__ = "0.0.0"\n',
        f"src/{slug}/datamodel/__init__.py": f"from .{slug} import *  # noqa: F403\n",
        f"src/{slug}/schema/README.md": "# Schema Directory\n",
        "src/README.md": "# The model\n",
        "tests/__init__.py": "",
        "tests/data/README.md": "# Example data\n",
        "tests/data/valid/.gitkeep": "",
        "tests/data/invalid/.gitkeep": "",
    }
    skip_prefixes = tuple(p.format(slug=slug) for p in SKIP_PREFIXES)
    for rel, text in files.items():
        target = dst / rel
        if target.exists() and (rel in SKIP_IF_EXISTS or rel.startswith(skip_prefixes)):
            continue
        if target.exists():
            print(f"fake copier: {rel} exists and _skip_if_exists does not cover it; the real copier would ask to overwrite it", file=sys.stderr)
            return 1
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8")
    if os.environ.get("FAKE_COPIER_GIT") == "1":
        (dst / ".git").mkdir(exist_ok=True)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
