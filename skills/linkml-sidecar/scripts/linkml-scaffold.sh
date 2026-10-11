#!/usr/bin/env bash
# linkml-scaffold.sh: Steps 1 to 3 of linkml-sidecar as one deterministic run.
# It pre-seeds the files the skill owns, runs copier for everything else,
# neutralises the template's root-install assumptions, wires a KTL bundle
# when one is present, adds the root pointers, and prints the hand-off
# facts. Nothing in it is a judgement: the facts come in as environment
# variables that the skill's Step 0 resolved from real sources.
#
# This file holds the one pin of the template. The contract script holds
# every other mention under skills/ and README.md to these two values, and
# the Python half verifies the tag still names this commit before it trusts
# the template with `--trust`.
#
# Usage: linkml-scaffold.sh [--dry-run] [--host DIR] [--mode plain|lokf|auto]
#                           [--gitignored] [--pointers-only] [--repair PATH]
#   Facts (environment): PROJ_NAME PROJ_SLUG PROJ_DESC GITHUB_ORG REPO_URL
#   FULL_NAME EMAIL LICENSE_ID SCHEMA_ID DOCS_URL [COPYRIGHT_YEAR] [TODAY]
#   [BASE_IRI, read from .lokf/knowledge/index.md when absent]
#   Overrides: LINKML_TEMPLATE_SRC (a URL or a local clone), LINKML_COPIER
#   (the copier command to run instead of uvx), LINKML_TEMPLATE_SKIP_PIN_CHECK=1.
# Exit: 0 done; 2 usage or a missing tool; 3 refused (a sidecar exists);
#       4 copier failed; 5 an overlay or pointer failed.
[ -n "${BASH_VERSION:-}" ] || { echo "run this with bash: bash ${0##*/} [options]" >&2; exit 2; }
set -euo pipefail

here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
: "${LINKML_TEMPLATE_SRC:=gh:linkml/linkml-project-copier}"
: "${LINKML_TEMPLATE_REF:=v0.5.0}"
: "${LINKML_TEMPLATE_SHA:=1d52a14e42db05ae0a3bff03350309dae437c531}"
export LINKML_TEMPLATE_SRC LINKML_TEMPLATE_REF LINKML_TEMPLATE_SHA

if command -v python3 >/dev/null 2>&1; then
  exec python3 "$here/linkml-scaffold.py" "$@"
elif command -v uv >/dev/null 2>&1; then
  exec uv run --quiet --no-project python "$here/linkml-scaffold.py" "$@"
else
  echo "linkml-scaffold.sh: neither python3 nor uv is on PATH; install uv (docs.astral.sh/uv) and run again" >&2
  exit 2
fi
