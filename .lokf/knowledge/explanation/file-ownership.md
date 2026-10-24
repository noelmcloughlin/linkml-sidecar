---
type: Explanation
id: https://w3id.org/ktl/linkml-sidecar/knowledge/explanation/file-ownership
title: Who owns which file
description: Who owns each file in a .linkml/ sidecar (the template, the host or the skill) and how each changes, which template recipes never run, and how just update keeps a sidecar current.
genre: explanation
resource: docs/architecture.md
sources:
  - resource: docs/architecture.md
  - resource: skills/linkml-sidecar/templates/linkml/README.md
tags:
  - ownership
  - just update
  - just setup
  - just deploy
  - repair
about:
  - https://w3id.org/ktl/linkml-sidecar/knowledge/glossary/sidecar
references:
  - https://w3id.org/ktl/linkml-sidecar/knowledge/references/template-assumptions
  - https://w3id.org/ktl/linkml-sidecar/knowledge/glossary/template-pin
  - https://w3id.org/ktl/linkml-sidecar/knowledge/explanation/two-patterns
generated:
  by: process:ktl-librarian
  at: "2026-10-22T18:19:05Z"
status: draft
---

# Overview

The template owns most of `.linkml/`: the justfile, `pyproject.toml`, `mkdocs.yml` and the rest that copier renders. Only `just update` changes them.

The host owns the schema, its tests and example data, the sidecar's README, license and docs pages, and `generators.yaml`.

The skill owns the preflight it installed, and `.linkmllint.yaml` beside a KTL bundle. Its repair rewrites them.

The README every sidecar carries maps every file to its owner.

## What never runs

`just setup` runs `git init` and commits, which would nest a repository inside the host. `just deploy` pushes the root of the host's `gh-pages` branch. Neither ever runs.

The workflow builds the site and publishes it under the `linkml/` subpath only, once a repository variable says so: to GitHub Pages, or to Codeberg Pages with the Forgejo workflow.

## Keeping it current

`cd .linkml && just update` moves the template to its latest release and upgrades LinkML in `uv.lock`. Run it on a clean tree, read the diff, and commit `uv.lock` and `.copier-answers.yml` with it.

There is no dry run: `copier update --pretend` fails inside a subfolder of a repository, so the diff is the preview. The preflight says which release a sidecar is at.
