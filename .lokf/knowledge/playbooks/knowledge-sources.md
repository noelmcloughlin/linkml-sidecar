---
type: Playbook
id: https://noelmcloughlin.github.io/linkml-sidecar/knowledge/playbooks/knowledge-sources
title: Knowledge sources
description: Map of the repository locations this bundle was derived from, the classes each yields, the files left out on purpose, and how to re-check each on a future refresh.
genre: how-to
resource: .
sources:
  - resource: README.md
  - resource: CONTRIBUTING.md
  - resource: CHANGELOG.md
  - resource: AI_COVENANT.md
  - resource: CODE_OF_CONDUCT.md
  - resource: LICENSE
  - resource: llms.txt
  - resource: .claude-plugin
  - resource: skills/linkml-sidecar
  - resource: skills/linkml-author
  - resource: scripts
  - resource: tests
  - resource: pytest.ini
  - resource: .github
  - resource: .gitignore
  - resource: .markdownlint-cli2.jsonc
  - resource: lychee.toml
  - resource: website
generated:
  by: process:ktl-librarian
  at: "2026-10-22T01:26:03Z"
status: draft
verified:
  - by: process:ktl-librarian
    at: "2026-10-22T07:43:26Z"
---

# Overview

This bundle is derived from the repository's own files. Each row names a source, the classes it yields, and how to re-check it.

| Source | Yields | Re-check |
| --- | --- | --- |
| `skills/linkml-sidecar/SKILL.md`, `skills/linkml-author/SKILL.md` | one `Playbook` per skill | the frontmatter `description` and `compatibility`, and the Scope section |
| `skills/linkml-sidecar/scripts/`, `templates/scripts/`, `templates/github/` | `Service` for the scaffold, the preflight and the workflow | each script's header comment and the workflow's jobs |
| `skills/linkml-sidecar/references/`, `skills/linkml-author/references/` | `Document`, `Explanation` and `GlossaryTerm` concepts | the headings, and the template version in `template-assumptions.md` |
| `skills/linkml-sidecar/templates/linkml/` | the dummy schema term | the `plain/` and `lokf/` schema files |
| `README.md`, `.claude-plugin/` | the install playbook, the three cases, the sidecar term, the KTL and LinkML references | the Three cases, Install and Layout sections |
| `CONTRIBUTING.md`, `.github/pull_request_template.md`, `tests/conftest.py`, `scripts/smoke-test-install.sh` | the contributing playbook and the release policy | the checklist and the Releasing section |
| `scripts/validate-repository.sh`, `.github/workflows/validate.yml`, `.github/dependabot.yml` | the repository contract | the numbered check comments and the job names |
| `AI_COVENANT.md`, `CODE_OF_CONDUCT.md` | `Policy` | the section headings |
| `website/`, `.github/workflows/knowledge-website.yaml` | the knowledge website playbook | `website/README.md` and the option comments in `website/site.config.mjs` |

## Left out on purpose

- `LICENSE` is the Apache-2.0 text, which the README's License section states.
- `CHANGELOG.md` records history; the release policy cites it for its format only.
- `llms.txt` points agents at the skills and this bundle, and states nothing the skills do not.
- `tests/` beyond `conftest.py`, and `pytest.ini`, exercise the scripts and describe no behaviour of their own.
- `.gitignore`, `.markdownlint-cli2.jsonc` and `lychee.toml` configure tools for this repository's own checks.
- The other `.github/workflows/knowledge-*.yaml` workflows and `.github/PULL_REQUEST_TEMPLATE/knowledge-sync.md` are ktl-sidecar's copies, which keep this bundle, not the skills.
