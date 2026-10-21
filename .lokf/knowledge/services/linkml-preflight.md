---
type: Service
id: https://noelmcloughlin.github.io/linkml-sidecar/knowledge/services/linkml-preflight
title: linkml-preflight.sh
description: "The read-only preflight both skills run first: one screen of ok, warn, missing and info lines about the host's shell, git, forge, uv, copier, just, network, an existing sidecar, a .lokf/ bundle and Pages, ending in a summary line of what is missing and which steps that disables."
resource: skills/linkml-sidecar/templates/scripts/linkml-preflight.sh
tags:
  - preflight
  - prerequisites
isPartOf:
  - https://noelmcloughlin.github.io/linkml-sidecar/knowledge/playbooks/linkml-sidecar-skill
sources:
  - resource: skills/linkml-sidecar/templates/scripts/linkml-preflight.sh
  - resource: skills/linkml-sidecar/references/prerequisites.md
  - resource: skills/linkml-sidecar/SKILL.md
generated:
  by: process:ktl-librarian
  at: "2026-10-21T22:30:32Z"
status: draft
---

# Overview

`templates/scripts/linkml-preflight.sh` says what a host can and cannot do for the two skills, on one read-only screen. linkml-sidecar runs it first, from the skill's directory, naming the host's root. The scaffold installs a copy at `.linkml/scripts/linkml-preflight.sh`, which linkml-author runs to find the project.

Each line is `ok`, `warn`, `missing` or `info`, then one summary line:

```text
Preflight: <n> missing, <m> warning(s). Missing disables: <steps>.
```

It always exits 0: the skills read the lines, and nothing here is a gate. It uses bash 3.2 and POSIX tools only, so it runs on macOS's stock bash and on Git for Windows.

## What it checks

It shows the host and shell; whether the tree is under git and on which forge; whether `uv`, `copier` and `just` run and whether github.com and pypi.org answer; whether a sidecar already exists, and in which shape; whether a `.lokf/` bundle is present, which switches on KTL mode; whether the host already publishes Pages; and whether the root declares a uv workspace.

`LINKML_PREFLIGHT_OFFLINE=1` skips the two checks that reach the network, for tests and air-gapped machines.

## When a line needs someone else

`skills/linkml-sidecar/references/prerequisites.md` translates each line: what it means, what it stops, who normally puts it right, and what to send that person. The contract checks that every line the preflight can print as missing or a warning has a row there.
