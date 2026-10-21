---
type: Reference
id: https://noelmcloughlin.github.io/linkml-sidecar/knowledge/references/linkml-project-copier
title: linkml-project-copier
description: The upstream copier template (MIT) that every sidecar is made from, pinned at tag v0.5.0 and verified against the commit the scaffold driver records before it runs with --trust.
genre: reference
resource: https://github.com/linkml/linkml-project-copier
tags:
  - copier
  - template
  - upstream
references:
  - https://noelmcloughlin.github.io/linkml-sidecar/knowledge/glossary/template-pin
sources:
  - resource: skills/linkml-sidecar/SKILL.md
  - resource: skills/linkml-sidecar/scripts/linkml-scaffold.sh
  - resource: README.md
generated:
  by: process:ktl-librarian
  at: "2026-10-21T22:30:32Z"
status: draft
---

# Overview

[linkml-project-copier](https://github.com/linkml/linkml-project-copier) is the LinkML project template, run by copier as `gh:linkml/linkml-project-copier`. Its licence is MIT. The sidecar's project shape comes from it at tag **v0.5.0**, the one pin, held in `skills/linkml-sidecar/scripts/linkml-scaffold.sh` and verified against the commit it names before the template is trusted.

Copier needs `--trust` for this template, because it runs a Jinja extension and migrations, which is why the pin is checked first. The template is built for a repository that is itself a schema project, so the scaffold neutralises what it assumes of a root.
