#!/usr/bin/env bash
# Repository-contract checks for the linkml-sidecar distribution repository.
# Separate from the Markdown and link checks (validate.yml runs those as their
# own jobs) so failures are easy to diagnose. The behavioural tests of the
# scaffold, the preflight and the workflow are under tests/ and run with
# pytest (tests/conftest.py says how). This script asserts facts about this
# repository's own files: the skills' shape, the links, the budgets, the one
# template pin and every mention of it, the action pins, the prerequisites
# rows, and that no tracked file holds a character a reader cannot see.
set -euo pipefail
# mapfile and declare -A below need bash 4; macOS ships 3.2 (brew install bash).
[ "${BASH_VERSINFO[0]}" -ge 4 ] || { echo "validate-repository.sh needs bash 4 or later; this is $BASH_VERSION" >&2; exit 2; }

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"
sidecar="skills/linkml-sidecar"
templates="$sidecar/templates"
scaffold="$sidecar/scripts/linkml-scaffold.sh"

fail=0
say() { printf '%s\n' "$*"; }
err() { printf 'FAIL: %s\n' "$*" >&2; fail=1; }
ok() { printf 'OK:   %s\n' "$*"; }

# 1. Exactly the intended published skill directories exist. This list is the
#    one place their number is written: checks 1 and 4 count it.
mapfile -t skill_dirs < <(find skills -mindepth 1 -maxdepth 1 -type d | sort)
expected_dirs=("skills/linkml-author" "skills/linkml-sidecar")
if [[ "${skill_dirs[*]}" == "${expected_dirs[*]}" ]]; then
  ok "exactly the ${#expected_dirs[@]} intended skill directories exist (${expected_dirs[*]})"
else
  err "expected skill directories ${expected_dirs[*]}, found ${skill_dirs[*]:-none}"
fi

# 2. Each required SKILL.md exists with the exact case-sensitive filename, and
#    3. its declared name matches its directory.
for dir in "${expected_dirs[@]}"; do
  skill_file="$dir/SKILL.md"
  if [[ ! -f "$skill_file" ]]; then
    err "$skill_file is missing (check exact case: SKILL.md)"
    continue
  fi
  ok "$skill_file exists"
  declared="$(sed -n 's/^name:[[:space:]]*//p' "$skill_file" | sed -n 1p | tr -d '"'"'"'')"
  if [[ "$declared" == "$(basename "$dir")" ]]; then
    ok "$skill_file frontmatter name '$declared' matches directory"
  else
    err "$skill_file frontmatter name '$declared' does not match directory '$(basename "$dir")'"
  fi
done

# 3b. Each skill states what it needs in the spec's optional `compatibility`
#     field (1-500 characters), and
# 3c. each description ends in a `Keywords:` list inside the spec's 1024
#     characters: catalogs have no tag field, so the keywords are the only
#     tag a search reads. The plugin manifest and its marketplace entry
#     carry one keyword list between them, on one line each.
for dir in "${expected_dirs[@]}"; do
  skill_file="$dir/SKILL.md"
  [[ -f "$skill_file" ]] || continue
  compat="$(awk 'NR>1 && /^---$/ {exit} /^compatibility:/ {sub(/^compatibility:[[:space:]]*/, ""); print}' "$skill_file")"
  if [[ -z "$compat" ]]; then
    err "$skill_file declares no compatibility field"
  elif (( ${#compat} > 500 )); then
    err "$skill_file compatibility is ${#compat} characters; the Agent Skills spec allows 500"
  else
    ok "$skill_file declares compatibility (${#compat} characters)"
  fi
  desc="$(awk 'NR>1 && /^---$/ {exit} /^description:/ {sub(/^description:[[:space:]]*/, ""); print}' "$skill_file")"
  if (( ${#desc} > 1024 )); then
    err "$skill_file description is ${#desc} characters; the Agent Skills spec allows 1024"
  elif ! grep -qE ' Keywords: [^.]+\.'"'"'?$' <<<"$desc"; then
    err "$skill_file description does not end in a 'Keywords: a, b, c.' list"
  else
    ok "$skill_file description ends in a Keywords list (${#desc} characters)"
  fi
done
plugin_kw="$(grep '"keywords"' .claude-plugin/plugin.json 2>/dev/null | sed 's/^ *//' || true)"
market_kw="$(grep '"keywords"' .claude-plugin/marketplace.json 2>/dev/null | sed 's/^ *//' || true)"
if [[ -z "$plugin_kw" || -z "$market_kw" ]]; then
  err ".claude-plugin/plugin.json or marketplace.json is missing, or has no one-line keywords array"
elif [[ "$plugin_kw" == "$market_kw" ]]; then
  ok "plugin.json and marketplace.json carry the same keywords"
else
  err ".claude-plugin/plugin.json and marketplace.json list different keywords"
fi

# 4. No duplicate SKILL.md under skills/, and none under templates/, where an
#    installer would list it as a skill.
mapfile -t all_skill_md < <(find skills -iname 'SKILL.md' | sort)
if [[ ${#all_skill_md[@]} -eq ${#expected_dirs[@]} ]]; then
  ok "no duplicate SKILL.md files under skills/"
else
  err "expected exactly ${#expected_dirs[@]} SKILL.md files under skills/, found ${#all_skill_md[@]}: ${all_skill_md[*]}"
fi
if [[ -n "$(find "$templates" -iname 'SKILL.md' 2>/dev/null)" ]]; then
  err "a SKILL.md sits under $templates"
else
  ok "no SKILL.md under $templates"
fi

# 5. Relative references resolve from each linking file's own directory,
#    which is how an installer copies one skill subtree at a time. Files
#    under templates/ are rendered into a host, where their links resolve
#    (docs/index.md links the elements gen-doc writes), so they are skipped.
say ""
say "Checking relative link targets..."
broken=0
while IFS= read -r file; do
  while IFS=: read -r line match; do
    link="${match#\](}"
    link="${link%)}"
    [[ "$link" =~ ^https?:// ]] && continue
    [[ "$link" =~ ^# ]] && continue
    link="${link%%#*}"
    [[ -z "$link" ]] && continue
    target="$(dirname "$file")/$link"
    if [[ ! -e "$target" ]]; then
      err "$file:$line: broken relative link '$link' (resolved: $target)"
      broken=1
    fi
  done < <(awk 'BEGIN{f=0} /^[[:space:]]*```/{f=!f; print ""; next} {print (f ? "" : $0)}' "$file" \
             | grep -noE '\]\(([^)]+)\)' || true)
done < <(find skills README.md CONTRIBUTING.md CHANGELOG.md AI_COVENANT.md CODE_OF_CONDUCT.md .github/pull_request_template.md -name '*.md' -not -path '*/templates/*' | sort)
[[ "$broken" -eq 0 ]] && ok "all relative Markdown links under skills/ and the root pages resolve (fenced examples ignored; templates/ render into a host)"

# 6. Shell scripts pass ShellCheck, and Python scripts compile.
say ""
say "Linting scripts..."
mapfile -t shell_scripts < <(find skills scripts -type f -name '*.sh' | sort)
if command -v shellcheck >/dev/null 2>&1; then
  for s in "${shell_scripts[@]}"; do
    if shellcheck "$s"; then ok "shellcheck clean: $s"; else err "shellcheck failed: $s"; fi
  done
else
  say "shellcheck not installed locally - CI runs it; skipping here (${#shell_scripts[@]} script(s))"
fi
# A Python template under templates/ holds placeholder tokens until it is
# rendered into a host, and the tests compile the rendered form.
mapfile -t py_scripts < <(find skills tests -type f -name '*.py' -not -path '*/.venv/*' -not -path '*/templates/*' | sort)
# ast.parse rather than py_compile, which would write __pycache__ as a side effect.
if command -v python3 >/dev/null 2>&1; then
  for p in "${py_scripts[@]}"; do
    if python3 -c 'import ast, sys; ast.parse(open(sys.argv[1], encoding="utf-8").read(), sys.argv[1])' "$p"; then ok "parses: $p"; else err "does not parse: $p"; fi
  done
fi

# 7. Word budgets. An agent loads the whole SKILL.md when the skill starts;
#    the detail a step needs goes in references/. CONTRIBUTING.md is a
#    checklist, not a design log.
say ""
say "Checking word budgets..."
declare -A skill_budget=(
  [skills/linkml-sidecar]=3500
  [skills/linkml-author]=3500
)
for dir in "${expected_dirs[@]}"; do
  file="$dir/SKILL.md"
  budget="${skill_budget[$dir]:-}"
  if [[ -z "$budget" ]]; then err "$file has no word budget in check 7"; continue; fi
  words="$(wc -w < "$file")"
  if (( words <= budget )); then ok "$file is $words words (budget $budget)"; else err "$file is $words words; the budget is $budget - move detail into $dir/references/"; fi
done
words="$(wc -w < CONTRIBUTING.md)"
if (( words <= 1000 )); then ok "CONTRIBUTING.md is $words words (budget 1000)"; else err "CONTRIBUTING.md is $words words; the budget is 1000"; fi

# 8. The one template pin. The scaffold driver holds LINKML_TEMPLATE_REF and
#    LINKML_TEMPLATE_SHA; every mention of a linkml-project-copier version
#    under skills/, README.md and CHANGELOG.md's [Unreleased] names the same
#    tag, and the catalogue's heading is for that version.
say ""
say "Checking the template pin..."
pin="$(grep -oE 'LINKML_TEMPLATE_REF:=v[0-9]+\.[0-9]+\.[0-9]+' "$scaffold" | head -1 | sed 's/.*:=//')"
pin_sha="$(grep -oE 'LINKML_TEMPLATE_SHA:=[0-9a-f]{40}' "$scaffold" | head -1 | sed 's/.*:=//')"
if [[ -z "$pin" || -z "$pin_sha" ]]; then
  err "$scaffold holds no LINKML_TEMPLATE_REF/LINKML_TEMPLATE_SHA pin"
else
  ok "the scaffold pins linkml-project-copier $pin (${pin_sha:0:12})"
  stray="$(grep -rnoE 'linkml-project-copier[^v]{0,40}v[0-9]+\.[0-9]+\.[0-9]+|v[0-9]+\.[0-9]+\.[0-9]+[^v]{0,40}linkml-project-copier' skills README.md | grep -v -- "$pin" || true)"
  if [[ -n "$stray" ]]; then err "a page names another template version than the pin $pin: $stray"; else ok "every mention of the template's version under skills/ and README.md is $pin"; fi
  if grep -qE "at template \*\*$pin\*\*|tag \*\*$pin\*\*" "$sidecar/SKILL.md" "$sidecar/references/template-assumptions.md"; then
    ok "SKILL.md and the catalogue name the pin $pin"
  else
    err "SKILL.md's Sources note or template-assumptions.md's intro does not name the pin $pin in bold"
  fi
  if grep -qE "^_commit: $pin\$|_commit: $pin" "$sidecar/SKILL.md"; then ok "Step 3 checks _commit against $pin"; else err "SKILL.md Step 3 does not check _commit: $pin"; fi
fi

# 9. Every action in the workflow template and this repository's own
#    workflows is pinned to a commit, with the version in a comment.
say ""
say "Checking action pins..."
if grep -rnE '^\s*-?\s*uses:' .github/workflows/ "$templates/github/" \
  | grep -vE 'uses:\s*[^@ ]+@([0-9a-f]{40}|sha256:[0-9a-f]{64})\b' \
  | grep -vE 'uses:\s*\./'; then
  err "the action(s) above are not pinned to a commit SHA"
else
  ok "every action in .github/workflows/ and $templates/github/ is pinned to a commit"
fi
# Dependabot bumps .github/workflows/ and never the template hosts copy, so an
# action both use must carry the same commit in both, or the bump fails here
# until the template follows (CONTRIBUTING.md says to bump them together).
shared_drift=0
while IFS= read -r action; do
  own="$(grep -rhoE "uses:\s*$action@[^ ]+" .github/workflows/ | sed 's/.*@//' | sort -u || true)"
  theirs="$(grep -hoE "uses:\s*$action@[^ ]+" "$templates/github/linkml-sidecar.yaml" | sed 's/.*@//' | sort -u || true)"
  if [[ -n "$own" && "$own" != "$theirs" ]]; then
    err "$action is pinned to $own in .github/workflows/ and to $theirs in $templates/github/linkml-sidecar.yaml; bump both together"
    shared_drift=1
  fi
done < <(grep -hoE 'uses:\s*[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+@' "$templates/github/linkml-sidecar.yaml" | sed -E 's/uses:\s*//; s/@$//' | sort -u)
[[ "$shared_drift" -eq 0 ]] && ok "every action the template shares with .github/workflows/ is pinned to the same commit in both"

# 10. Every line the preflight can print as missing or a warning has a row on
#     the prerequisites page, so a person can be told who fixes it.
say ""
say "Checking prerequisites rows..."
mapfile -t keys < <(grep -oE '\b(miss|warn) [a-z]+ ' "$templates/scripts/linkml-preflight.sh" | awk '{print $2}' | sort -u)
for key in "${keys[@]}"; do
  if grep -qE "^\| \`$key\` \|" "$sidecar/references/prerequisites.md"; then
    ok "prerequisites.md has a row for the preflight's '$key' line"
  else
    err "prerequisites.md has no row for the preflight's '$key' line"
  fi
done

# 11. CHANGELOG.md never carries two headings for one released version.
mapfile -t headings < <(grep -oE '^## \[[0-9]+\.[0-9]+\.[0-9]+\]' CHANGELOG.md || true)
dupes="$(printf '%s\n' "${headings[@]}" | sort | uniq -d)"
if [[ -z "$dupes" ]]; then ok "every released version in CHANGELOG.md has exactly one heading"; else err "CHANGELOG.md has more than one heading for: $dupes"; fi

# 12. No tracked file holds a character a reader cannot see: a control
#     character other than a tab or a line's closing carriage return, or a
#     format character such as a zero-width space, a byte order mark or the
#     right-to-left override the "Trojan Source" attack (CVE-2021-42574)
#     hides code behind. Code that needs one spells it as an escape.
say ""
say "Searching tracked files for characters a reader cannot see..."
read -r -d '' unseen_py <<'PY' || true
import sys, unicodedata
hits = 0
for raw in sys.stdin.buffer.read().split(b"\0"):
    try:
        with open(raw, "rb") as handle:
            data = handle.read()
    except OSError:
        continue
    if b"\0" in data[:8000]:
        continue
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError:
        continue
    for number, line in enumerate(text.split("\n"), start=1):
        for char in sorted(set(line[:-1] if line.endswith("\r") else line)):
            kind = unicodedata.category(char)
            if kind == "Cf" or (kind == "Cc" and char != "\t"):
                hits += 1
                print(f"{raw.decode('utf-8', 'replace')}:{number}: U+{ord(char):04X} {unicodedata.name(char, '')}".rstrip())
sys.exit(1 if hits else 0)
PY
if command -v python3 >/dev/null 2>&1; then
  unseen_run=(python3 -c "$unseen_py")
elif command -v uv >/dev/null 2>&1; then
  unseen_run=(uv run --quiet --no-project python -c "$unseen_py")
else
  unseen_run=(false)
  err "neither python3 nor uv is on PATH, so no tracked file was searched for characters a reader cannot see"
fi
if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  listing=(git ls-files -z)
else
  listing=(find . -path ./.git -prune -o -path ./.template-cache -prune -o -type f -print0)
fi
if unseen_out="$("${listing[@]}" | "${unseen_run[@]}" 2>&1)"; then
  ok "no tracked file holds a character a reader cannot see"
else
  err "these lines hold a character a reader cannot see; delete it, or spell it as an escape in code: $unseen_out"
fi
unseen_dir="$(mktemp -d)"
printf 'echo ok # a\xe2\x80\xaeb\n' > "$unseen_dir/planted.sh"
if printf '%s\0' "$unseen_dir/planted.sh" | "${unseen_run[@]}" >/dev/null 2>&1; then
  err "the search missed a right-to-left override planted in a script"
else
  ok "the search finds a right-to-left override planted in a script"
fi
rm -rf "${unseen_dir:?}"

# 13. The lokf fixture's justfile is ktl-sidecar's template, rendered, so the
#     scaffold's exact-line edits are tested against the lines a real host
#     has. Compared only when a knowledge-trust-ladder clone is named.
if [[ -n "${KTL_REPO:-}" && -f "$KTL_REPO/skills/ktl-sidecar/templates/justfile" ]]; then
  if cmp -s <(sed 's/<PROJ_NAME>/Fixture/g' "$KTL_REPO/skills/ktl-sidecar/templates/justfile") tests/fixtures/lokf/justfile; then
    ok "tests/fixtures/lokf/justfile matches ktl-sidecar's justfile template"
  else
    err "tests/fixtures/lokf/justfile differs from ktl-sidecar's justfile template at $KTL_REPO - re-render the fixture, and check the scaffold's exact-line edits still match"
  fi
else
  say "KTL_REPO not set - the lokf fixture is not compared with ktl-sidecar's template"
fi

say ""
if [[ "$fail" -eq 0 ]]; then
  say "Repository contract: PASS"
  exit 0
else
  say "Repository contract: FAIL"
  exit 1
fi
