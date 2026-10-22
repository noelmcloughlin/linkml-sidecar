---
type: Reference
id: https://noelmcloughlin.github.io/linkml-sidecar/knowledge/references/agent-skills-specification
title: Agent Skills specification
description: "The Agent Skills format both skills follow: a folder with a SKILL.md whose frontmatter carries name, description, license and compatibility, checked in CI with gh skill publish --dry-run."
genre: reference
resource: https://agentskills.io
tags:
  - agent skills
  - SKILL.md
sources:
  - resource: README.md
  - resource: scripts/validate-repository.sh
  - resource: .github/workflows/validate.yml
generated:
  by: process:ktl-librarian
  at: "2026-10-21T22:30:32Z"
status: draft
verified:
  - by: process:ktl-librarian
    at: "2026-10-22T18:19:05Z"
---

# Overview

Both skills are [Agent Skills](https://agentskills.io): each is a folder under `skills/` with a `SKILL.md` whose frontmatter carries `name`, `description`, `license` and `compatibility`. The repository contract checks that each declared name matches its directory, that each skill states `compatibility`, and that each description ends in a `Keywords:` list. The `validate-skills` job of `validate.yml` also runs `gh skill publish --dry-run`, the spec check of the GitHub CLI.
