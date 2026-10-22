#!/usr/bin/env python3
# /// script
# requires-python = ">=3.8"
# dependencies = []
# ///
"""The Python half of linkml-scaffold.sh: lay down a `.linkml/` sidecar.

The driver sets the template pin and picks an interpreter; this file does
the work, in this order:

1. refuse when a LinkML schema project already exists (a sidecar in
   `.linkml/`, or linkml-project-copier's answers or a `config.public.mk`
   at the root or one directory down), unless asked to repair one file or
   to re-add the root pointers. A `.linkml/` that holds only configuration
   files is installed around, never emptied. A schema the host already
   holds outside any project is refused too, until `--adopt` names it or
   `--dummy` asks for the example schema beside it;
2. check the facts the environment carries against the template's own
   rules, and read the ones a KTL bundle already records;
3. verify that the pinned tag still names the pinned commit, so `--trust`
   is given to a template that was read, not to whatever the tag points
   at today;
4. pre-seed every file the skill owns into a staging directory beside
   `.linkml/`, with the placeholders substituted by `str.replace` (never
   sed: a value holding sed's delimiter would change the command rather
   than the text);
5. run copier for everything else, into the same staging directory; the
   template's `_skip_if_exists` keeps it off the pre-seeded files, and
   `copier update` keeps it that way;
6. move the staged files into `.linkml/`: a name both hold is a clash and
   nothing moves. A failure before this point removes the staging
   directory and nothing else, so `.linkml/` is never deleted here;
7. neutralise what the template assumes of a repository root (the
   catalogue is references/template-assumptions.md), and rename the
   generators' settings from config.yaml to generators.yaml. Then name
   the schema in a KTL bundle's justfile when one is present, add the
   root pointers, and print the hand-off.

With `--adopt <schema>`, no dummy is written. `config.public.mk` points
`LINKML_SCHEMA_SOURCE_DIR` at the folder that already holds the host's
schema, which is never moved, linked or edited, and the folder the
template expects gets a README that says where the schema is.

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
STAGING_PREFIX = ".linkml-staging-"
# What tells a LinkML schema project apart from any other folder, by its
# files and never by its name: linkml-project-copier's answers naming that
# template, or the config.public.mk that it and the older
# linkml-project-cookiecutter render. The second is a signal upstream may
# retire; the first stays as long as copier does.
PROJECT_TEMPLATE = "linkml-project-copier"
PROJECT_CONFIG = "config.public.mk"
# What a schema project holds besides those two, so that a .linkml/ made by
# hand, or left by an older scaffold's failed run, is told from one that
# holds only configuration files.
PROJECT_SHAPE = ("pyproject.toml", "justfile", "Makefile", "src")
# How a LinkML schema file is recognised by its content (one of the signs,
# and a top-level key only a schema has), and the folders that by convention
# hold copies, fixtures or rendered output rather than the host's own model.
# The preflight applies the same rule and the same list.
SCHEMA_SIGNS = ("linkml:types", "https://w3id.org/linkml/")
SCHEMA_KEYS = re.compile(r"^(classes|slots|enums|types|subsets|imports):", re.M)
PRUNED = (".git", ".github", ".venv", "node_modules", "tmp", "site", "project", "docs", "tests", "test", "fixtures", "templates", ".lokf", SIDECAR)
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
    "SCHEMA_DIR",
    "DOCS_URL",
    "COPYRIGHT_YEAR",
    "TODAY",
    "BASE_IRI",
    "TEMPLATE_REF",
)
LICENSES = ("Apache-2.0", "MIT", "BSD-3-Clause", "MPL-2.0", "LGPL-3.0-only", "GPL-3.0-only", "LicenseRef-Custom")
LICENSE_FILES = ("LICENSE", "LICENSE.md", "LICENSE.txt", "LICENCE", "LICENCE.md", "LICENCE.txt", "COPYING")
NAME_RE = re.compile(r"^[A-Za-z][A-Za-z0-9 _\-]*[A-Za-z0-9]$")
SLUG_RE = re.compile(r"^[a-z][a-z0-9_]+$")
CODE_HOSTS = ("github.com", "gitlab.com", "bitbucket.org", "codeberg.org", "sourceforge.net", "github.io/")
# The KTL workflows whose validate step runs `lokf validate --check-refs`
# inline until ktl-sidecar's template carries the `schema` variable, and the
# line that template runs instead. The runners have no `just`, so the step
# runs it through uvx.
# The generators' settings. The template renders them as config.yaml at the
# project's root and names that file in config.public.mk, which every recipe
# reads; nothing else names it. The sidecar keeps them as generators.yaml, so
# from the host's root they sit at .linkml/generators.yaml, in the folder
# upstream LinkML may name for its configuration files. A new sidecar is
# renamed without asking, and `--repair generators.yaml` moves an existing
# project's file when a person agrees. copier update leaves the moved file
# alone: a test from v0.4.0 to v0.4.2, where upstream changed config.yaml,
# kept the old settings. So the template's later changes no longer arrive.
TEMPLATE_GENERATORS = "config.yaml"
GENERATORS = "generators.yaml"
GENERATORS_VAR = "LINKML_GENERATORS_CONFIG_YAML"
KTL_WORKFLOWS = ("knowledge-registrar.yaml", "knowledge-librarian.yaml", "knowledge-release.yaml")
KTL_VALIDATE_STEP = "uvx --from rust-just==1.47.0 just lokf-check-refs"
# The files the skill owns, as (template path, destination inside .linkml/).
# Each is in the template's `_skip_if_exists`, or outside the template. The
# dummy schema, its test and its data come from templates/linkml/schema/<mode>/.
OWNED = (
    ("linkml/README.md", "README.md"),
    ("linkml/docs/index.md", "docs/index.md"),
    ("linkml/docs/about.md", "docs/about.md"),
    ("scripts/linkml-preflight.sh", "scripts/linkml-preflight.sh"),
)
# The staging directory of the current run, so that a path in it is printed
# as its place under .linkml/.
_stage = None


class Refused(Exception):
    def __init__(self, code, message):
        super().__init__(message)
        self.code = code


def say(kind, text):
    print(f"{kind}: {text}", flush=True)


def shown(path):
    """A path as the hand-off names it: a file in the staging directory reads as its place under .linkml/."""
    text = str(path)
    if _stage is not None and text.startswith(str(_stage)):
        return SIDECAR + text[len(str(_stage)) :]
    return text


def read(path):
    return Path(path).read_text(encoding="utf-8")


def write(path, text, dry, mode=None):
    path = Path(path)
    say("scaffold", f"{'would write' if dry else 'write'} {shown(path)}")
    if dry:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    # open() rather than Path.write_text, whose newline argument needs Python 3.10.
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(text)
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
    mk = sidecar / PROJECT_CONFIG
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
    slug = facts["PROJ_SLUG"]
    # An adopted schema sits outside the sidecar, where config.public.mk points; the dummy sits where the template put it.
    srcdir = mk_value(mk, "LINKML_SCHEMA_SOURCE_DIR") or (f"src/{slug}/schema" if slug else "")
    if srcdir.startswith(".."):
        try:
            facts["SCHEMA_DIR"] = (sidecar / srcdir).resolve().relative_to(host.resolve()).as_posix()
        except ValueError:
            facts["SCHEMA_DIR"] = srcdir
    schema = sidecar / srcdir / f"{slug}.yaml" if slug and srcdir else None
    if schema and schema.is_file():
        facts["SCHEMA_ID"] = answers_value(schema, "id")
    facts["BASE_IRI"] = frontmatter_value(host / ".lokf" / "knowledge" / "index.md", "base_iri")
    for token in TOKENS:
        value = os.environ.get(token, "").strip()
        if value:
            facts[token] = value
    return facts


def validate(facts, mode, adopted=False):
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
    # An adopted schema's id is the host's choice, made before this skill came; only an id chosen here is held to the namespace rules.
    for token in ("SCHEMA_ID", "BASE_IRI"):
        value = facts.get(token, "")
        if not value:
            continue
        if not re.match(r"^https?://", value):
            problems.append(f"{token} must be an http(s) IRI")
        if any(h in value for h in CODE_HOSTS) and not (adopted and token == "SCHEMA_ID"):
            problems.append(f"{token} {value!r} names a code host; use a namespace the project controls (w3id.org, purl.org, its own domain)")
    if facts.get("BASE_IRI") and not facts["BASE_IRI"].endswith("/"):
        problems.append("BASE_IRI must end with /")
    if facts.get("SCHEMA_ID", "").endswith("/") and not adopted:
        problems.append("SCHEMA_ID must not end with /; the schema's prefix adds it")
    if facts["COPYRIGHT_YEAR"] and not re.match(r"^\d{4}$", facts["COPYRIGHT_YEAR"]):
        problems.append("COPYRIGHT_YEAR must be four digits")
    if problems:
        raise Refused(2, "; ".join(problems))


def validate_host(host, facts):
    """What the facts must agree with on disk, checked before anything runs."""
    if host_license(host) is None and facts["LICENSE_ID"] != "LicenseRef-Custom":
        raise Refused(
            2,
            f"no LICENSE file at the host root, so LICENSE_ID must be LicenseRef-Custom, not {facts['LICENSE_ID']!r}: "
            "the stub .linkml/LICENSE says the sidecar carries the host's license, and pyproject.toml records what LICENSE_ID says",
        )


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


# ---- what the host already holds -------------------------------------------


def linkml_project(directory):
    """Whether a directory holds a LinkML schema project, by the two signals PROJECT_TEMPLATE and PROJECT_CONFIG name."""
    if (directory / PROJECT_CONFIG).is_file():
        return True
    answers = directory / ".copier-answers.yml"
    return answers.is_file() and PROJECT_TEMPLATE in answers_value(answers, "_src_path")


def refuse_existing(host):
    """A sidecar, a schema project at the root or one level down, or a .linkml/ nobody can account for: refused. Configuration files alone in .linkml/ are installed around."""
    sidecar = host / SIDECAR
    if (sidecar / ".copier-answers.yml").is_file():
        raise Refused(3, f"{SIDECAR}/ already holds a sidecar; linkml-author works there, and --repair re-lays one file")
    if sidecar.is_dir():
        held = sorted(p.name for p in sidecar.iterdir())
        shaped = [name for name in held if name in PROJECT_SHAPE or name == PROJECT_CONFIG]
        if shaped:
            raise Refused(
                3,
                f"{SIDECAR}/ holds {', '.join(shaped)} but no .copier-answers.yml: a project made by hand, which linkml-author works in, "
                "or what an older scaffold's failed run left, which only a person removes",
            )
        if held:
            more = ", ..." if len(held) > 5 else ""
            say("scaffold", f"{SIDECAR}/ holds {len(held)} file(s) and no project ({', '.join(held[:5])}{more}); the sidecar installs around them, and a name both hold is refused")
    elif sidecar.exists():
        raise Refused(3, f"{SIDECAR} exists and is not a directory")
    for directory in [host] + [p for p in sorted(host.iterdir()) if p.is_dir() and p.name not in PRUNED]:
        if linkml_project(directory):
            where = "this repository is itself" if directory == host else f"{directory.name}/ is"
            told_by = "copier answers" if (directory / ".copier-answers.yml").is_file() else PROJECT_CONFIG
            raise Refused(3, f"{where} a LinkML schema project already ({told_by}); no sidecar applies, linkml-author works there")


def is_schema(path):
    """Whether a file reads as a LinkML schema: one of SCHEMA_SIGNS and one of SCHEMA_KEYS in its first 64 KiB."""
    try:
        with open(path, "rb") as handle:
            head = handle.read(65536).decode("utf-8", "replace")
    except OSError:
        return False
    return any(sign in head for sign in SCHEMA_SIGNS) and SCHEMA_KEYS.search(head) is not None


def schema_files(host):
    """Schema files the host holds outside any project, by content: what git tracks or would track, else the whole tree, less the pruned folders."""
    listed = None
    try:
        done = subprocess.run(["git", "-C", str(host), "ls-files", "-z", "-co", "--exclude-standard", "--", "*.yaml", "*.yml"], capture_output=True, text=True)
        if done.returncode == 0:
            listed = done.stdout.split("\0")
    except OSError:
        pass
    if listed is None:
        listed = []
        for base, dirs, files in os.walk(host):
            dirs[:] = [d for d in dirs if d not in PRUNED]
            for name in files:
                if name.endswith((".yaml", ".yml")):
                    listed.append(os.path.relpath(os.path.join(base, name), host))
    found = []
    for rel in listed:
        rel = rel.replace("\\", "/")
        if not rel or any(part in PRUNED for part in rel.split("/")[:-1]):
            continue
        if is_schema(host / rel):
            found.append(rel)
    return sorted(found)


def tracked_under(host, rel):
    """The files git tracks under a path; none when there is no git or no repository."""
    try:
        done = subprocess.run(["git", "-C", str(host), "ls-files", "-z", "--", rel], capture_output=True, text=True)
    except OSError:
        return []
    return [p for p in done.stdout.split("\0") if p] if done.returncode == 0 else []


def adoption(host, given):
    """The schema file --adopt names, checked: (its folder relative to the host, its slug, its id)."""
    path = Path(given)
    file = (path if path.is_absolute() else host / path).resolve()
    try:
        rel = file.relative_to(host.resolve())
    except ValueError:
        raise Refused(2, f"--adopt {given} is outside {host}")
    if not file.is_file():
        raise Refused(2, f"--adopt {given}: no such file under {host}")
    if rel.parts[0] == SIDECAR:
        raise Refused(2, f"--adopt {given} is inside {SIDECAR}/, where only the sidecar's own schema lives")
    if file.suffix != ".yaml":
        raise Refused(2, f"--adopt {given}: the template names the schema <slug>.yaml, so a {file.suffix or 'bare'} file must be renamed first")
    if not is_schema(file):
        raise Refused(2, f"--adopt {given} does not read as a LinkML schema (no linkml:types import and no linkml prefix)")
    slug = file.stem
    if not SLUG_RE.match(slug):
        raise Refused(
            2,
            f"--adopt {given}: the file's stem {slug!r} is not a slug ({SLUG_RE.pattern}), and the template names the schema file after the slug; "
            "rename the file, or lay the dummy (--dummy) and import this schema from it",
        )
    return rel.parent.as_posix(), slug, answers_value(file, "id")


def adopt_facts(facts, adopt):
    """The facts an adopted schema settles: the slug is its file's stem, its id stands, and SCHEMA_DIR is its folder."""
    folder, slug, schema_id = adopt
    given = os.environ.get("PROJ_SLUG", "").strip()
    if given and given != slug:
        raise Refused(2, f"PROJ_SLUG={given!r}, but the adopted schema file is {slug}.yaml; the template names the schema after the slug, so they must agree")
    facts["PROJ_SLUG"] = slug
    facts["SCHEMA_DIR"] = folder
    if schema_id:
        if facts["SCHEMA_ID"] and facts["SCHEMA_ID"] != schema_id:
            say("handoff", f"SCHEMA_ID={facts['SCHEMA_ID']} differs from the schema's own id {schema_id}, which stands; the sidecar never edits the schema")
        facts["SCHEMA_ID"] = schema_id


# ---- the sidecar -----------------------------------------------------------


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


def adopted_readme(text, facts):
    """The sidecar README for an adopted schema: the tree names the folder the schema really lives in, and a section says so before the removal notes."""
    def tree_line(m):
        entry = f"|-- src/{m.group(1)}/schema/README.md"
        return entry.ljust(45) + f"# says where the schema is: {facts['SCHEMA_DIR']}/ in the host"

    text = re.sub(r"^\|-- src/(\S+)/schema/\S+\.yaml\s+# the schema: the one file to edit$", tree_line, text, count=1, flags=re.M)
    section = render(read(TEMPLATES / "linkml" / "README-adopted.md"), facts).rstrip("\n") + "\n\n"
    if "## Remove it" in text:
        return text.replace("## Remove it", section + "## Remove it", 1)
    return text.rstrip("\n") + "\n\n" + section


def preseed(host, stage, facts, mode, dry, adopt):
    """The files the skill owns, into the staging directory; with an adopted schema, no dummy and no dummy data."""
    slug = facts["PROJ_SLUG"]
    source = host_license(host)
    if source:
        say("scaffold", f"{'would copy' if dry else 'copy'} {source.name} to {SIDECAR}/LICENSE")
        if not dry:
            stage.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, stage / "LICENSE")
    else:
        write(stage / "LICENSE", render(read(TEMPLATES / "linkml" / "LICENSE.missing"), facts), dry)
        say("handoff", "no LICENSE at the host root: .linkml/LICENSE is a stub that says so, and LICENSE_ID is LicenseRef-Custom until a license exists")
    for template, dest in OWNED:
        text = render(read(TEMPLATES / template), facts)
        if adopt and dest == "README.md":
            text = adopted_readme(text, facts)
        mode_bits = 0o755 if dest.endswith(".sh") else None
        write(stage / dest, text, dry, mode_bits)
    if adopt:
        # The template expects src/<slug>/schema/ and renders its own README there;
        # this one, in _skip_if_exists, says where the schema really is. The data
        # test comes without the dummy's data: the host's classes are not Person.
        write(stage / "src" / slug / "schema" / "README.md", render(read(TEMPLATES / "linkml" / "schema-folder-README.md"), facts), dry)
        for path in dummy_files("plain"):
            if path.name == "test_data.py":
                write(stage / path.relative_to(TEMPLATES / "linkml" / "schema" / "plain"), render(read(path), facts), dry)
        return
    for path in dummy_files(mode):
        rel = path.relative_to(TEMPLATES / "linkml" / "schema" / mode)
        if rel.name == "schema.yaml":
            dest = stage / "src" / slug / "schema" / f"{slug}.yaml"
        else:
            dest = stage / rel
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
        return shlex.split(custom, posix=os.name != "nt")
    return ["uvx", "--from", "copier>=9.4.0,<10", "--with", "jinja2-time", "copier"]


def run_copier(host, stage, facts, src, ref, dry):
    answers = answers_text(facts)
    cmd = copier_command() + ["copy", "--trust", "--defaults", "--vcs-ref", ref, "--data-file", "ANSWERS", "--quiet", src, stage.name]
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
        if line.strip():
            say("scaffold", f"copier: {line.rstrip()}")


def after_copy(host, stage, facts, mode, ref, dry, adopt):
    if dry:
        plan = f"would check .linkml/.copier-answers.yml, remove nothing, patch mkdocs.yml, rename {TEMPLATE_GENERATORS} to {GENERATORS}"
        plan += ", point config.public.mk at the adopted schema's folder" if adopt else ", append the doorway recipe"
        plan += ", set --render-imports and write .linkmllint.yaml" if mode == "lokf" else ""
        say("scaffold", plan)
        say_inert_handoffs(None)
        return
    if (stage / ".git").exists():
        raise Refused(5, ".linkml/.git appeared: a nested repository; remove it (rm -rf .linkml/.git) and never run just setup there")
    answers = stage / ".copier-answers.yml"
    if not answers.is_file():
        raise Refused(5, "copier left no .linkml/.copier-answers.yml")
    commit = answers_value(answers, "_commit")
    if commit != ref:
        say("handoff", f"copier recorded _commit: {commit}, not {ref}; a local template clone without the tag does that; the pin still names {ref}")
    say("scaffold", f"copier recorded _src_path: {answers_value(answers, '_src_path')} _commit: {commit}")
    mkdocs = stage / "mkdocs.yml"
    if mkdocs.is_file():
        text = read(mkdocs)
        text = re.sub(r"^site_url:.*$", lambda _m: f"site_url: {facts['DOCS_URL']}", text, count=1, flags=re.M)
        text = re.sub(r"^repo_url:.*$", lambda _m: f"repo_url: {facts['REPO_URL']}", text, count=1, flags=re.M)
        write(mkdocs, text, dry)
    mk = stage / PROJECT_CONFIG
    if adopt:
        # The one line that makes the host's schema the project's: every recipe
        # derives its paths from LINKML_SCHEMA_SOURCE_DIR and LINKML_SCHEMA_NAME.
        source_dir = os.path.relpath(host / facts["SCHEMA_DIR"], host / SIDECAR).replace(os.sep, "/")
        if not mk.is_file():
            raise Refused(5, f"copier left no {PROJECT_CONFIG}, which adoption points at the schema; the template moved under the pin")
        text = re.sub(r"^LINKML_SCHEMA_SOURCE_DIR=.*$", lambda _m: f'LINKML_SCHEMA_SOURCE_DIR="{source_dir}"', read(mk), count=1, flags=re.M)
        write(mk, text, dry)
        say("handoff", f"adopted {facts['SCHEMA_DIR']}/{facts['PROJ_SLUG']}.yaml: {PROJECT_CONFIG} names its folder (LINKML_SCHEMA_SOURCE_DIR={source_dir}); the file was not moved, linked or changed")
    else:
        append_doorway_recipe(stage, facts, dry)
    if (host / SIDECAR / GENERATORS).exists():
        say("handoff", f"{SIDECAR}/{GENERATORS} was already there and is the host's, so the generators' settings stay in {SIDECAR}/{TEMPLATE_GENERATORS}")
    else:
        reason = move_generators(host, stage, stage / GENERATORS, GENERATORS, dry)
        if reason:
            say("handoff", f"the generators' settings stay in {SIDECAR}/{TEMPLATE_GENERATORS}: {reason}")
        else:
            say_generators_update()
    if mode == "lokf":
        if mk.is_file():
            text = read(mk)
            text = re.sub(r"^LINKML_GENERATORS_DOC_ARGS=.*$", lambda _m: 'LINKML_GENERATORS_DOC_ARGS="--render-imports"', text, count=1, flags=re.M)
            write(mk, text, dry)
        write(stage / ".linkmllint.yaml", lint_config(host), dry)
    say_inert_handoffs(stage)


def move_generators(host, project, dest, value, dry):
    """Move project/config.yaml to dest and name value in project/config.public.mk.

    Returns why it could not, or None once it is done (or, in a dry run,
    planned). It checks everything before it moves anything, so a refusal
    leaves both files as they were.
    """
    source = project / TEMPLATE_GENERATORS
    mk = project / PROJECT_CONFIG

    def rel(path):
        return shown(path) if _stage is not None and str(path).startswith(str(_stage)) else os.path.relpath(path, host).replace(os.sep, "/")

    if not source.is_file():
        return f"there is no {rel(source)}"
    if dest.exists() or dest.is_symlink():
        return f"{rel(dest)} already exists"
    if not mk.is_file():
        return f"there is no {rel(mk)}, whose {GENERATORS_VAR} names the file for every recipe"
    line = re.compile(rf'^{GENERATORS_VAR}="?{re.escape(TEMPLATE_GENERATORS)}"?[ \t]*$', re.M)
    text = read(mk)
    if not line.search(text):
        return f"{rel(mk)} does not set {GENERATORS_VAR}={TEMPLATE_GENERATORS}, so the recipes may not read that file"
    if dry:
        say("scaffold", f"would move {rel(source)} to {rel(dest)} and set {GENERATORS_VAR}={value} in {rel(mk)}")
        return None
    dest.parent.mkdir(parents=True, exist_ok=True)
    os.rename(source, dest)
    write(mk, line.sub(f"{GENERATORS_VAR}={value}", text, count=1), dry)
    say("scaffold", f"moved {rel(source)} to {rel(dest)}; {rel(mk)} sets {GENERATORS_VAR}={value}, which every recipe reads")
    return None


def say_generators_update():
    say("handoff", f"the generators' settings are {SIDECAR}/{GENERATORS}, the project's own: just update no longer changes them, so read the template's changelog for changes to its {TEMPLATE_GENERATORS} when the pin moves")


def repair_generators(host, dry):
    """--repair generators.yaml: move a finished project's config.yaml to .linkml/generators.yaml.

    The project is the sidecar, or a schema project at the host's root (made
    with linkml-project-copier or the older cookiecutter); --host names a
    project that sits anywhere else. A root project's file goes into
    .linkml/, beside whatever configuration files are already there.
    """
    if (host / SIDECAR / ".copier-answers.yml").is_file():
        project, value = host / SIDECAR, GENERATORS
    elif linkml_project(host):
        project, value = host, f"{SIDECAR}/{GENERATORS}"
    else:
        raise Refused(3, f"no sidecar and no LinkML schema project at {host}; --host names the project's directory")
    dest = host / SIDECAR / GENERATORS
    if dest.is_file() and not (project / TEMPLATE_GENERATORS).exists() and mk_value(project / PROJECT_CONFIG, GENERATORS_VAR) == value:
        say("scaffold", f"nothing to do: {GENERATORS_VAR}={value} already, and there is no {TEMPLATE_GENERATORS} beside it")
        return
    reason = move_generators(host, project, dest, value, dry)
    if reason:
        raise Refused(3, f"{reason}; nothing was moved")
    if not dry:
        say_generators_update()


def clashes(host, stage):
    """The staged paths .linkml/ already holds, relative to both; a name is enough, contents are never compared."""
    sidecar = host / SIDECAR
    if not sidecar.is_dir():
        return []
    found = []
    for path in sorted(stage.rglob("*")):
        rel = path.relative_to(stage)
        target = sidecar / rel
        if path.is_dir():
            if target.exists() and not target.is_dir():
                found.append(rel.as_posix())
        elif target.exists() or target.is_symlink():
            found.append(rel.as_posix())
    return found


def refuse_clashes(host, stage):
    found = clashes(host, stage)
    if found:
        more = ", ..." if len(found) > 8 else ""
        raise Refused(
            3,
            f"{SIDECAR}/ already holds {len(found)} of the files the sidecar writes ({', '.join(found[:8])}{more}); nothing was written to it. "
            "Move or rename them first; the scaffold never overwrites",
        )


def land(host, stage, dry):
    """Move the staged sidecar into .linkml/, around whatever is already there; a name both hold stops the move before it starts."""
    sidecar = host / SIDECAR
    if dry:
        say("scaffold", f"would move the staged files into {SIDECAR}/" + (" around the files already there" if sidecar.is_dir() else ""))
        return
    if not sidecar.exists():
        os.rename(stage, sidecar)
        return
    refuse_clashes(host, stage)
    for path in sorted(stage.rglob("*")):
        target = sidecar / path.relative_to(stage)
        if path.is_dir():
            target.mkdir(parents=True, exist_ok=True)
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            os.replace(path, target)
    shutil.rmtree(stage)
    say("scaffold", f"moved the sidecar into {SIDECAR}/ around the files already there")


def say_inert_handoffs(sidecar):
    """The two hand-off lines about what the template left that the host ignores; a dry run counts nothing."""
    if sidecar is None:
        count = "the"
    else:
        inert = [p for p in (sidecar / ".github").rglob("*") if p.is_file()] if (sidecar / ".github").is_dir() else []
        if (sidecar / ".pre-commit-config.yaml").is_file():
            inert.append(sidecar / ".pre-commit-config.yaml")
        count = str(len(inert))
    say("handoff", f"{count} inert file(s) under .linkml/.github/ and .pre-commit-config.yaml (GitHub and pre-commit read the root only); the hoisted workflow is Step 5")
    say("handoff", "CODE_OF_CONDUCT.md and CONTRIBUTING.md under .linkml/ are the template's copies; the host's own govern")


def append_doorway_recipe(sidecar, facts, dry):
    """The linkml-link recipe at the end of project.justfile, the file copier merges, once."""
    project_justfile = sidecar / "project.justfile"
    block = render(read(TEMPLATES / "project.justfile.append"), facts)
    existing = read(project_justfile) if project_justfile.is_file() else ""
    if MARKER in existing:
        say("scaffold", "project.justfile already carries the doorway recipe")
        return
    write(project_justfile, existing.rstrip("\n") + "\n\n" + block, dry)


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
    if not (lokf / "pyproject.toml").is_file():
        raise Refused(2, ".lokf/ has no pyproject.toml, so the lokf toolkit cannot be installed to copy lokf.yaml out of; run ktl-sidecar first")
    if not shutil.which("uv"):
        raise Refused(2, "uv is needed to install the lokf toolkit and copy lokf.yaml beside the bundle")
    if dry:
        say("scaffold", "would copy the toolkit's lokf.yaml to .lokf/lokf.yaml (uv sync, then importlib.resources)")
        return
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


def say_ktl_workflows():
    """The hand-off for KTL workflows that still validate inline, which never see the schema."""
    say(
        "handoff",
        f"make the validate step of {', '.join(KTL_WORKFLOWS[:-1])} and {KTL_WORKFLOWS[-1]} run `{KTL_VALIDATE_STEP}`, "
        "so CI checks the bundle against the schema too (the host then owns those copies)",
    )


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
        write(justfile, re.sub(r'^schema := ""$', lambda _m: f'schema := "{schema}"', text, count=1, flags=re.M), dry)
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
        say_ktl_workflows()
        say("handoff", "list ExampleConcept under the KTL plugins' Known LOKF types")
        return
    for old, new in edits:
        text = text.replace(old, new, 1)
    write(justfile, text, dry)
    say("handoff", f".lokf/justfile wired: schema := \"{schema}\"; lokf-validate and lokf-check-refs run from the schema's directory")
    say_ktl_workflows()
    say("handoff", "list ExampleConcept under the KTL plugins' Known LOKF types")


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
    at = first_section(lines)
    if at is None:
        new = text.rstrip("\n") + "\n\n" + aside
    elif at == 0:
        new = aside + "\n" + text
    else:
        new = "\n".join(lines[:at]).rstrip("\n") + "\n\n" + aside + "\n" + "\n".join(lines[at:])
    write(readme, new, dry)


def first_section(lines):
    """The index of the first `## ` heading outside a fenced code block, or None."""
    fence = None
    for i, line in enumerate(lines):
        stripped = line.lstrip()
        if fence is None and (stripped.startswith("```") or stripped.startswith("~~~")):
            fence = stripped[:3]
            continue
        if fence is not None:
            if stripped.startswith(fence):
                fence = None
            continue
        if line.startswith("## "):
            return i
    return None


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
        os.symlink(target, link, target_is_directory=True)
    except OSError as exc:
        say("handoff", f"could not create the {DOORWAY} link ({exc}); on Windows: mklink /J {DOORWAY} {SIDECAR}\\src\\{facts['PROJ_SLUG']}\\schema")


def gitignore_lines(host, dry, with_doorway=True):
    path = host / ".gitignore"
    text = read(path) if path.is_file() else ""
    have = {line.strip().lstrip("/").rstrip("/") for line in text.split("\n")}
    wanted = (f"{SIDECAR}/", DOORWAY) if with_doorway else (f"{SIDECAR}/",)
    add = [line for line in wanted if line.rstrip("/") not in have]
    if not add:
        say("scaffold", ".gitignore already names the sidecar and the doorway" if with_doorway else ".gitignore already names the sidecar")
        return
    block = "\n# The LinkML schema sidecar is kept out of git on this host (linkml-sidecar Step 0).\n" + "\n".join(add) + "\n"
    write(path, (text.rstrip("\n") + "\n" if text else "") + block.lstrip("\n"), dry)


def pointers(host, facts, mode, gitignored, dry, adopted=False):
    """The root pointers; an adopted schema is already visible where it is, so it gets none of the three."""
    if adopted:
        say("handoff", f"no README aside, llms.txt section or {DOORWAY} doorway: the schema is already visible at {facts['SCHEMA_DIR']}/; mention {SIDECAR}/'s recipes where the host documents the schema")
    else:
        readme_aside(host, facts, dry)
        llms_pointer(host, facts, mode, dry)
        doorway(host, facts, dry)
    if gitignored:
        gitignore_lines(host, dry, with_doorway=not adopted)
    say("handoff", f"exclude {SIDECAR}/ and {DOORWAY}/ from any repo-wide Markdown, spelling or link check the host runs; the same files would be processed twice")


def adoption_handoff(host, facts):
    """What an adopted schema's sidecar still needs from a person."""
    say("handoff", f"no example data was laid down: add one valid example per class under {SIDECAR}/tests/data/valid/ (and counter-examples under invalid/)")
    say("handoff", f"Step 5's workflow runs on {SIDECAR}/** only; add \"{facts['SCHEMA_DIR']}/**\" to both paths lists of .github/workflows/linkml-sidecar.yaml so a schema edit runs the gate")
    if (host / ".lokf").is_dir():
        say("handoff", ".lokf/ is present and not wired: the adopted schema stays as it is; to make it the bundle's domain schema, linkml-author adds the lokf.yaml import and the justfile's schema variable")


# ---- repair ----------------------------------------------------------------


def repair(host, facts, mode, target, dry):
    rel = target.replace("\\", "/")
    if os.path.isabs(rel):
        rel = os.path.relpath(rel, host).replace("\\", "/")
    rel = os.path.normpath(rel).replace("\\", "/")
    if rel.startswith(SIDECAR + "/"):
        rel = rel[len(SIDECAR) + 1 :]
    slug = facts["PROJ_SLUG"]
    adopted = bool(facts.get("SCHEMA_DIR"))
    if rel == ".linkmllint.yaml":
        if mode != "lokf":
            raise Refused(2, ".linkmllint.yaml is written in KTL mode only (the host has no .lokf/, or --mode plain was given)")
        write(host / SIDECAR / rel, lint_config(host), dry)
        return
    if rel == "project.justfile":
        append_doorway_recipe(host / SIDECAR, facts, dry)
        return
    for template, dest in OWNED:
        if dest == rel:
            text = render(read(TEMPLATES / template), facts)
            if adopted and dest == "README.md":
                text = adopted_readme(text, facts)
            write(host / SIDECAR / dest, text, dry, 0o755 if dest.endswith(".sh") else None)
            return
    if adopted and rel == f"src/{slug}/schema/README.md":
        write(host / SIDECAR / rel, render(read(TEMPLATES / "linkml" / "schema-folder-README.md"), facts), dry)
        return
    for path in dummy_files("plain" if adopted else mode):
        rel_t = path.relative_to(TEMPLATES / "linkml" / "schema" / ("plain" if adopted else mode))
        dest = f"src/{slug}/schema/{slug}.yaml" if rel_t.name == "schema.yaml" else str(rel_t)
        if dest == rel and not (adopted and dest != "tests/test_data.py"):
            write(host / SIDECAR / dest, render(read(path), facts), dry)
            return
    if rel == "LICENSE":
        preseed_license_only(host, facts, dry)
        return
    raise Refused(2, f"{target} is not a file this skill owns (the preflight, README.md, docs/index.md, docs/about.md, LICENSE, the dummy schema and its tests, .linkmllint.yaml, project.justfile's doorway recipe, or {GENERATORS}, which moves {TEMPLATE_GENERATORS}); a template-owned file comes back with `just --justfile .linkml/justfile update`")


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
    global _stage
    parser = argparse.ArgumentParser(description="lay down a .linkml/ LinkML sidecar")
    parser.add_argument("--host", default=".", help="the repository root (default: the current directory)")
    parser.add_argument("--mode", choices=["plain", "lokf", "auto"], default="auto", help="lokf when .lokf/ exists (default: auto)")
    parser.add_argument("--dry-run", action="store_true", help="print every action; write nothing")
    parser.add_argument("--gitignored", action="store_true", help="the host keeps .linkml/ out of git: add it and the doorway to .gitignore")
    parser.add_argument("--pointers-only", action="store_true", help="re-add the root pointers to a finished sidecar")
    parser.add_argument("--repair", metavar="PATH", help="rewrite one skill-owned file of a finished sidecar; generators.yaml moves a finished project's config.yaml there")
    schema = parser.add_mutually_exclusive_group()
    schema.add_argument("--adopt", metavar="SCHEMA", help="give the schema file the host already holds the toolchain, instead of laying the dummy")
    schema.add_argument("--dummy", action="store_true", help="lay the dummy schema although the host holds a schema")
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
    stage = None
    try:
        if args.repair and os.path.normpath(args.repair).replace("\\", "/") in (GENERATORS, f"{SIDECAR}/{GENERATORS}"):
            repair_generators(host, dry)
            return 0
        if args.pointers_only or args.repair:
            if not (host / SIDECAR / ".copier-answers.yml").is_file():
                raise Refused(3, f"no finished sidecar under {host} to work on")
            facts = facts_from_sidecar(host, ref)
            validate_light(facts)
            if args.repair:
                repair(host, facts, mode, args.repair, dry)
            else:
                pointers(host, facts, mode, args.gitignored, dry, adopted=bool(facts.get("SCHEMA_DIR")))
            return 0
        refuse_existing(host)
        adopt = adoption(host, args.adopt) if args.adopt else None
        if adopt and args.mode == "lokf":
            raise Refused(2, "--adopt and --mode lokf do not go together: adoption never edits the host's schema, and making it the bundle's domain schema is linkml-author's job afterwards")
        if adopt and mode == "lokf":
            say("scaffold", ".lokf/ is present, but an adopted schema is left as it is: plain mode; linkml-author wires it to the bundle when it should type concepts")
            mode = "plain"
        if not adopt and not args.dummy:
            schemas = schema_files(host)
            if schemas:
                more = ", ..." if len(schemas) > 5 else ""
                raise Refused(3, f"the host already holds a LinkML schema: {', '.join(schemas[:5])}{more}; --adopt <path> gives it the toolchain, --dummy lays the example schema beside it")
        if args.gitignored:
            tracked = tracked_under(host, SIDECAR)
            if tracked:
                raise Refused(2, f"{SIDECAR}/ holds files git tracks ({', '.join(tracked[:5])}); ignoring the directory would hide them, so the sidecar is committed beside them or not installed")
        facts = facts_from_env(host, mode, ref)
        if adopt:
            adopt_facts(facts, adopt)
        validate(facts, mode, adopted=bool(adopt))
        validate_host(host, facts)
        say("scaffold", f"mode {mode}; host {host}; template {src} at {ref}")
        for token in ("PROJ_NAME", "PROJ_SLUG", "LICENSE_ID", "SCHEMA_ID", "SCHEMA_DIR", "DOCS_URL", "BASE_IRI"):
            if facts.get(token):
                say("handoff", f"{token}={facts[token]}")
        if mode == "lokf":
            pin_lokf_schema(host, dry)
        check_pin(src, ref, sha, os.environ.get("LINKML_TEMPLATE_SKIP_PIN_CHECK") == "1")
        if dry:
            stage = host / SIDECAR
        else:
            stage = Path(tempfile.mkdtemp(prefix=STAGING_PREFIX, dir=str(host)))
            os.chmod(stage, 0o755)
            _stage = stage
        preseed(host, stage, facts, mode, dry, adopt)
        if not dry:
            refuse_clashes(host, stage)
        run_copier(host, stage, facts, src, ref, dry)
        after_copy(host, stage, facts, mode, ref, dry, adopt)
        land(host, stage, dry)
        stage = None
        if mode == "lokf":
            wire_lokf(host, facts, dry)
        pointers(host, facts, mode, args.gitignored, dry, adopted=bool(adopt))
        if adopt:
            adoption_handoff(host, facts)
        say("handoff", f"sidecar {'would be ' if dry else ''}laid down in {SIDECAR}/ ({'gitignored' if args.gitignored else 'to be committed'}); validation not yet run")
        say("next", f"just --justfile {SIDECAR}/justfile install && just --justfile {SIDECAR}/justfile lint && just --justfile {SIDECAR}/justfile test")
        if mode == "lokf":
            say("next", "cd .lokf && just lokf-validate && just lokf-check-refs")
        return 0
    except Refused as exc:
        say("scaffold", f"{'refused' if exc.code == 3 else 'failed'} ({exc.code}): {exc}")
        return exc.code
    finally:
        # Whatever stopped the run, only the staging directory goes; .linkml/ is
        # never removed here, whoever made it.
        if stage is not None and stage.name.startswith(STAGING_PREFIX) and stage.is_dir():
            shutil.rmtree(stage, ignore_errors=True)
            say("scaffold", f"removed the staging directory; {SIDECAR}/ was not touched")


def validate_light(facts):
    if not facts.get("PROJ_SLUG"):
        raise Refused(2, "the sidecar records no project_slug; set PROJ_SLUG")


if __name__ == "__main__":
    sys.exit(main())
