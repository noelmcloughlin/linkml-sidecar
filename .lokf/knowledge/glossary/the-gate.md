---
type: GlossaryTerm
id: https://noelmcloughlin.github.io/linkml-sidecar/knowledge/glossary/the-gate
title: The gate
description: "linkml-author's check after every schema edit: just lint, then just gen-project, then just test, run through the project's justfile, with lokf validate after it beside a KTL bundle."
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
  at: "2026-10-21T22:30:32Z"
status: draft
---

# Overview

**The gate** is what linkml-author runs after every schema edit, in this order:

```bash
just --justfile .linkml/justfile lint          # linkml-lint, the recommended rules: warnings fail it
just --justfile .linkml/justfile gen-project   # every generator in config.yaml
just --justfile .linkml/justfile test          # generate into tmp/, pytest, then the example runner
```

`just test` runs no lint, so `lint` comes first. A generator that fails on a schema `lint` accepted is a schema error too. Example data sits beside the schema's tests: a file under `tests/data/valid/<ClassName>-<anything>.yaml` must validate against that class, and one under `tests/data/invalid/` must fail. Beside a KTL bundle, `cd .lokf && just lokf-validate && just lokf-check-refs` follows the gate.
