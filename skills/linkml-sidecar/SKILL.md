---
name: linkml-sidecar
description: 'Install a `.linkml/` LinkML schema sidecar (a pinned linkml-project-copier project with its generators, docs and tests, a dummy schema, and a `linkml_schema` doorway link beside it) in the repository this skill sits in, without touching the host''s build, or give a schema the repository already holds that toolchain in place (`--adopt`). Use when: a repo has no LinkML schema project yet and someone asks to add, scaffold, bootstrap or set up a LinkML sidecar, schema project, data model or domain schema, with or without a KTL `.lokf/` bundle; or to repair a missing or broken sidecar file. Not for authoring classes, slots or enums; that is the linkml-author skill, which this one hands off to when done. Keywords: LinkML, schema, data model, copier, linkml-project-copier, sidecar, JSON Schema, Pydantic, OWL, SHACL, LOKF, KTL, domain schema.'
license: Apache-2.0
compatibility: 'Requires bash (Git for Windows on Windows) and uv, which runs copier, just and the project''s own Python; one network run to github.com and pypi.org for the scaffold; Python 3.10+ for the project. Any forge or none; Step 5''s workflow is GitHub Actions. Works with or without a `.lokf/` KTL bundle.'
---

# linkml-sidecar

Create a fresh **`.linkml/` sidecar** inside the repository this skill is invoked from. It is a complete [LinkML](https://linkml.io) schema project made by [linkml-project-copier](https://github.com/linkml/linkml-project-copier): the schema in one file, every generator (JSON Schema, Pydantic, OWL, SHACL, TypeScript, a docs site) one recipe away, a small **dummy** schema, and nothing changed in the host's build. A schema the repository already holds gets the same toolchain around it, where it is (`--adopt`). Then hand off to **linkml-author** to replace the dummy with the real model. One script, `scripts/linkml-scaffold.sh`, does Steps 1 to 3 (paths below are relative to this skill's directory). The files this skill owns come from `templates/`, never retyped, and everything else comes from the template at its pin.

> Sources: linkml.io is the canonical site for what LinkML *means*. The project shape comes from `gh:linkml/linkml-project-copier` at tag **v0.5.0** (MIT), the one pin, held in `scripts/linkml-scaffold.sh` and verified against the commit it names before the template is trusted. Copier needs `--trust` for this template (a Jinja extension and migrations), which is why the pin is checked first. What the template assumes of a repository root, and what this skill does about each assumption, is [references/template-assumptions.md](references/template-assumptions.md). Where a schema may live and how the skills find it is [references/layouts.md](references/layouts.md).

> Model: a small/mid-tier model is enough here: Step 0 is structured file lookup, Step 1 is one script run. Mistakes are caught by Step 3's grep, Step 4's gate and Step 6's human sign-off. **linkml-author** is the opposite case: keep it on the calling agent's normal model.

## Scope

- **This skill** runs **once**, to create `.linkml/` (around the dummy, or around a schema the host already holds), to **repair** one file it owns (`--repair`), or to re-add the root pointers (`--pointers-only`). It never authors classes.
- **linkml-author** runs **often**, to turn the dummy into the host's model and keep it generated, documented and tested.

> Guardrails: `.linkml/.copier-answers.yml` means a sidecar exists; use linkml-author instead. A `.linkml/` holding only configuration files is installed around, never emptied; a name both hold is refused. A schema project anywhere else (copier answers naming the template, or `config.public.mk`; [references/layouts.md](references/layouts.md)) is reported and never migrated unasked; linkml-author works there. Never lay the dummy beside a schema the host already holds unless asked (`--dummy`). Never run `just setup` (it runs `git init` and commits, nesting a repository inside the host) or `just deploy` (it pushes the host's `gh-pages` branch root). Never edit a template-owned file by hand; `just update` is how those change. Non-git, non-GitHub or non-POSIX host: see [references/portability.md](references/portability.md).

**Three cases, one skill.** A repository that *is* a schema project (lmodel/gist, say) runs copier at its root itself, in one command, and needs nothing here. A domain codebase whose maintainers would resist a schema project in their root folder gets the sidecar: one hidden folder, one visible doorway, one workflow, and a README that says so. A repository that holds a schema but no project (most of them) gets the sidecar around that schema, untouched where it lies.

## Step 0 - Gather the host project's facts

**First, the preflight.** Run `bash templates/scripts/linkml-preflight.sh <host-root>` from this skill's directory (the copy under `.linkml/scripts/` does not exist yet), naming the host's root. Without it the script reports on the tree it sits in, which is wrong when the skill is installed outside the host. Read its screen before anything else. It shows:

- the host and shell;
- whether the tree is under git, and on which forge;
- whether `uv`, `copier` and `just` run here, and whether github.com and pypi.org answer;
- what the host already holds: a project, configuration files in `.linkml/`, or schema files outside any project;
- whether a `.lokf/` bundle is present, which switches on **KTL mode**;
- whether the host already publishes Pages (a docs collision);
- whether the root declares a uv workspace.

Its last line names what is missing and which steps that disables; repeat that line in the Step 6 hand-off. When the person you are working with cannot act on a `missing` or `warn` line themselves, write them a request note from [references/prerequisites.md](references/prerequisites.md), which gives each line's meaning, who fixes it, and what to send.

**Dummy or adoption: decide now.** A `schema` line means the host already holds one. One file: run Step 1 with `--adopt <file>`. Several: ask the person which, or, unattended, list them and stop. The scaffold refuses the dummy beside an existing schema unless `--dummy` says so. The file must be `<slug>.yaml` (the template names the schema after the slug); one that is not, or that a new schema should import instead, takes the dummy and linkml-author's import.

Resolve every fact from real project sources before running anything; the scaffold refuses a missing or malformed one, and never leaves a `<...>` token behind.

| Fact | Meaning | Where to find it |
| --- | --- | --- |
| `PROJ_NAME` | Human-readable project name; the template's `project_name` | repo name, manifest `name` (`package.json`, `pyproject.toml`, `Cargo.toml`, `go.mod`, ...), root `README.md` title. Letters, digits, space, `-`, `_`; starts with a letter, ends alphanumeric |
| `PROJ_SLUG` | Python package and schema name, snake_case | derived from `PROJ_NAME` (`Acme Platform` becomes `acme_platform`); at least two characters; the scaffold derives it when unset. With `--adopt`, the schema file's stem, and nothing else |
| `PROJ_DESC` | One-sentence description | manifest `description`, README intro |
| `GITHUB_ORG`, `REPO_URL` | Owner and the repository's URL | `git remote get-url origin`; any forge |
| `FULL_NAME`, `EMAIL` | The schema's author | `git config user.name` / `user.email`, manifest authors, `CODEOWNERS` |
| `LICENSE_ID` | SPDX id of the host's license | the root `LICENSE` text or the manifest's `license`; one of `Apache-2.0`, `MIT`, `BSD-3-Clause`, `MPL-2.0`, `LGPL-3.0-only`, `GPL-3.0-only`, else `LicenseRef-Custom`. No license file: `LicenseRef-Custom`, which the scaffold insists on, and it writes a stub that says so; flag it |
| `SCHEMA_ID` | The schema's `id` IRI, with no trailing `/`; the scaffold adds the `/` for its prefix's namespace | With `--adopt`, the schema's own `id`, which stands whatever it is. Otherwise, in order: (1) In KTL mode, the bundle's `base_iri` authority plus `/schema/<slug>`. (2) A persistent-identifier namespace the project already publishes under (w3id.org, purl.org, an owned domain). (3) The docs `site_url`, unless it is on a code host's pages (`github.io`), which the scaffold refuses like the repo URL. (4) Else `https://<slug>.example/schema/<slug>`, flagged for review. **Never** the code-host repo URL: that path space is not the project's, so the IRIs could never resolve |
| `DOCS_URL` | Where the sidecar's docs site will live | the host's Pages URL plus `/linkml/`, else `https://<org>.github.io/<repo>/linkml/`, flagged |
| `BASE_IRI` | KTL mode only; the dummy concept's `id` | `.lokf/knowledge/index.md`; the scaffold reads it when unset |

`SCHEMA_ID` matters most: every class and slot IRI starts with it. It need not resolve today, but must be stable and in a namespace the project controls, and a w3id redirect to `DOCS_URL` later makes every generated page's IRI a link that works.

**Tracked or gitignored: decide now.** Check whether the root `.gitignore` already excludes `.linkml/` (ask if unclear). Committing `.linkml/` is the default both skills assume. Gitignoring it is equally valid, for a personal sidecar or under a policy against committing agent-authored content. It changes four things:

- still create every file;
- skip the Step 4 commit and Step 5 entirely;
- run the scaffold with `--gitignored`, which adds `.linkml/` and `linkml_schema` to the root `.gitignore`;
- say so in Step 6.

The scaffold refuses `--gitignored` when `.linkml/` already holds tracked files: the line would hide them.

**KTL mode.** When `.lokf/` exists, the sidecar's dummy schema becomes the bundle's *domain schema*. It imports LOKF's core schema, every class in it that is `is_a: Concept` is a type the bundle's concepts may carry, and `lokf validate --schema` checks the bundle against both. The scaffold pins `.lokf/lokf.yaml` out of the installed toolkit when it is absent, writes a dummy that imports it and a lint config that excuses LOKF's own camelCase slot names, and names the schema in `.lokf/justfile`. [references/ktl.md](references/ktl.md) says what each piece does, what ktl-librarian's recipe asks for, and the one upstream bug the justfile edit works around. An adopted schema is not made the domain schema: the scaffold runs in plain mode and says so in the hand-off. linkml-author connects it later if its maintainers want that.

## Step 1 - Scaffold

Export the facts, read the plan, then run it:

```bash
export PROJ_NAME PROJ_SLUG PROJ_DESC GITHUB_ORG REPO_URL FULL_NAME EMAIL LICENSE_ID SCHEMA_ID DOCS_URL
bash scripts/linkml-scaffold.sh --dry-run    # every action it would take, and the answers copier would get
bash scripts/linkml-scaffold.sh              # add --gitignored when Step 0 decided so; --adopt <file> to build around the host's schema
```

Run it from the host's root (`--host DIR` otherwise). Every line it prints starts with `scaffold:`, `handoff:` or `next:`; keep the `handoff:` lines for Step 6. It exits 0 when done, 2 on a bad fact or a missing tool, 3 when refused (a project, a schema or a file already there stands in the way), 4 when copier failed, 5 when an overlay failed. It never removes anything but its own staging directory. In order, it:

1. **Refuses** a sidecar in `.linkml/`, a schema project at the root or one directory down, a `.linkml/` holding project files without answers, and, without `--adopt` or `--dummy`, a schema the host already holds. It installs around configuration files alone in `.linkml/`.
2. **Checks the facts** against the template's own rules (the name and slug patterns, the license list, an IRI that names no code host; an adopted schema's `id` is exempt, since it was chosen before).
3. **Pins `.lokf/lokf.yaml`** in KTL mode, out of the installed toolkit (`uv sync` in `.lokf/` first), and stops before writing anything if that cannot be done.
4. **Verifies the pin**: `git ls-remote` on the template, and the tag must name the commit the script records. Only then is the template run with `--trust`.
5. **Pre-seeds the files this skill owns** into a staging directory beside `.linkml/`, substituting the facts as literal text through Python's `str.replace`, never sed (a value holding sed's delimiter would change the command, not the text):

   | Template | Destination in `.linkml/` |
   | --- | --- |
   | the host's `LICENSE` (or `templates/linkml/LICENSE.missing`) | `LICENSE` |
   | `templates/linkml/README.md` | `README.md`: the sidecar's own README, with the ownership map and the never-run list; with `--adopt`, a section that says where the schema is |
   | `templates/linkml/docs/index.md`, `docs/about.md` | `docs/index.md`, `docs/about.md` |
   | `templates/linkml/schema/plain/` or `schema/lokf/` | `src/<slug>/schema/<slug>.yaml` (DUMMY; linkml-author replaces), `tests/test_data.py`, `tests/data/**` (in KTL mode the valid example sits under `problem/valid/`, which the example runner skips: [references/ktl.md](references/ktl.md)). With `--adopt`: `tests/test_data.py` alone, and `src/<slug>/schema/README.md` saying where the schema is |
   | `templates/scripts/linkml-preflight.sh` | `scripts/linkml-preflight.sh` (`chmod +x`): linkml-author runs it to find the project |

   Each is in the template's `_skip_if_exists` list or outside the template, so copier leaves it alone now and on every `just update`.
6. **Runs copier** for everything else, into the same staging directory: `uvx --from 'copier>=9.4.0,<10' --with jinja2-time copier copy --trust --defaults --vcs-ref v0.5.0 --data-file <answers> gh:linkml/linkml-project-copier <staging>`, the answers rendered from `templates/answers.yml`. Four answers are fixed and make the project a sidecar: `add_example: false` (the upstream example fails `just lint`, and copier would recreate a deleted one on update), `gh_action_pypi: false` and `gh_action_docs_preview: false` (inert inside `.linkml/`), `existing_license_file: LICENSE` (the pre-seeded copy).
7. **Neutralises the root assumptions** that remain: the `site_url` and `repo_url` lines of `mkdocs.yml` become `DOCS_URL` and `REPO_URL`; the `linkml-link` recipe is appended to `project.justfile` (the file copier merges); in KTL mode `config.public.mk` gets `--render-imports` for gen-doc and `.linkmllint.yaml` is written. With `--adopt`, `config.public.mk`'s `LINKML_SCHEMA_SOURCE_DIR` is pointed at the schema's folder instead, relative to `.linkml/`, and no doorway recipe is added. It checks that no `.linkml/.git` appeared and that `.copier-answers.yml` records the pin.
8. **Moves the staged files into `.linkml/`**, around whatever is already there. A name both hold is a clash: nothing moves, the names are printed, and the run ends with exit 3. A failure at any earlier step removes the staging directory and nothing else.
9. **Wires `.lokf/justfile`** in KTL mode: `schema :=` and the two validate recipes, by exact match on ktl-sidecar's template lines; a justfile that differs gets the edit printed instead.
10. **Adds the Step 2 pointers**, then prints the hand-off facts and the Step 4 commands.

`--repair PATH` rewrites one owned file of a finished sidecar (the preflight, the README, the docs pages, `LICENSE`, a dummy file, `.linkmllint.yaml` in KTL mode, `project.justfile`'s doorway recipe, or an adopted sidecar's `src/<slug>/schema/README.md`). It reads the facts back from the sidecar's answers and config. `just update` restores a template-owned file.

## Step 2 - Point people and agents at the schema (root-level, add-only)

The scaffold makes three additions at the **repo root**, outside `.linkml/`; `--pointers-only` makes them again on a finished sidecar. Add only, never overwrite, and check for an existing item first. All three stay true **whether or not `.linkml/` exists later**, so nothing ever needs cleaning up if the sidecar is removed. An adopted schema gets none of the three: it is already visible where it lies, and the hand-off says to mention `.linkml/`'s recipes where the host documents it.

- **README aside**: if `README.md` exists and does not already name `.linkml/`, `templates/readme-for-schema.md` goes in after the intro, before the first `##`. It is one blockquote that says the model is a sidecar, where the schema is, which skill edits it, and that an agent reads the schema before the code. Do not invent a README on a host that has none.
- **`llms.txt`**: created from `templates/llms.txt` if absent; otherwise the `## Schema` section (`templates/llms-section.md`, or the KTL variant) is appended, only if the file does not already name `.linkml/`.
- **`linkml_schema` doorway**: `ln -s .linkml/src/<slug>/schema linkml_schema`, the schema folder under an ordinary, visible name beside the hidden `.linkml/`. Finder and most folder pickers hide dot-directories, so the doorway is the one name a person needs to know. The target is relative, which keeps the link valid after a clone or move; `just --justfile .linkml/justfile linkml-link` recreates it on a machine where a sync service dropped it. POSIX only: on Windows a junction does the job (`mklink /J linkml_schema .linkml\src\<slug>\schema`); on a filesystem without links, skip it. Mirror the Step 0 decision: commit it beside a tracked `.linkml/`, or it joins the root `.gitignore` with `--gitignored`.

If the host lints, spell-checks or link-checks `**/*.md` repo-wide, exclude `.linkml/` and `linkml_schema/` from that config: the generated docs are not the host's prose, and the same schema folder would otherwise be processed twice.

## Step 3 - Verify the skeleton

Check for placeholder tokens only; the files legitimately contain other angle brackets:

```bash
grep -rn -e '<PROJ_' -e '<SCHEMA_ID>' -e '<SCHEMA_DIR>' -e '<DOCS_URL>' -e '<BASE_IRI>' -e '<LICENSE_ID>' -e '<TODAY>' -e '<REPO_URL>' -e '<TEMPLATE_REF>' .linkml/ linkml_schema/ llms.txt README.md --exclude-dir=.venv 2>/dev/null
test ! -e .linkml/.git && grep -q '^_commit: v0.5.0$' .linkml/.copier-answers.yml && grep -c 'linkml-sidecar: the linkml_schema doorway' .linkml/project.justfile
```

Zero hits from the grep, no nested repository, the pin recorded, the recipe block once. With `--adopt` there is no recipe block; check that `LINKML_SCHEMA_SOURCE_DIR` in `.linkml/config.public.mk` names the schema's folder and that the schema file is as it was. Leave the dummy as a dummy; do not start the real model here.

## Step 4 - Validate the skeleton

```bash
just --justfile .linkml/justfile install   # uv sync --group dev; writes .linkml/uv.lock
just --justfile .linkml/justfile lint      # linkml-lint, the recommended rules
just --justfile .linkml/justfile test      # generate into tmp/, pytest, run the examples (it does not lint)
```

`just` runs each recipe inside `.linkml/`, so these work from the host's root; `uvx --from rust-just just` stands in for an uninstalled `just`. Fix findings, then commit `.linkml/` **including `uv.lock`** (Step 5's workflow installs from it), unless `.linkml/` is gitignored (Step 0). In KTL mode also run `cd .lokf && just lokf-install && just lokf-validate && just lokf-check-refs`: the bundle, dummy concept and all, against LOKF's schema plus the sidecar's. A lint finding in an adopted schema is the host's to decide on, not this skill's to fix: report it. With no `git`, no `uv`, no copier or no network there is no sidecar to make and no fallback; say so plainly and stop after Step 0.

## Step 5 - Install the automation (optional)

**Skip this step if `.linkml/` is gitignored.** It has no placeholders.

| Template | Destination |
| --- | --- |
| `templates/github/linkml-sidecar.yaml` | `.github/workflows/linkml-sidecar.yaml`: on a pull request or push that touches `.linkml/**`, every step runs in `.linkml/` (`working-directory`), installs from `uv.lock` with `--locked`, then `just lint` and `just test` on one Python version. On the repository's default branch, whatever its name, a second job builds the docs site and keeps it as an artifact. A third publishes it under the `linkml/` subpath of the host's `gh-pages` branch, replacing that subpath alone, only once the repository variable `LINKML_DOCS_ENABLED` is `true` |

With `--adopt`, add the schema's folder (`"<dir>/**"`) to both `paths:` lists, so an edit to the schema runs the gate too. The template's own workflows under `.linkml/.github/` are inert there and stay as the template's copies. The host's root `dependabot.yml`, if any, can gain a `uv` entry for `/.linkml`; suggest it in one line, do not scaffold it. Check whether the host already runs ShellCheck and `actionlint` over its tree; if not, suggest coverage for `.linkml/scripts/linkml-preflight.sh` and the workflow, in one line. [references/automation.md](references/automation.md) says what each job does, the variable to set, and how to port the workflow to another forge.

## Step 6 - Hand off to linkml-author

The sidecar ends here. linkml-author's first run replaces the dummy with the host's model, from the code, data and documents the repository holds, keeping the gate green after each change; for an adopted schema it adds the example data and carries the model on. In KTL mode, ktl-librarian reads the schema the `.lokf/justfile` names and may type concepts with its classes, and ktl-curator's report counts vocabulary fit against it. In the hand-off, tell the user:

- which Step 0 values were **guessed** rather than found (`SCHEMA_ID` above all, then `LICENSE_ID` and `DOCS_URL`; every generated IRI starts with the first, so it needs sign-off);
- whether Step 4's gate ran and passed, and in KTL mode whether `lokf validate` did;
- which optional pieces (README aside, `llms.txt`, Step 5 workflow) were added, appended to, or left alone because they already existed;
- whether `.linkml/` is **git-tracked or gitignored**, and which files it already held that the sidecar was installed around;
- whether the **`linkml_schema` doorway** was created and, if not, the one command that makes it;
- the pin (`_commit: v0.5.0`) and how the template moves: `cd .linkml && just update` on a clean tree, then commit `uv.lock` and `.copier-answers.yml` with the diff;
- what the sidecar still carries from the template and ignores: the inert `.github/` and `.pre-commit-config.yaml`, and `CODE_OF_CONDUCT.md` and `CONTRIBUTING.md`, which the host's own govern;
- on a host that already publishes Pages, that `just deploy` must never run from `.linkml/` and the Step 5 docs job is scoped to `linkml/`;
- with `--adopt`:
  - that the schema was not moved, linked or changed, and `config.public.mk` names its folder;
  - that no example data exists yet;
  - that the workflow's `paths:` need the schema's folder;
  - beside a `.lokf/` bundle, that the schema is not made its domain schema;
- in KTL mode:
  - on a `.lokf/` from before ktl-sidecar's `schema` variable, that the validate step of `knowledge-registrar.yaml`, `knowledge-librarian.yaml` and `knowledge-release.yaml` should run `uvx --from rust-just==1.47.0 just lokf-check-refs`, so CI checks the bundle against the schema too;
  - that the KTL plugins' "Known LOKF types" setting needs each domain class;
  - that `.lokf/lokf.yaml` moves when the `lokf` floor does.
