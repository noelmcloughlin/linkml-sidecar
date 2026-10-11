#!/usr/bin/env bash
# Isolated install smoke test. Installs the two skills into a throwaway
# "consumer" repo via the open skills CLI, so generated agent directories
# never contaminate this distribution source, then runs the installed
# preflight and the installed scaffold's dry run from where the installer
# put them.
#
# Usage:
#   scripts/smoke-test-install.sh                  # source = git origin remote
#   scripts/smoke-test-install.sh /path/to/local    # source = local path (pre-push)
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
source_arg="${1:-}"

if [[ -z "$source_arg" ]]; then
  source_arg="$(git -C "$repo_root" remote get-url origin 2>/dev/null || true)"
  if [[ -z "$source_arg" ]]; then
    echo "No source given and no git origin remote configured on $repo_root." >&2
    echo "Pass a local path or push the repo and set an origin remote first." >&2
    exit 1
  fi
fi

if ! command -v npx >/dev/null 2>&1; then
  echo "npx not found - install Node.js to run this smoke test." >&2
  exit 1
fi

test_root="$(mktemp -d)"
trap 'rm -rf "$test_root"' EXIT

echo "Source:    $source_arg"
echo "Test root: $test_root"

mkdir -p "$test_root/consumer"
(
  cd "$test_root/consumer"
  git init -q
  npx --yes skills add "$source_arg" --skill linkml-sidecar --skill linkml-author --yes
)

echo ""
echo "Assertions:"
fail=0
assert() {
  local description="$1"
  local check="$2"
  if eval "$check"; then
    echo "OK:   $description"
  else
    echo "FAIL: $description"
    fail=1
  fi
}

sidecar_dir="$(find "$test_root/consumer" \( -path "*.agents/skills/linkml-sidecar" -o -path "*.claude/skills/linkml-sidecar" \) -type d 2>/dev/null | head -1)"
author_dir="$(find "$test_root/consumer" \( -path "*.agents/skills/linkml-author" -o -path "*.claude/skills/linkml-author" \) -type d 2>/dev/null | head -1)"
assert "linkml-sidecar discovered by name" "[[ -n \"$sidecar_dir\" && -f \"$sidecar_dir/SKILL.md\" ]]"
assert "linkml-author discovered by name" "[[ -n \"$author_dir\" && -f \"$author_dir/SKILL.md\" ]]"
assert "linkml-sidecar templates/, scripts/ and references/ carried along" \
  "[[ -f \"$sidecar_dir/templates/answers.yml\" && -f \"$sidecar_dir/scripts/linkml-scaffold.sh\" && -f \"$sidecar_dir/references/template-assumptions.md\" ]]"
assert "linkml-author references/ carried along" "[[ -f \"$author_dir/references/metamodel.md\" ]]"
assert "the installed preflight runs on the consumer and ends on its summary line" \
  "bash \"$sidecar_dir/templates/scripts/linkml-preflight.sh\" \"$test_root/consumer\" | grep -q '^Preflight: '"
printf '# Consumer\n\nA consumer.\n\n## Usage\n' > "$test_root/consumer/README.md"
cp "$repo_root/LICENSE" "$test_root/consumer/LICENSE"
assert "the installed scaffold's dry run plans a sidecar from where the installer put it" \
  "(cd \"$test_root/consumer\" && PROJ_NAME=consumer PROJ_DESC='A consumer.' GITHUB_ORG=acme REPO_URL=https://github.com/acme/consumer FULL_NAME='Smoke Test' EMAIL=smoke@example.invalid LICENSE_ID=Apache-2.0 SCHEMA_ID=https://w3id.org/acme/consumer DOCS_URL=https://acme.github.io/consumer/linkml/ LINKML_TEMPLATE_SKIP_PIN_CHECK=1 bash \"$sidecar_dir/scripts/linkml-scaffold.sh\" --dry-run | grep -q '^next: just')"
assert "no installer metadata leaked back into this source repo" \
  "[[ -z \"\$(git -C \"\$repo_root\" status --porcelain --untracked-files=all -- .agents .claude skills-lock.json 2>/dev/null)\" ]]"

echo ""
if [[ "$fail" -eq 0 ]]; then
  echo "Smoke test: PASS"
else
  echo "Smoke test: FAIL"
  exit 1
fi
