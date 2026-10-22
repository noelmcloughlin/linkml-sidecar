---
type: GlossaryTerm
id: https://noelmcloughlin.github.io/linkml-sidecar/knowledge/glossary/the-gate
title: The gate
description: "linkml-author's check after every schema edit: lint, then gen-project, then test, through the project's justfile or Makefile, or the three LinkML tools directly for a schema with no project, with lokf validate after it beside a KTL bundle that names the schema."
definition: "The three recipes linkml-author runs after every schema edit, in order: lint, gen-project and test."
resource: skills/linkml-author/SKILL.md
tags:
  - gate
  - linkml-lint
  - gen-project
  - just test
sources:
  - resource: skills/linkml-author/SKILL.md
generated:
  by: process:ktl-librarian
  at: "2026-10-22T01:26:03Z"
status: draft
---

# Overview

**The gate** is what linkml-author runs after every schema edit, in this order:

```bash
just --justfile <project>/justfile lint          # linkml-lint, the recommended rules: warnings fail it
just --justfile <project>/justfile gen-project   # every generator in config.yaml
just --justfile <project>/justfile test          # generate into tmp/, pytest, then the example runner
```

`just test` runs no lint, so `lint` comes first. A generator that fails on a schema `lint` accepted is a schema error too. A project with a `Makefile` runs the same targets through `make`.

A schema on its own has no recipes. Its gate is `linkml-lint <schema>`, then `gen-project` into a temporary folder, then `linkml-validate` over whatever example data the host keeps, each through the host's environment.

Example data sits beside the schema's tests: a file under `tests/data/valid/<ClassName>-<anything>.yaml` must validate against that class, and one under `tests/data/invalid/` must fail. Beside a KTL bundle that names the schema, `cd .lokf && just lokf-validate && just lokf-check-refs` follows the gate.
