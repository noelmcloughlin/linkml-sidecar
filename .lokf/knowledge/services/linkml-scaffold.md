---
type: Service
id: https://noelmcloughlin.github.io/linkml-sidecar/knowledge/services/linkml-scaffold
title: linkml-scaffold.sh
description: "The scaffold script that does Steps 1 to 3 of linkml-sidecar in one deterministic run: it verifies the template pin, pre-seeds the skill's own files, runs copier, neutralises root assumptions, wires a KTL bundle, adds the root pointers, and exits 0, 2, 3, 4 or 5."
resource: skills/linkml-sidecar/scripts/linkml-scaffold.sh
tags:
  - scaffold
  - copier
  - exit codes
isPartOf:
  - https://noelmcloughlin.github.io/linkml-sidecar/knowledge/playbooks/linkml-sidecar-skill
dependsOn:
  - https://noelmcloughlin.github.io/linkml-sidecar/knowledge/references/linkml-project-copier
references:
  - https://noelmcloughlin.github.io/linkml-sidecar/knowledge/glossary/template-pin
  - https://noelmcloughlin.github.io/linkml-sidecar/knowledge/references/template-assumptions
sources:
  - resource: skills/linkml-sidecar/scripts/linkml-scaffold.sh
  - resource: skills/linkml-sidecar/scripts/linkml-scaffold.py
  - resource: skills/linkml-sidecar/SKILL.md
generated:
  by: process:ktl-librarian
  at: "2026-10-21T22:30:32Z"
status: draft
---

# Overview

`scripts/linkml-scaffold.sh` is the driver and `scripts/linkml-scaffold.py` its Python half. Nothing in it is a judgement: the facts come in as environment variables that the skill's Step 0 resolved from real sources.

```text
linkml-scaffold.sh [--dry-run] [--host DIR] [--mode plain|lokf|auto]
                   [--gitignored] [--pointers-only] [--repair PATH]
```

The facts are `PROJ_NAME`, `PROJ_SLUG`, `PROJ_DESC`, `GITHUB_ORG`, `REPO_URL`, `FULL_NAME`, `EMAIL`, `LICENSE_ID`, `SCHEMA_ID` and `DOCS_URL`, with `BASE_IRI` read from `.lokf/knowledge/index.md` when it is absent.

## What it does, in order

1. Refuses an existing `.linkml/`, a visible `linkml/` with answers, or answers at the root.
2. Checks the facts against the template's own rules.
3. In KTL mode, pins `.lokf/lokf.yaml` out of the installed toolkit.
4. Verifies the pin: the tag must name the commit the driver records before the template runs with `--trust`.
5. Pre-seeds the files the skill owns, substituting facts as literal text through Python's `str.replace`, never sed.
6. Runs copier for everything else.
7. Neutralises the root assumptions that remain.
8. In KTL mode, edits `.lokf/justfile` to name the schema.
9. Adds the root pointers, then prints the hand-off facts.

Every line it prints starts with `scaffold:`, `handoff:` or `next:`.

## Exit codes

- `0`: done.
- `2`: a usage error, a bad fact or a missing tool.
- `3`: refused, because a sidecar exists.
- `4`: copier failed; the scaffold removes the unfinished `.linkml/`.
- `5`: an overlay or a pointer failed.

The driver holds the one template pin, `LINKML_TEMPLATE_REF` and `LINKML_TEMPLATE_SHA`.
