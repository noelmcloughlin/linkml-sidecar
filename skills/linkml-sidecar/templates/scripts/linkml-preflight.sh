#!/usr/bin/env bash
# What this host can and cannot do for the LinkML sidecar skills: one
# read-only screen, no project needed. linkml-sidecar runs it first (Step 0)
# and repeats its summary line in the hand-off; linkml-author runs the copy
# the sidecar installed under .linkml/scripts/ to find the project. A missing
# tool disables a step out loud instead of being discovered after the
# scaffold has run.
#
# Each line is `ok`, `warn`, `missing` or `info`, then one summary line:
#   Preflight: <n> missing, <m> warning(s). Missing disables: <steps>.
# Exit 0 always: the skills read the lines; nothing here is a gate.
#
# Bash 3.2 and POSIX tools only, so it runs on macOS's stock bash and on Git
# for Windows. From PowerShell, run it through Git for Windows' bash: the
# one-liner is in linkml-sidecar/references/portability.md.
#
# Usage: linkml-preflight.sh [repo-root]   (default: the nearest ancestor of
# the current directory holding `.linkml/`, `.lokf/` or `.git`, else the
# current directory)
[ -n "${BASH_VERSION:-}" ] || { echo "run this with bash: bash ${0##*/} [repo-root]" >&2; exit 2; }
set -u

missing=0; warns=0; disables=""
line() { printf '%-8s%-11s%s\n' "$1" "$2" "$3"; }
ok()   { line ok "$1" "$2"; }
info() { line info "$1" "$2"; }
warn() { line warn "$1" "$2"; warns=$((warns + 1)); }
miss() { line missing "$1" "$2"; missing=$((missing + 1)); [ -n "${3:-}" ] && disables="${disables}${disables:+; }$3"; }
have() { command -v "$1" >/dev/null 2>&1; }
# One value out of a `KEY="value"` or `KEY=value` line of config.public.mk.
mkvalue() { sed -n "s/^$2=//p" "$1" 2>/dev/null | head -n 1 | sed -e 's/^"//' -e 's/"$//'; }

# ---- root ------------------------------------------------------------------
root="${1:-}"
if [ -z "$root" ]; then
  d="$(pwd -P)"; root="$d"
  while [ "$d" != "/" ]; do
    if [ -d "$d/.linkml" ] || [ -d "$d/.lokf" ] || [ -d "$d/.git" ]; then root="$d"; break; fi
    d="$(dirname "$d")"
  done
fi
root="$(cd "$root" 2>/dev/null && pwd -P)" || { echo "no such directory: ${1:-.}" >&2; exit 2; }

# ---- host ------------------------------------------------------------------
os="$(uname -s 2>/dev/null || echo unknown)"
case "$os" in
  Linux) host=Linux ;;
  Darwin) host=macOS ;;
  MINGW*|MSYS*|CYGWIN*) host="Windows (Git for Windows bash)" ;;
  *) host="$os" ;;
esac
if have python3; then py="python3 $(python3 --version 2>&1 | sed 's/^Python //')"; else py="none (uv run python stands in)"; fi
printf 'Preflight for %s\n' "$root"
ok host "$host, bash ${BASH_VERSION%%(*}; python: $py"
case "$root" in
  *OneDrive*|*Dropbox*|*iCloud*|*"Google Drive"*|*GoogleDrive*|*Nextcloud*)
    info sync "synced folder: the linkml_schema link is per machine, and .venv/ should be excluded from the sync" ;;
esac

# ---- git -------------------------------------------------------------------
ingit=0; tracked=""; forge=none; remote=""
if have git && git -C "$root" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  ingit=1
  if [ -n "$(git -C "$root" ls-files .linkml 2>/dev/null | head -n 1)" ]; then tracked="tracked"
  elif git -C "$root" check-ignore -q .linkml 2>/dev/null; then tracked="gitignored (no workflow, no pull requests for the schema)"
  elif [ -d "$root/.linkml" ]; then tracked="not yet committed"
  else tracked="not present"; fi
  remote="$(git -C "$root" remote get-url origin 2>/dev/null || true)"
  case "$remote" in
    *github*) forge=github ;;
    *gitlab*) forge=gitlab ;;
    *codeberg*|*forgejo*|*gitea*) forge=forgejo ;;
    *bitbucket*) forge=bitbucket ;;
    "") forge=none ;;
    *) forge=other ;;
  esac
  ok git ".linkml/ $tracked; forge $forge${remote:+ ($remote)}"
  toplevel="$(git -C "$root" rev-parse --show-toplevel 2>/dev/null || true)"
  [ -n "$toplevel" ] && [ "$toplevel" != "$root" ] && warn git "this directory is inside the repository at $toplevel; the sidecar belongs at the repository root"
else
  info git "no git: copier update, the workflow and pull requests do not apply; the host's own history is the record"
fi

# ---- tooling ---------------------------------------------------------------
if have uv; then
  ok uv "uv $(uv --version 2>/dev/null | sed 's/^uv //')"
  pyfound="$(uv python find '>=3.10' 2>/dev/null || true)"
  if [ -n "$pyfound" ]; then ok python "$pyfound satisfies the project's >=3.10"
  else miss python "uv finds no Python >=3.10 - uv python install 3.12" "Step 4 (install, lint, test)"; fi
  if [ -f "$root/.python-version" ]; then
    pinned="$(head -n 1 "$root/.python-version" | tr -d ' \r')"
    case "$pinned" in
      2.*|3.[0-9]|3.[0-9].*) warn python "root .python-version pins $pinned; uv reads it inside .linkml/ too, and the project needs >=3.10" ;;
    esac
  fi
  copier_cmd="uvx --from copier>=9.4.0,<10 --with jinja2-time copier"
  if cv="$( (${copier_cmd} --version) 2>/dev/null | head -n 1)" && [ -n "$cv" ]; then
    ok copier "$cv through uvx, with jinja2-time (the template needs both)"
  else
    miss copier "uvx cannot run copier (offline, or a uv cache problem) - try: $copier_cmd --version" "Step 1 (the scaffold)"
  fi
  if have just; then ok just "just $(just --version 2>/dev/null | sed 's/^just //')"
  else info just "just not installed - uvx --from rust-just just works the same, and so does uv tool install rust-just"; fi
else
  miss uv "uv not installed (docs.astral.sh/uv) - copier, just, the project's Python and every generator run through it" "Steps 1, 4 and 5"
fi

# ---- sidecar ---------------------------------------------------------------
sidecar=""
if [ -f "$root/.linkml/.copier-answers.yml" ]; then
  sidecar="$root/.linkml"
  commit="$(sed -n 's/^_commit: *//p' "$root/.linkml/.copier-answers.yml" | head -n 1)"
  src="$(sed -n 's/^_src_path: *//p' "$root/.linkml/.copier-answers.yml" | head -n 1)"
  ok sidecar ".linkml/ from ${src:-?} at ${commit:-?}; linkml-author works here; just --justfile .linkml/justfile update moves the template"
  [ -e "$root/.linkml/.git" ] && warn sidecar ".linkml/.git exists: a nested repository, which just setup creates - remove it (rm -rf .linkml/.git) so the host repository holds the sidecar"
elif [ -d "$root/.linkml" ]; then
  warn sidecar ".linkml/ exists but holds no .copier-answers.yml - a half-made sidecar; linkml-sidecar repairs or replaces it"
elif [ -f "$root/linkml/.copier-answers.yml" ]; then
  sidecar="$root/linkml"
  info sidecar "a visible linkml/ sidecar exists (hand-made shape); linkml-sidecar leaves it alone, linkml-author works in it"
elif [ -f "$root/.copier-answers.yml" ]; then
  sidecar="$root"
  info sidecar "this repository is itself a copier project; no sidecar applies, linkml-author works at the root"
else
  miss sidecar "no .linkml/ under $root - run linkml-sidecar first" "linkml-author, and linkml-sidecar Steps 2 to 5 until Step 1 has run"
fi

# ---- project ---------------------------------------------------------------
# The project directory as a person reads it: relative to the root, or empty when it is the root.
sdisp="${sidecar#"$root"}"; sdisp="${sdisp#/}"; sdisp="${sdisp:+$sdisp/}"
if [ -n "$sidecar" ] && [ -f "$sidecar/config.public.mk" ]; then
  name="$(mkvalue "$sidecar/config.public.mk" LINKML_SCHEMA_NAME)"
  srcdir="$(mkvalue "$sidecar/config.public.mk" LINKML_SCHEMA_SOURCE_DIR)"
  schema="$srcdir/$name.yaml"
  venv="no .venv (just install)"; [ -d "$sidecar/.venv" ] && venv=".venv present"
  if [ -f "$sidecar/$schema" ]; then ok project "schema $sdisp$schema; $venv"
  else warn project "config.public.mk names $schema but it is not there - the schema file is the one thing linkml-author needs"; fi
  if [ "$ingit" -eq 1 ] && [ "$tracked" = tracked ] && [ -f "$root/.github/workflows/linkml-sidecar.yaml" ] \
     && [ -z "$(git -C "$root" ls-files .linkml/uv.lock 2>/dev/null | head -n 1)" ]; then
    warn project ".linkml/uv.lock is not in git - the workflow installs with uv sync --locked and fails without it; run just --justfile .linkml/justfile install and commit the file"
  fi
  inert=0
  for f in "$sidecar"/.github/workflows/*.yaml "$sidecar"/.github/workflows/*.yml "$sidecar"/.github/dependabot.yml "$sidecar"/.pre-commit-config.yaml; do
    [ -f "$f" ] && inert=$((inert + 1))
  done
  [ "$inert" -gt 0 ] && [ "$sidecar" != "$root" ] && info nested "$inert file(s) under $sdisp.github/ and .pre-commit-config.yaml are inert there (GitHub and pre-commit read the root only); the hoisted workflow is .github/workflows/linkml-sidecar.yaml"
elif [ -n "$sidecar" ]; then
  warn project "${sdisp}config.public.mk missing - just cannot find the schema name; linkml-sidecar repair, or copier update, lays it down"
fi

# ---- doorway ---------------------------------------------------------------
door="$root/linkml_schema"
if [ -L "$door" ]; then ok doorway "linkml_schema -> $(readlink "$door")"
elif [ -d "$door" ]; then ok doorway "linkml_schema is a folder or junction"
elif [ -d "$root/.linkml" ]; then
  slug="${name:-<slug>}"
  info doorway "no linkml_schema doorway (ln -s .linkml/src/$slug/schema linkml_schema, just --justfile .linkml/justfile linkml-link, or mklink /J on Windows)"
fi

# ---- KTL -------------------------------------------------------------------
if [ -d "$root/.lokf" ]; then
  floor="$(sed -n 's/.*"lokf\[build\]>=\([0-9.]*\)".*/\1/p' "$root/.lokf/pyproject.toml" 2>/dev/null | head -n 1)"
  pinned="absent (the scaffold copies it out of the installed toolkit)"; [ -f "$root/.lokf/lokf.yaml" ] && pinned="pinned"
  wired="not wired"; grep -q '^schema := ' "$root/.lokf/justfile" 2>/dev/null && wired="wired ($(sed -n 's/^schema := //p' "$root/.lokf/justfile" | head -n 1))"
  base="$(sed -n 's/^base_iri: *//p' "$root/.lokf/knowledge/index.md" 2>/dev/null | head -n 1)"
  ok lokf "KTL bundle present: with-KTL mode; lokf floor >=${floor:-?}; .lokf/lokf.yaml $pinned; .lokf/justfile schema $wired; base_iri ${base:-unknown}"
  [ -z "$base" ] && warn lokf "no base_iri in .lokf/knowledge/index.md - the dummy concept's id needs it (BASE_IRI)"
else
  info lokf "no .lokf/: plain mode; a KTL bundle can be added later and the schema wired to it (references/ktl.md)"
fi

# ---- root pointers, docs and workflows --------------------------------------
if [ -f "$root/.gitignore" ] && grep -qE '^\.linkml/?$' "$root/.gitignore"; then
  info gitignore "root .gitignore names .linkml: gitignored mode (no commit, no workflow)"
fi
pages=""
if [ "$ingit" -eq 1 ]; then
  git -C "$root" show-ref --quiet refs/heads/gh-pages 2>/dev/null && pages="a local gh-pages branch"
  git -C "$root" show-ref --quiet refs/remotes/origin/gh-pages 2>/dev/null && pages="${pages:-}${pages:+ and }origin/gh-pages"
fi
if [ -d "$root/.github/workflows" ] && grep -lsqE 'gh-pages|deploy-pages|mkdocs gh-deploy' "$root"/.github/workflows/*.y*ml 2>/dev/null; then
  pages="${pages:-}${pages:+ and }a workflow that publishes Pages"
fi
if [ -n "$pages" ]; then
  warn pages "the host already publishes Pages ($pages) - never run just deploy from .linkml/; the Step 5 docs job publishes under the linkml/ subpath only"
fi
if [ -d "$root/.github/workflows" ]; then
  if [ -f "$root/.github/workflows/linkml-sidecar.yaml" ]; then
    if grep -q 'working-directory: .linkml' "$root/.github/workflows/linkml-sidecar.yaml"; then ok workflows "linkml-sidecar.yaml present"
    else warn workflows "a linkml-sidecar.yaml exists that is not the sidecar's hoisted workflow - rename one of them"; fi
  else
    n="$(find "$root/.github/workflows" -maxdepth 1 -name '*.y*ml' | wc -l | tr -d ' ')"
    info workflows "$n workflow(s), none for the sidecar (Step 5 lays down linkml-sidecar.yaml)"
  fi
fi
if [ -f "$root/pyproject.toml" ] && grep -q '^\[tool.uv.workspace\]' "$root/pyproject.toml"; then
  warn workspace "the root pyproject.toml declares a uv workspace; .linkml/ is not a member and uv sync inside it is untested (references/template-assumptions.md)"
fi

# ---- session and network ---------------------------------------------------
unattended=""
for v in CI GITHUB_ACTIONS GITLAB_CI TF_BUILD; do
  val="${!v:-}"; [ -n "$val" ] && unattended="${unattended}${unattended:+, }$v"
done
if [ -n "$unattended" ]; then info session "unattended ($unattended set): guessed facts cannot be confirmed here; the hand-off lists them"
else info session "attended: a person can confirm each guessed fact"; fi
if have curl; then
  net=""
  if curl -sI --max-time 4 https://github.com/linkml/linkml-project-copier >/dev/null 2>&1; then net="github.com"
  else warn network "github.com unreachable - copier cannot fetch the template"; fi
  if curl -sI --max-time 4 https://pypi.org/simple/linkml/ >/dev/null 2>&1; then net="${net}${net:+, }pypi.org"
  else warn network "pypi.org unreachable - uv cannot install copier, just or linkml"; fi
  [ -n "$net" ] && info network "$net reachable"
else
  warn network "curl not installed - reachability not checked; the scaffold needs github.com and pypi.org"
fi

printf 'Preflight: %d missing, %d warning(s).%s\n' "$missing" "$warns" "${disables:+ Missing disables: $disables.}"
exit 0
