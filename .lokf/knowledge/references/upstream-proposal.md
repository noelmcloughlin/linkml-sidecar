---
type: Document
id: https://noelmcloughlin.github.io/linkml-sidecar/knowledge/references/upstream-proposal
title: Upstream layout proposal
description: A draft, not yet filed, for an issue on linkml/linkml-project-copier proposing a layout answer (root or sidecar) and a sidecar_dir, which would remove most rows of the template assumptions catalogue; filing it is a person's call.
genre: explanation
resource: skills/linkml-sidecar/references/upstream-proposal.md
tags:
  - upstream
  - copier
  - layout
about:
  - https://noelmcloughlin.github.io/linkml-sidecar/knowledge/references/linkml-project-copier
references:
  - https://noelmcloughlin.github.io/linkml-sidecar/knowledge/references/template-assumptions
sources:
  - resource: skills/linkml-sidecar/references/upstream-proposal.md
generated:
  by: process:ktl-librarian
  at: "2026-10-21T22:30:32Z"
status: draft
---

# Overview

`skills/linkml-sidecar/references/upstream-proposal.md` is a draft for an issue on [linkml/linkml-project-copier](https://github.com/linkml/linkml-project-copier), to file when the maintainer of this skill decides to. Filing it is a person's call, not the skill's.

It follows the template maintainer's reply on issue #151 (2026-05-24) that a layout putting "everything except `.github` into a single folder" should be doable, and the sidecar item on the v1.0.0 wishlist in issue #93.

## What it proposes

- `layout`: `root` (today's behaviour) or `sidecar`.
- `sidecar_dir`: the folder name, default `.linkml`, asked only when `layout` is `sidecar`.
- With `sidecar`, the template would:
  - render the workflows at the repository root with the sidecar as their working directory;
  - render no `CODE_OF_CONDUCT.md`, `CONTRIBUTING.md` or `dependabot.yml`;
  - make `setup` skip the git steps;
  - make `deploy` publish under a subpath or refuse;
  - set `site_url` to the host's Pages URL plus `/<sidecar_dir>/`.

Copier itself already handles the subfolder; only the template's rendering assumes a root.
