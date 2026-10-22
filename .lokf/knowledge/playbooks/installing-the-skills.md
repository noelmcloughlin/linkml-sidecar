---
type: Playbook
id: https://noelmcloughlin.github.io/linkml-sidecar/knowledge/playbooks/installing-the-skills
title: Installing the skills
description: How to install linkml-sidecar and linkml-author with npx skills or as a Claude Code plugin, and how to run the preflight and the scaffold by hand without an agent.
genre: how-to
resource: README.md
tags:
  - install
  - npx skills
  - claude plugin
references:
  - https://noelmcloughlin.github.io/linkml-sidecar/knowledge/playbooks/linkml-sidecar-skill
  - https://noelmcloughlin.github.io/linkml-sidecar/knowledge/playbooks/linkml-author-skill
  - https://noelmcloughlin.github.io/linkml-sidecar/knowledge/services/linkml-scaffold
  - https://noelmcloughlin.github.io/linkml-sidecar/knowledge/services/linkml-preflight
sources:
  - resource: README.md
  - resource: .claude-plugin/plugin.json
  - resource: .claude-plugin/marketplace.json
generated:
  by: process:ktl-librarian
  at: "2026-10-21T22:30:32Z"
status: draft
verified:
  - by: process:ktl-librarian
    at: "2026-10-22T15:14:26Z"
---

# Overview

Install both skills with the Open Skills CLI:

```bash
npx skills add noelmcloughlin/linkml-sidecar --skill linkml-sidecar --skill linkml-author --yes
```

In Claude Code, add the marketplace and install the plugin instead:

```bash
claude plugin marketplace add noelmcloughlin/linkml-sidecar && claude plugin install linkml-sidecar@linkml-sidecar
```

Then ask the agent to set up a LinkML sidecar. Hosts need `git` and `uv`; copier, just and LinkML run through uv.

## Without an agent

The skill's two scripts work without an agent. From the host's root, with this repository cloned beside it, run the preflight, export the facts, and run the scaffold with `--dry-run` first:

```bash
bash ../linkml-sidecar/skills/linkml-sidecar/templates/scripts/linkml-preflight.sh .
bash ../linkml-sidecar/skills/linkml-sidecar/scripts/linkml-scaffold.sh --dry-run
bash ../linkml-sidecar/skills/linkml-sidecar/scripts/linkml-scaffold.sh
```

The README lists the variables to export. Step 0 of the linkml-sidecar skill says where each fact comes from, and Step 1 lists the exit codes, `--repair` and `--pointers-only`.
