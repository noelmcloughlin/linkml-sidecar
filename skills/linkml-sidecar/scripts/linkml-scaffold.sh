#!/usr/bin/env bash
# linkml-scaffold.sh: Steps 1 to 3 of linkml-sidecar as one deterministic run.
# It pre-seeds the files the skill owns, runs copier for everything else,
# neutralises the template's root-install assumptions, names the schema in
# a KTL bundle's justfile when one is present, adds the root pointers, and
# prints the hand-off facts. Nothing in it is a judgement: the facts come
# in as environment variables that the skill's Step 0 resolved from real
# sources.
#
# This file holds the one pin of the template. The contract script holds
# every other mention under skills/ and README.md to these two values, and
# the Python half verifies the tag still names this commit before it trusts
# the template with `--trust`.
#
# The Python half runs through `uv run` first, which reads the half's own
# header and so passes over a python3 older than 3.8, such as RHEL 8's 3.6.
# Then it runs through python3, and through python as the last resort, each
# only when it is 3.8 or later. The half needs only the standard library, so
# its header names no package for a mirror to refuse.
#
# Usage: linkml-scaffold.sh [--dry-run] [--host DIR] [--mode plain|lokf|auto]
#                           [--gitignored] [--adopt SCHEMA | --dummy]
#                           [--pointers-only] [--repair PATH]
#   --repair generators.yaml moves a finished project's config.yaml to
#   .linkml/generators.yaml; a new sidecar is given that name without asking.
#   Facts (environment): PROJ_NAME PROJ_SLUG PROJ_DESC GITHUB_ORG REPO_URL
#   FULL_NAME EMAIL LICENSE_ID SCHEMA_ID DOCS_URL [COPYRIGHT_YEAR] [TODAY]
#   [BASE_IRI, read from .lokf/knowledge/index.md when absent]
#   With --adopt, PROJ_SLUG and SCHEMA_ID come from the schema file itself.
#   Overrides: LINKML_TEMPLATE_SRC (a URL or a local clone), LINKML_COPIER
#   (the copier command to run instead of uvx), LINKML_TEMPLATE_SKIP_PIN_CHECK=1.
# Exit: 0 done; 2 usage or a missing tool; 3 refused (a project, a schema or
#       a file already there stands in the way); 4 copier failed; 5 an
#       overlay or pointer failed. Nothing but its own staging directory is
#       ever removed.
[ -n "${BASH_VERSION:-}" ] || { echo "run this with bash: bash ${0##*/} [options]" >&2; exit 2; }
set -euo pipefail

here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
: "${LINKML_TEMPLATE_SRC:=gh:linkml/linkml-project-copier}"
: "${LINKML_TEMPLATE_REF:=v0.5.0}"
: "${LINKML_TEMPLATE_SHA:=1d52a14e42db05ae0a3bff03350309dae437c531}"
export LINKML_TEMPLATE_SRC LINKML_TEMPLATE_REF LINKML_TEMPLATE_SHA

usable() { command -v "$1" >/dev/null 2>&1 && "$1" -c 'import sys; assert sys.version_info >= (3, 8)' >/dev/null 2>&1; }
if command -v uv >/dev/null 2>&1; then
  exec uv run --quiet "$here/linkml-scaffold.py" "$@"
elif usable python3; then
  exec python3 "$here/linkml-scaffold.py" "$@"
elif usable python; then
  exec python "$here/linkml-scaffold.py" "$@"
fi
echo "linkml-scaffold.sh: needs uv, or python3 3.8 or later; install uv (docs.astral.sh/uv) and run again" >&2
exit 2
