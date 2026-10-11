#!/usr/bin/env python3
"""The Python half of linkml-scaffold.sh: lay down a `.linkml/` sidecar.

The driver sets the template pin and picks an interpreter; this file does
the work, in this order:

1. refuse when a sidecar already exists (`.linkml/`, a visible `linkml/`
   with answers, or answers at the root), unless asked to repair one file
   or to re-add the root pointers;
2. check the facts the environment carries against the template's own
   rules, and read the ones a KTL bundle already records;
3. verify that the pinned tag still names the pinned commit, so `--trust`
   is given to a template that was read, not to whatever the tag points
   at today;
4. pre-seed every file the skill owns, with the placeholders substituted
   by `str.replace` (never sed: a value holding sed's delimiter would
   change the command rather than the text);
5. run copier for everything else; the template's `_skip_if_exists` keeps
   it off the pre-seeded files, and `copier update` keeps it that way;
6. neutralise what the template assumes of a repository root (the
   catalogue is references/template-assumptions.md), wire a KTL bundle
   when one is present, add the root pointers, and print the hand-off.

Every line it prints starts with `scaffold:`, `handoff:` or `next:`, so a
skill can read it back. `--dry-run` prints the same lines and writes
nothing. Python 3.8 or later, standard library only.
"""

from __future__ import annotations

import argparse
import datetime
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
TEMPLATES = SKILL_DIR / "templates"
SIDECAR = ".linkml"
DOORWAY = "linkml_schema"
MARKER = "# ---- linkml-sidecar: the linkml_schema doorway"
TOKENS = (
    "PROJ_NAME",
    "PROJ_SLUG",
    "PROJ_DESC",
    "GITHUB_ORG",
    "REPO_URL",
    "FULL_NAME",
    "EMAIL",
    "LICENSE_ID",
    "SCHEMA_ID",
    "DOCS_URL",
    "COPYRIGHT_YEAR",
    "TODAY",
    "BASE_IRI",
    "TEMPLATE_REF",
)
LICENSES = ("Apache-2.0", "MIT", "BSD-3-Clause", "MPL-2.0", "LGPL-3.0-only", "GPL-3.0-only", "LicenseRef-Custom")
LICENSE_FILES = ("LICENSE", "LICENSE.md", "LICENSE.txt", "LICENCE", "LICENCE.md", "LICENCE.txt", "COPYING")
NAME_RE = re.compile(r"^[A-Za-z][A-Za-z0-9 _\-]*[A-Za-z0-9]$")
SLUG_RE = re.compile(r"^[a-z][a-z0-9_]*$")
CODE_HOSTS = ("github.com", "gitlab.com", "bitbucket.org", "codeberg.org", "sourceforge.net", "github.io/")
# The files the skill owns, as (template path, destination inside .linkml/).
# Each is in the template's `_skip_if_exists`, or outside the template. The
# dummy schema, its test and its data come from templates/linkml/schema/<mode>/.
OWNED = (
    ("linkml/README.md", "README.md"),
    ("linkml/docs/index.md", "docs/index.md"),
    ("linkml/docs/about.md", "docs/about.md"),
    ("scripts/linkml-preflight.sh", "scripts/linkml-preflight.sh"),
)


class Refused(Exception):
    def __init__(self, code, message):
        super().__init__(message)
        self.code = code


def say(kind, text):
    print(f"{kind}: {text}", flush=True)


def read(path):
    return Path(path).read_text(encoding="utf-8")


def write(path, text, dry, mode=None):
    path = Path(path)
    say("scaffold", f"{'would write' if dry else 'write'} {path}")
    if dry:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")
    if mode is not None:
        path.chmod(mode)


def render(text, facts):
    for token in TOKENS:
        value = facts.get(token)
        if value:
            text = text.replace("<" + token + ">", value)
    left = sorted({m for m in re.findall(r"<([A-Z][A-Z_]+)>", text) if m in TOKENS})
    if left:
        raise Refused(5, f"placeholder(s) {', '.join(left)} have no value; set them in the environment")
    return text


def slugify(name):
    slug = re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")
    return slug if slug and slug[0].isalpha() else "schema_" + slug


def git_toplevel(host):
    try:
        out = subprocess.run(["git", "-C", str(host), "rev-parse", "--show-toplevel"], capture_output=True, text=True)
    except OSError:
        return None
    return Path(out.stdout.strip()) if out.returncode == 0 and out.stdout.strip() else None


def frontmatter_value(path, key):
    try:
        text = read(path)
    except OSError:
        return ""
    if not text.startswith("---"):
        return ""
    head = text.split("\n---", 1)[0]
    m = re.search(rf"^{re.escape(key)}:\s*(.+?)\s*$", head, re.M)
    return m.group(1).strip("\"'") if m else ""


def mk_value(path, key):
    try:
        text = read(path)
    except OSError:
        return ""
    m = re.search(rf"^{re.escape(key)}=(.*)$", text, re.M)
    return m.group(1).strip().strip('"') if m else ""


def answers_value(path, key):
    try:
        text = read(path)
    except OSError:
        return ""
    m = re.search(rf"^{re.escape(key)}:\s*(.*)$", text, re.M)
    return m.group(1).strip().strip("\"'") if m else ""


# ---- facts -----------------------------------------------------------------


def facts_from_env(host, mode, template_ref):
    env = os.environ
    facts = {token: env.get(token, "").strip() for token in TOKENS}
    facts["TEMPLATE_REF"] = template_ref
    facts["TODAY"] = facts["TODAY"] or datetime.date.today().isoformat()
    facts["COPYRIGHT_YEAR"] = facts["COPYRIGHT_YEAR"] or facts["TODAY"][:4]
    if not facts["PROJ_SLUG"] and facts["PROJ_NAME"]:
        facts["PROJ_SLUG"] = slugify(facts["PROJ_NAME"])
    if mode == "lokf" and not facts["BASE_IRI"]:
        facts["BASE_IRI"] = frontmatter_value(host / ".lokf" / "knowledge" / "index.md", "base_iri")
    return facts


def facts_from_sidecar(host, template_ref):
    """The facts a finished sidecar records, for --pointers-only and --repair; the environment still wins."""
    sidecar = host / SIDECAR
    answers = sidecar / ".copier-answers.yml"
    mk = sidecar / "config.public.mk"
    facts = {token: "" for token in TOKENS}
    facts.update(
        PROJ_NAME=answers_value(answers, "project_name"),
        PROJ_SLUG=answers_value(answers, "project_slug") or mk_value(mk, "LINKML_SCHEMA_NAME"),
        PROJ_DESC=answers_value(answers, "project_description") or mk_value(mk, "LINKML_SCHEMA_DESCRIPTION"),
        GITHUB_ORG=answers_value(answers, "github_org"),
        FULL_NAME=answers_value(answers, "full_name"),
        EMAIL=answers_value(answers, "email"),
        LICENSE_ID=answers_value(answers, "license"),
        COPYRIGHT_YEAR=answers_value(answers, "copyright_year"),
        TEMPLATE_REF=answers_value(answers, "_commit") or template_ref,
        TODAY=datetime.date.today().isoformat(),
    )
    mkdocs = sidecar / "mkdocs.yml"
    facts["DOCS_URL"] = answers_value(mkdocs, "site_url")
    facts["REPO_URL"] = answers_value(mkdocs, "repo_url")
    schema = sidecar / "src" / facts["PROJ_SLUG"] / "schema" / f"{facts['PROJ_SLUG']}.yaml" if facts["PROJ_SLUG"] else None
    if schema and schema.is_file():
        facts["SCHEMA_ID"] = answers_value(schema, "id")
    facts["BASE_IRI"] = frontmatter_value(host / ".lokf" / "knowledge" / "index.md", "base_iri")
    for token in TOKENS:
        value = os.environ.get(token, "").strip()
        if value:
            facts[token] = value
    return facts


def validate(facts, mode):
    problems = []
    required = ["PROJ_NAME", "PROJ_SLUG", "PROJ_DESC", "GITHUB_ORG", "REPO_URL", "FULL_NAME", "EMAIL", "LICENSE_ID", "SCHEMA_ID", "DOCS_URL"]
    if mode == "lokf":
        required.append("BASE_IRI")
    for token in required:
        if not facts.get(token):
            problems.append(f"{token} is not set")
    if facts["PROJ_NAME"] and not NAME_RE.match(facts["PROJ_NAME"]):
        problems.append(f"PROJ_NAME {facts['PROJ_NAME']!r} must match {NAME_RE.pattern} (the template's rule)")
    if facts["PROJ_SLUG"] and not SLUG_RE.match(facts["PROJ_SLUG"]):
        problems.append(f"PROJ_SLUG {facts['PROJ_SLUG']!r} must be a Python package name: {SLUG_RE.pattern}")
    if facts["LICENSE_ID"] and facts["LICENSE_ID"] not in LICENSES:
        problems.append(f"LICENSE_ID {facts['LICENSE_ID']!r} is not one of {', '.join(LICENSES)}")
    if facts["EMAIL"] and "@" not in facts["EMAIL"]:
        problems.append("EMAIL has no @")
    for token in ("SCHEMA_ID", "BASE_IRI"):
        value = facts.get(token, "")
        if not value:
            continue
        if not re.match(r"^https?://", value):
            problems.append(f"{token} must be an http(s) IRI")
        if any(h in value for h in CODE_HOSTS):
            problems.append(f"{token} {value!r} names a code host; use a namespace the project controls (w3id.org, purl.org, its own domain)")
    if facts.get("BASE_IRI") and not facts["BASE_IRI"].endswith("/"):
        problems.append("BASE_IRI must end with /")
    if facts["COPYRIGHT_YEAR"] and not re.match(r"^\d{4}$", facts["COPYRIGHT_YEAR"]):
        problems.append("COPYRIGHT_YEAR must be four digits")
    if problems:
        raise Refused(2, "; ".join(problems))


# ---- the pin ---------------------------------------------------------------


def template_url(src):
    if src.startswith("gh:"):
        return "https://github.com/" + src[3:] + ".git"
    if src.startswith("gl:"):
        return "https://gitlab.com/" + src[3:] + ".git"
    return src


def check_pin(src, ref, sha, skip):
    url = template_url(src)
    if skip or not re.match(r"^(https?|git|ssh)://|^git@", url):
        say("scaffold", f"pin check skipped for {src} ({'asked' if skip else 'a local path'})")
        return
    try:
        out = subprocess.run(["git", "ls-remote", "--tags", url, f"refs/tags/{ref}^{{}}", f"refs/tags/{ref}"], capture_output=True, text=True, timeout=60)
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise Refused(2, f"git ls-remote {url} failed: {exc}")
    if out.returncode != 0:
        raise Refused(2, f"git ls-remote {url} failed: {out.stderr.strip()}")
    found = {}
    for line in out.stdout.splitlines():
        parts = line.split()
        if len(parts) == 2:
            found[parts[1]] = parts[0]
    commit = found.get(f"refs/tags/{ref}^{{}}") or found.get(f"refs/tags/{ref}")
    if commit != sha:
        raise Refused(2, f"the tag {ref} on {url} names {commit or 'nothing'}, not the pinned {sha}; the pin moved, or the tag did - read the template before trusting it")
    say("scaffold", f"pin verified: {ref} is {sha[:12]} on {url}")


# ---- the sidecar -----------------------------------------------------------


def refuse_existing(host):
    if (host / SIDECAR).exists():
        raise Refused(3, f"{SIDECAR}/ already exists under {host}; linkml-author works there, and --repair re-lays one file")
    if (host / "linkml" / ".copier-answers.yml").is_file():
        raise Refused(3, "a visible linkml/ sidecar exists (the hand-made shape); it is left alone, and linkml-author works in it")
    if (host / ".copier-answers.yml").is_file():
        raise Refused(3, "this repository is itself a copier project; no sidecar applies")


def host_license(host):
    for name in LICENSE_FILES:
        if (host / name).is_file():
            return host / name
    return None


def dummy_files(mode):
    base = TEMPLATES / "linkml" / "schema" / mode
    out = []
    for path in sorted(base.rglob("*")):
        if path.is_file():
            out.append(path)
    return out


def preseed(host, facts, mode, dry):
    sidecar = host / SIDECAR
    slug = facts["PROJ_SLUG"]
    source = host_license(host)
    if source:
        say("scaffold", f"{'would copy' if dry else 'copy'} {source.name} to {sidecar / 'LICENSE'}")
        if not dry:
            sidecar.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, sidecar / "LICENSE")
    else:
        write(sidecar / "LICENSE", render(read(TEMPLATES / "linkml" / "LICENSE.missing"), facts), dry)
        say("handoff", "no LICENSE at the host root: .linkml/LICENSE is a stub that says so; LICENSE_ID should be LicenseRef-Custom until a license exists")
    for template, dest in OWNED:
        src = TEMPLATES / template
        text = render(read(src), facts)
        mode_bits = 0o755 if dest.endswith(".sh") else None
        write(sidecar / dest, text, dry, mode_bits)
    for path in dummy_files(mode):
        rel = path.relative_to(TEMPLATES / "linkml" / "schema" / mode)
        if rel.name == "schema.yaml":
            dest = sidecar / "src" / slug / "schema" / f"{slug}.yaml"
        else:
            dest = sidecar / rel
        write(dest, render(read(path), facts), dry)


def answers_text(facts):
    template = read(TEMPLATES / "answers.yml")
    lines = []
    for line in template.splitlines():
        m = re.match(r'^(\w+): "<([A-Z_]+)>"$', line)
        if m:
            lines.append(f"{m.group(1)}: {json.dumps(facts[m.group(2)])}")
        else:
            lines.append(line)
    return "\n".join(lines) + "\n"


def copier_command():
    custom = os.environ.get("LINKML_COPIER", "").strip()
    if custom:
        return shlex.split(custom)
    return ["uvx", "--from", "copier>=9.4.0,<10", "--with", "jinja2-time", "copier"]


def run_copier(host, facts, src, ref, dry):
    answers = answers_text(facts)
    cmd = copier_command() + ["copy", "--trust", "--defaults", "--vcs-ref", ref, "--data-file", "ANSWERS", "--quiet", src, SIDECAR]
    say("scaffold", f"{'would run' if dry else 'run'} in {host}: {' '.join(shlex.quote(c) for c in cmd)}")
    if dry:
        for line in answers.rstrip("\n").splitlines():
            say("scaffold", f"  answer {line}")
        return
    with tempfile.NamedTemporaryFile("w", suffix=".yml", prefix="linkml-answers-", delete=False, encoding="utf-8") as handle:
        handle.write(answers)
        answers_path = handle.name
    try:
        cmd[cmd.index("ANSWERS")] = answers_path
        done = subprocess.run(cmd, cwd=str(host), stdin=subprocess.DEVNULL, capture_output=True, text=True)
    finally:
        os.unlink(answers_path)
    if done.returncode != 0:
        raise Refused(4, f"copier failed ({done.returncode}): {(done.stderr or done.stdout).strip()[-2000:]}")
    for line in (done.stdout + done.stderr).splitlines():
        if line.strip() and "just setup" not in line and "PROJECT CREATION COMPLETE" not in line:
            say("scaffold", f"copier: {line.rstrip()}")


def after_copy(host, facts, mode, ref, dry):
    sidecar = host / SIDECAR
    if dry:
        say("scaffold", "would check .linkml/.copier-answers.yml, remove nothing, patch mkdocs.yml, append the doorway recipe" + (", set --render-imports" if mode == "lokf" else ""))
        return
    if (sidecar / ".git").exists():
        raise Refused(5, ".linkml/.git appeared: a nested repository; remove it (rm -rf .linkml/.git) and never run just setup there")
    answers = sidecar / ".copier-answers.yml"
    if not answers.is_file():
        raise Refused(5, "copier left no .linkml/.copier-answers.yml")
    commit = answers_value(answers, "_commit")
    if commit != ref:
        say("handoff", f"copier recorded _commit: {commit}, not {ref}; a local template clone without the tag does that; the pin still names {ref}")
    say("scaffold", f"copier recorded _src_path: {answers_value(answers, '_src_path')} _commit: {commit}")
    mkdocs = sidecar / "mkdocs.yml"
    if mkdocs.is_file():
        text = read(mkdocs)
        text = re.sub(r"^site_url:.*$", f"site_url: {facts['DOCS_URL']}", text, count=1, flags=re.M)
        text = re.sub(r"^repo_url:.*$", f"repo_url: {facts['REPO_URL']}", text, count=1, flags=re.M)
        write(mkdocs, text, dry)
    project_justfile = sidecar / "project.justfile"
    block = read(TEMPLATES / "project.justfile.append")
    existing = read(project_justfile) if project_justfile.is_file() else ""
    if MARKER not in existing:
        write(project_justfile, existing.rstrip("\n") + "\n\n" + block, dry)
    if mode == "lokf":
        mk = sidecar / "config.public.mk"
        if mk.is_file():
            text = read(mk)
            text = re.sub(r"^LINKML_GENERATORS_DOC_ARGS=.*$", 'LINKML_GENERATORS_DOC_ARGS="--render-imports"', text, count=1, flags=re.M)
            write(mk, text, dry)
        write(sidecar / ".linkmllint.yaml", lint_config(host), dry)
    inert = [p for p in (sidecar / ".github").rglob("*") if p.is_file()] if (sidecar / ".github").is_dir() else []
    if (sidecar / ".pre-commit-config.yaml").is_file():
        inert.append(sidecar / ".pre-commit-config.yaml")
    say("handoff", f"{len(inert)} inert file(s) under .linkml/.github/ and .pre-commit-config.yaml (GitHub and pre-commit read the root only); the hoisted workflow is Step 5")
    say("handoff", "CODE_OF_CONDUCT.md and CONTRIBUTING.md under .linkml/ are the template's copies; the host's own govern")


# ---- KTL -------------------------------------------------------------------


def lokf_slot_names(host):
    """The top-level slot names of the pinned LOKF schema, read from its YAML text."""
    names = []
    try:
        text = read(host / ".lokf" / "lokf.yaml")
    except OSError:
        return names
    in_slots = False
    for line in text.splitlines():
        if re.match(r"^[A-Za-z_]+:", line):
            in_slots = line.startswith("slots:")
            continue
        m = re.match(r"^  ([A-Za-z_][A-Za-z0-9_]*):\s*$", line)
        if in_slots and m:
            names.append(m.group(1))
    return names


def lint_config(host):
    """linkml-lint checks imported slots too (standard_naming walks the import closure), so LOKF's camelCase relation names would fail `just lint`; this excuses those names and no others."""
    odd = [n for n in lokf_slot_names(host) if not re.fullmatch(r"[a-z][a-z0-9_]*", n)]
    names = ", ".join(odd) if odd else ""
    return (
        "# Written by linkml-sidecar for a schema that imports LOKF's (.lokf/lokf.yaml).\n"
        "# linkml-lint's standard_naming rule walks the import closure, so LOKF's\n"
        "# camelCase slot names would fail `just lint` here. They are excused by\n"
        "# name, and nothing else is: the host's own slots are still held to\n"
        "# snake_case. Regenerate the list when .lokf/lokf.yaml moves to a new\n"
        "# floor (the linkml-sidecar repair does): names that are not snake_case\n"
        "# under its top-level `slots:`.\n"
        "extends: recommended\n"
        "rules:\n"
        "  standard_naming:\n"
        "    level: warning\n"
        f"    exclude: [{names}]\n"
    )




def pin_lokf_schema(host, dry):
    """The pinned core schema beside the bundle, so the sidecar's schema can import it (ktl-librarian's domain-schema.md, step 1)."""
    lokf = host / ".lokf"
    target = lokf / "lokf.yaml"
    if target.is_file():
        say("scaffold", ".lokf/lokf.yaml is pinned already")
        return
    if dry:
        say("scaffold", "would copy the toolkit's lokf.yaml to .lokf/lokf.yaml (uv sync, then importlib.resources)")
        return
    if not (lokf / "pyproject.toml").is_file():
        raise Refused(2, ".lokf/ has no pyproject.toml, so the lokf toolkit cannot be installed to copy lokf.yaml out of; run ktl-sidecar first")
    if not shutil.which("uv"):
        raise Refused(2, "uv is needed to install the lokf toolkit and copy lokf.yaml beside the bundle")
    sync = subprocess.run(["uv", "sync"], cwd=str(lokf), capture_output=True, text=True)
    if sync.returncode != 0:
        raise Refused(2, f"uv sync in .lokf/ failed: {sync.stderr.strip()[-800:]}")
    code = "from importlib.resources import files; print(files('lokf') / 'data' / 'lokf.yaml')"
    found = subprocess.run(["uv", "run", "--quiet", "python", "-c", code], cwd=str(lokf), capture_output=True, text=True)
    path = found.stdout.strip().splitlines()[-1] if found.returncode == 0 and found.stdout.strip() else ""
    if not path or not Path(path).is_file():
        raise Refused(2, f"could not find lokf.yaml in the installed toolkit: {found.stderr.strip()[-400:]}")
    shutil.copyfile(path, target)
    say("scaffold", f"copied {path} to .lokf/lokf.yaml")


def wire_lokf(host, facts, dry):
    """`schema :=` and `--schema` in .lokf/justfile (domain-schema.md, step 4); an unexpected line is printed, not patched."""
    justfile = host / ".lokf" / "justfile"
    schema = f"../{SIDECAR}/src/{facts['PROJ_SLUG']}/schema/{facts['PROJ_SLUG']}.yaml"
    if not justfile.is_file():
        say("handoff", f"no .lokf/justfile to wire; when one exists, add schema := \"{schema}\" and --schema {{{{ schema }}}} to lokf-validate and lokf-check-refs")
        return
    text = read(justfile)
    if re.search(r'^schema := ""$', text, re.M):
        # The ktl-sidecar template that carries the variable itself: its recipes
        # already pass --schema and run from the schema's directory when it is set.
        write(justfile, re.sub(r'^schema := ""$', f'schema := "{schema}"', text, count=1, flags=re.M), dry)
        say("handoff", f'.lokf/justfile wired: schema := "{schema}" (the template\'s own recipes take it from there)')
        say("handoff", "list ExampleConcept under the KTL plugins' Known LOKF types")
        return
    if re.search(r"^schema := ", text, re.M):
        say("scaffold", ".lokf/justfile already names a schema; left alone")
        return
    run_there = "cd {{ parent_directory(schema) }} && uv run --project {{ justfile_directory() }} lokf validate"
    edits = [
        (
            'bundle := "knowledge"\n',
            'bundle := "knowledge"\n'
            "# The sidecar's domain schema; the validate recipes run from its directory so\n"
            "# its relative import of lokf.yaml resolves (linkml-sidecar references/ktl.md).\n"
            f'schema := "{schema}"\n',
        ),
        ("    uv run lokf validate {{ bundle }}\n", f"    {run_there} --schema {{{{ file_name(schema) }}}} {{{{ justfile_directory() }}}}/{{{{ bundle }}}}\n"),
        ("    uv run lokf validate --check-refs {{ bundle }}\n", f"    {run_there} --check-refs --schema {{{{ file_name(schema) }}}} {{{{ justfile_directory() }}}}/{{{{ bundle }}}}\n"),
    ]
    missing = [old for old, _ in edits if old not in text]
    if missing:
        say(
            "handoff",
            f".lokf/justfile does not hold the ktl-sidecar template's lines {missing!r}; "
            f"add schema := \"{schema}\" and --schema {{{{ schema }}}} to lokf-validate and lokf-check-refs by hand",
        )
        return
    for old, new in edits:
        text = text.replace(old, new, 1)
    write(justfile, text, dry)
    say("handoff", f".lokf/justfile wired: schema := \"{schema}\"; lokf-validate and lokf-check-refs run from the schema's directory")
    say(
        "handoff",
        "make the validate steps of knowledge-registrar.yaml and knowledge-librarian.yaml run `just lokf-validate` "
        "(the host then owns those copies), and list ExampleConcept under the plugins' Known LOKF types",
    )


# ---- root pointers ---------------------------------------------------------


def readme_aside(host, facts, dry):
    readme = host / "README.md"
    if not readme.is_file():
        say("scaffold", "no README.md at the root; no aside added (never invent one)")
        return
    text = read(readme)
    if SIDECAR + "/" in text:
        say("scaffold", "README.md already names .linkml/; left alone")
        return
    aside = render(read(TEMPLATES / "readme-for-schema.md"), facts).rstrip("\n") + "\n"
    lines = text.split("\n")
    at = next((i for i, line in enumerate(lines) if line.startswith("## ")), None)
    if at is None:
        new = text.rstrip("\n") + "\n\n" + aside
    else:
        new = "\n".join(lines[:at]).rstrip("\n") + "\n\n" + aside + "\n" + "\n".join(lines[at:])
    write(readme, new, dry)


def llms_pointer(host, facts, mode, dry):
    llms = host / "llms.txt"
    section = "llms-section-lokf.md" if mode == "lokf" else "llms-section.md"
    if not llms.is_file():
        text = render(read(TEMPLATES / "llms.txt"), facts).rstrip("\n") + "\n\n" + render(read(TEMPLATES / section), facts)
        write(llms, text, dry)
        return
    text = read(llms)
    if SIDECAR + "/" in text:
        say("scaffold", "llms.txt already names .linkml/; left alone")
        return
    write(llms, text.rstrip("\n") + "\n\n" + render(read(TEMPLATES / section), facts), dry)


def doorway(host, facts, dry):
    link = host / DOORWAY
    target = f"{SIDECAR}/src/{facts['PROJ_SLUG']}/schema"
    if link.is_symlink():
        current = os.readlink(link)
        if current == target:
            say("scaffold", f"{DOORWAY} -> {target} already present")
        else:
            say("handoff", f"{DOORWAY} links elsewhere ({current}); left alone")
        return
    if link.exists():
        say("handoff", f"{DOORWAY} exists and is not a link; left alone")
        return
    say("scaffold", f"{'would link' if dry else 'link'} {DOORWAY} -> {target}")
    if dry:
        return
    try:
        os.symlink(target, link)
    except OSError as exc:
        say("handoff", f"could not create the {DOORWAY} link ({exc}); on Windows: mklink /J {DOORWAY} {SIDECAR}\\src\\{facts['PROJ_SLUG']}\\schema")


def gitignore_lines(host, dry):
    path = host / ".gitignore"
    text = read(path) if path.is_file() else ""
    have = set(text.split("\n"))
    add = [line for line in (f"{SIDECAR}/", DOORWAY) if line not in have and line.rstrip("/") not in have]
    if not add:
        say("scaffold", ".gitignore already names the sidecar and the doorway")
        return
    block = "\n# The LinkML schema sidecar is kept out of git on this host (linkml-sidecar Step 0).\n" + "\n".join(add) + "\n"
    write(path, (text.rstrip("\n") + "\n" if text else "") + block.lstrip("\n"), dry)


def pointers(host, facts, mode, gitignored, dry):
    readme_aside(host, facts, dry)
    llms_pointer(host, facts, mode, dry)
    doorway(host, facts, dry)
    if gitignored:
        gitignore_lines(host, dry)
    say("handoff", f"exclude {SIDECAR}/ and {DOORWAY}/ from any repo-wide Markdown, spelling or link check the host runs; the same files would be processed twice")


# ---- repair ----------------------------------------------------------------


def repair(host, facts, mode, target, dry):
    rel = target.replace("\\", "/")
    if rel.startswith(SIDECAR + "/"):
        rel = rel[len(SIDECAR) + 1 :]
    slug = facts["PROJ_SLUG"]
    for template, dest in OWNED:
        if dest == rel:
            write(host / SIDECAR / dest, render(read(TEMPLATES / template), facts), dry, 0o755 if dest.endswith(".sh") else None)
            return
    for path in dummy_files(mode):
        rel_t = path.relative_to(TEMPLATES / "linkml" / "schema" / mode)
        dest = f"src/{slug}/schema/{slug}.yaml" if rel_t.name == "schema.yaml" else str(rel_t)
        if dest == rel:
            write(host / SIDECAR / dest, render(read(path), facts), dry)
            return
    if rel == "LICENSE":
        preseed_license_only(host, facts, dry)
        return
    raise Refused(2, f"{target} is not a file this skill owns; a template-owned file comes back with `just --justfile .linkml/justfile update`, and project.justfile's block with --pointers-only")


def preseed_license_only(host, facts, dry):
    source = host_license(host)
    if source:
        say("scaffold", f"{'would copy' if dry else 'copy'} {source.name} to {SIDECAR}/LICENSE")
        if not dry:
            shutil.copyfile(source, host / SIDECAR / "LICENSE")
    else:
        write(host / SIDECAR / "LICENSE", render(read(TEMPLATES / "linkml" / "LICENSE.missing"), facts), dry)


# ---- main ------------------------------------------------------------------


def main(argv=None):
    parser = argparse.ArgumentParser(description="lay down a .linkml/ LinkML sidecar")
    parser.add_argument("--host", default=".", help="the repository root (default: the current directory)")
    parser.add_argument("--mode", choices=["plain", "lokf", "auto"], default="auto", help="lokf when .lokf/ exists (default: auto)")
    parser.add_argument("--dry-run", action="store_true", help="print every action; write nothing")
    parser.add_argument("--gitignored", action="store_true", help="the host keeps .linkml/ out of git: add it and the doorway to .gitignore")
    parser.add_argument("--pointers-only", action="store_true", help="re-add the root pointers to a finished sidecar")
    parser.add_argument("--repair", metavar="PATH", help="re-lay one skill-owned file of a finished sidecar")
    args = parser.parse_args(argv)

    host = Path(args.host).resolve()
    if not host.is_dir():
        say("scaffold", f"no such directory: {args.host}")
        return 2
    src = os.environ.get("LINKML_TEMPLATE_SRC", "gh:linkml/linkml-project-copier")
    ref = os.environ.get("LINKML_TEMPLATE_REF", "")
    sha = os.environ.get("LINKML_TEMPLATE_SHA", "")
    if not ref or not sha:
        say("scaffold", "LINKML_TEMPLATE_REF and LINKML_TEMPLATE_SHA are unset; run linkml-scaffold.sh, which holds the pin")
        return 2
    mode = args.mode if args.mode != "auto" else ("lokf" if (host / ".lokf").is_dir() else "plain")
    dry = args.dry_run
    try:
        if args.pointers_only or args.repair:
            if not (host / SIDECAR / ".copier-answers.yml").is_file():
                raise Refused(3, f"no finished sidecar under {host} to work on")
            facts = facts_from_sidecar(host, ref)
            if args.repair:
                validate_light(facts)
                repair(host, facts, mode, args.repair, dry)
            else:
                pointers(host, facts, mode, args.gitignored, dry)
            return 0
        refuse_existing(host)
        facts = facts_from_env(host, mode, ref)
        validate(facts, mode)
        say("scaffold", f"mode {mode}; host {host}; template {src} at {ref}")
        for token in ("PROJ_NAME", "PROJ_SLUG", "LICENSE_ID", "SCHEMA_ID", "DOCS_URL", "BASE_IRI"):
            if facts.get(token):
                say("handoff", f"{token}={facts[token]}")
        if mode == "lokf":
            pin_lokf_schema(host, dry)
        check_pin(src, ref, sha, os.environ.get("LINKML_TEMPLATE_SKIP_PIN_CHECK") == "1")
        preseed(host, facts, mode, dry)
        run_copier(host, facts, src, ref, dry)
        after_copy(host, facts, mode, ref, dry)
        if mode == "lokf":
            wire_lokf(host, facts, dry)
        pointers(host, facts, mode, args.gitignored, dry)
        say("handoff", f"sidecar {'would be ' if dry else ''}laid down in {SIDECAR}/ ({'gitignored' if args.gitignored else 'to be committed'}); validation not yet run")
        say("next", f"just --justfile {SIDECAR}/justfile install && just --justfile {SIDECAR}/justfile lint && just --justfile {SIDECAR}/justfile test")
        if mode == "lokf":
            say("next", "cd .lokf && just lokf-validate && just lokf-check-refs")
        return 0
    except Refused as exc:
        say("scaffold", f"{'refused' if exc.code == 3 else 'failed'} ({exc.code}): {exc}")
        return exc.code


def validate_light(facts):
    if not facts.get("PROJ_SLUG"):
        raise Refused(2, "the sidecar records no project_slug; set PROJ_SLUG")


if __name__ == "__main__":
    sys.exit(main())
