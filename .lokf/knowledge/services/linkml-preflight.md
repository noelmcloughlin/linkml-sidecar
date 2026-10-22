---
type: Service
id: https://noelmcloughlin.github.io/linkml-sidecar/knowledge/services/linkml-preflight
title: linkml-preflight.sh
description: "The read-only preflight both skills run first: one screen of ok, warn, missing and info lines about the host's shell, git, forge, uv, copier, just and network, where a LinkML schema project or schema file sits, how to run the tools on it and how many people have committed to it, a .lokf/ bundle and Pages, ending in a summary line of what is missing and which steps that disables."
resource: skills/linkml-sidecar/templates/scripts/linkml-preflight.sh
tags:
  - preflight
  - prerequisites
isPartOf:
  - https://noelmcloughlin.github.io/linkml-sidecar/knowledge/playbooks/linkml-sidecar-skill
sources:
  - resource: skills/linkml-sidecar/templates/scripts/linkml-preflight.sh
  - resource: skills/linkml-sidecar/references/prerequisites.md
  - resource: skills/linkml-sidecar/references/layouts.md
  - resource: skills/linkml-sidecar/SKILL.md
generated:
  by: process:ktl-librarian
  at: "2026-10-22T12:07:45Z"
status: draft
verified:
  - by: process:ktl-librarian
    at: "2026-10-22T15:14:26Z"
---

# Overview

`templates/scripts/linkml-preflight.sh` says what a host can and cannot do for the two skills, on one read-only screen. linkml-sidecar runs it first, from the skill's directory, naming the host's root. The scaffold installs a copy at `.linkml/scripts/linkml-preflight.sh`. linkml-author runs that copy, or this one, to find the schema and the way to run the tools on it.

Each line is `ok`, `warn`, `missing` or `info`, then one summary line:

```text
Preflight: <n> missing, <m> warning(s). Missing disables: <steps>.
```

It always exits 0: the skills read the lines, and nothing here is a gate. It uses bash 3.2 and POSIX tools only, so it runs on macOS's stock bash and on Git for Windows.

## What it checks

It shows:

- the host and shell;
- whether the tree is under git, and on which forge;
- whether `uv`, `copier` and `just` run, and whether github.com and pypi.org answer;
- what the host already holds: a sidecar, a schema project elsewhere, configuration files in `.linkml/`, or schema files outside any project;
- how lint and the generators run there, on its `tools` line;
- where the generators' settings are, with an offer to move a `config.yaml` to `.linkml/generators.yaml`;
- how many people have committed to the schema folder, with bot commits counted apart and up to five names quoted as data, on its `authors` line, which linkml-author reads before offering a refactor;
- whether a `.lokf/` bundle is present, which switches on KTL mode;
- whether the host already publishes Pages;
- whether the root declares a uv workspace.

`LINKML_PREFLIGHT_OFFLINE=1` skips the two checks that reach the network, for tests and air-gapped machines.

## How it finds the schema

It finds a schema by its files, never by its folder's name. It looks for a project in `.linkml/`, at the repository root, in the directory it was started in, and in every directory one level down. Copier answers whose `_src_path` names linkml-project-copier, or a `config.public.mk`, make a project. When `config.public.mk` is absent, the answers' `project_slug` names the schema. A second project is reported on an `also` line. With no project anywhere, it finds schema files by content and prints each on an `ok schema` line.

Only `.linkml/.copier-answers.yml` means a sidecar. A `.linkml/` holding other files is reported as holding configuration files, or as empty. Beside a `.lokf/` bundle, the `lokf` line says whether `.lokf/justfile` names the schema, and the schema is not the bundle's domain schema until it does. `skills/linkml-sidecar/references/layouts.md` states the rule.

## When a line needs someone else

`skills/linkml-sidecar/references/prerequisites.md` translates each line: what it means, what it stops, who normally puts it right, and what to send that person. The contract checks that every line the preflight can print as missing or a warning has a row there.
