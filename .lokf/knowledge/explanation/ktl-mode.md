---
type: Explanation
id: https://w3id.org/ktl/linkml-sidecar/knowledge/explanation/ktl-mode
title: KTL mode
description: "What changes when the host carries a .lokf/ Knowledge Trust Ladder bundle: the sidecar's dummy schema becomes the bundle's domain schema, and the scaffold pins .lokf/lokf.yaml, writes an ExampleConcept dummy, excuses LOKF's camelCase slots in the linter and names the schema in .lokf/justfile; an adopted schema is not made the domain schema."
genre: explanation
resource: skills/linkml-sidecar/references/ktl.md
tags:
  - ktl
  - lokf
  - domain schema
  - lokf validate
about:
  - https://w3id.org/ktl/linkml-sidecar/knowledge/glossary/domain-schema
references:
  - https://w3id.org/ktl/linkml-sidecar/knowledge/references/knowledge-trust-ladder
  - https://w3id.org/ktl/linkml-sidecar/knowledge/playbooks/linkml-author-skill
sources:
  - resource: skills/linkml-sidecar/references/ktl.md
  - resource: skills/linkml-author/references/ktl-domain-schema.md
  - resource: skills/linkml-author/SKILL.md
  - resource: docs/architecture.md
generated:
  by: process:ktl-librarian
  at: "2026-10-22T18:19:05Z"
status: draft
verified:
  - by: process:ktl-librarian
    at: "2026-10-22T11:13:31Z"
---

# Overview

The sidecar stands alone. When the host carries a `.lokf/` bundle, the preflight switches on KTL mode, and the sidecar's dummy schema becomes the bundle's domain schema. It imports LOKF's core schema. Each class in it that is `is_a: Concept` is a type the bundle's concepts may carry, and `lokf validate --schema` checks the bundle against both schemas.

A schema the host already held (`--adopt`) is not made the domain schema: the scaffold runs in plain mode beside the bundle and says so in the hand-off. A bundle beside a schema may be a bundle *about* the repository, as in a schema repository that documents itself. The schema is the bundle's domain schema only when `.lokf/justfile` names it or it imports `.lokf/lokf.yaml`, and its maintainers decide that.

## What the scaffold does in KTL mode

1. Pins the core schema beside the bundle: `.lokf/lokf.yaml` is copied out of the installed `lokf` toolkit, at the floor `.lokf/pyproject.toml` names.
2. Writes a dummy that imports it: one class, `ExampleConcept`, `is_a: Concept`, with one slot of its own.
3. Excuses LOKF's camelCase relation slots in `.linkml/.linkmllint.yaml`, and nothing else, so the host's own slots are still held to snake_case.
4. Adds `--render-imports` to gen-doc, so `is_a: Concept` links to a page that exists.
5. Sets `schema :=` in `.lokf/justfile`, and makes its `lokf-validate` and `lokf-check-refs` recipes pass `--schema`.

## The one workaround

The two recipes run from the schema's directory rather than from `.lokf/`. `lokf validate` passes the schema to `linkml.validator.validate()`, which drops the schema's path, so a relative import resolves from the working directory. [linkml PR 3855](https://github.com/linkml/linkml/pull/3855), released in linkml 1.12.0, changes how imports are tracked. The `cd` form works on 1.11.x and 1.12.0 alike, so it stays while a `.lokf/uv.lock` may still hold 1.11.x.

## Two more upstream limits

- LOKF has a slot named `from`, a Python keyword, so the generated dataclasses cannot be imported on linkml 1.11.1, and the template's example runner needs them. KTL mode keeps its valid example under `tests/data/problem/valid/`, which the runner skips, and its `tests/test_data.py` validates both folders through `linkml.validator.validate()`.
- `copier update --pretend` fails in a subproject, so there is no dry run of `just update`.

## What the host still does by hand

It adds each domain class to the *Known LOKF types* setting of the KTL Registrar and KTL Curator plugins. When the `lokf` floor moves, it refreshes `.lokf/lokf.yaml`, regenerates `.linkmllint.yaml` and re-runs both gates. When the sidecar is removed, `.lokf/justfile` is reset to `schema := ""`.
