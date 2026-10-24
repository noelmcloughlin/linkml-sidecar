---
type: Service
id: https://w3id.org/ktl/linkml-sidecar/knowledge/services/linkml-scaffold
title: linkml-scaffold.sh
description: "The scaffold script that does Steps 1 to 3 of linkml-sidecar in one deterministic run: it verifies the template pin, stages the skill's files and copier's output, moves them into .linkml/ around what is already there, keeps the generators' settings in generators.yaml, adopts a schema the host holds with --adopt, names the schema in a KTL bundle's justfile, adds the root pointers, and exits 0, 2, 3, 4 or 5."
resource: skills/linkml-sidecar/scripts/linkml-scaffold.sh
tags:
  - scaffold
  - copier
  - exit codes
isPartOf:
  - https://w3id.org/ktl/linkml-sidecar/knowledge/playbooks/linkml-sidecar-skill
dependsOn:
  - https://w3id.org/ktl/linkml-sidecar/knowledge/references/linkml-project-copier
references:
  - https://w3id.org/ktl/linkml-sidecar/knowledge/glossary/template-pin
  - https://w3id.org/ktl/linkml-sidecar/knowledge/references/template-assumptions
sources:
  - resource: skills/linkml-sidecar/scripts/linkml-scaffold.sh
  - resource: skills/linkml-sidecar/scripts/linkml-scaffold.py
  - resource: skills/linkml-sidecar/SKILL.md
generated:
  by: process:ktl-librarian
  at: "2026-10-22T18:19:05Z"
status: draft
verified:
  - by: process:ktl-librarian
    at: "2026-10-22T15:14:26Z"
---

# Overview

`scripts/linkml-scaffold.sh` is the driver and `scripts/linkml-scaffold.py` its Python half. Nothing in it is a judgement: the facts come in as environment variables that the skill's Step 0 resolved from real sources.

The driver runs the Python half through `uv run` first, which reads the half's own `# /// script` header and so passes over a python3 older than 3.8, such as RHEL 8's 3.6. Without uv, it uses python3, and python as the last resort, each only when it is 3.8 or later. The half needs only the standard library, so its header names no package for a mirror to refuse. With none of these, the driver exits 2.

```text
linkml-scaffold.sh [--dry-run] [--host DIR] [--mode plain|lokf|auto]
                   [--gitignored] [--adopt SCHEMA | --dummy]
                   [--pointers-only] [--repair PATH]
```

The facts are `PROJ_NAME`, `PROJ_SLUG`, `PROJ_DESC`, `GITHUB_ORG`, `REPO_URL`, `FULL_NAME`, `EMAIL`, `LICENSE_ID`, `SCHEMA_ID` and `DOCS_URL`, with `BASE_IRI` read from `.lokf/knowledge/index.md` when it is absent. With `--adopt`, `PROJ_SLUG` and `SCHEMA_ID` come from the schema file itself.

## What it does, in order

1. Refuses a sidecar in `.linkml/`, a schema project at the root or one directory down, and a `.linkml/` holding project files without answers. It refuses a schema the host already holds unless `--adopt` or `--dummy` says what to do. It installs around configuration files alone in `.linkml/`.
2. Checks the facts against the template's own rules. An adopted schema's `id` is exempt, since it was chosen before.
3. In KTL mode, pins `.lokf/lokf.yaml` out of the installed toolkit.
4. Verifies the pin: the tag must name the commit the driver records before the template runs with `--trust`.
5. Pre-seeds the files the skill owns into a staging directory beside `.linkml/`, substituting facts as literal text through Python's `str.replace`, never sed.
6. Runs copier for everything else, into the same staging directory.
7. Neutralises the root assumptions that remain. With `--adopt`, it points `config.public.mk`'s `LINKML_SCHEMA_SOURCE_DIR` at the schema's folder, relative to `.linkml/`. It renames `config.yaml` to `generators.yaml` and names it in `config.public.mk`, unless the host already keeps a `.linkml/generators.yaml`.
8. Moves the staged files into `.linkml/`, around whatever is already there. A name both hold is a clash: nothing moves, and the run ends with exit 3.
9. In KTL mode, edits `.lokf/justfile` to name the schema.
10. Adds the root pointers, then prints the hand-off facts.

Every line it prints starts with `scaffold:`, `handoff:` or `next:`. It never removes anything but its own staging directory, so a failed run leaves `.linkml/` as it was.

`--repair generators.yaml` moves a finished project's `config.yaml` to `.linkml/generators.yaml`: the sidecar's, or a root project's into `.linkml/`. It changes the one line of `config.public.mk` that names the file, and moves nothing when it cannot finish. After the move, `copier update` leaves the file alone, so the template's later changes to its settings no longer arrive.

## Exit codes

- `0`: done.
- `2`: a usage error, a bad fact or a missing tool.
- `3`: refused, because a project, a schema or a file already there stands in the way.
- `4`: copier failed.
- `5`: an overlay or a pointer failed.

The driver holds the one template pin, `LINKML_TEMPLATE_REF` and `LINKML_TEMPLATE_SHA`.
