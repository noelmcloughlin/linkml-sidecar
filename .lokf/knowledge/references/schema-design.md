---
type: Document
id: https://noelmcloughlin.github.io/linkml-sidecar/knowledge/references/schema-design
title: Schema design for reuse
description: "linkml-author's page on designing a LinkML schema that others can import and extend, distilled from Damien Goutte-Gattat's draft LinkML guidelines: reuse by import, minor releases that only add, prefixed class names, attributes before slots, mixins, type designators instead of kind enums, no enum inheritance and typed references."
genre: reference
resource: skills/linkml-author/references/schema-design.md
tags:
  - schema design
  - reuse
  - extensibility
  - versioning
references:
  - https://noelmcloughlin.github.io/linkml-sidecar/knowledge/playbooks/linkml-author-skill
sources:
  - resource: skills/linkml-author/references/schema-design.md
generated:
  by: process:ktl-librarian
  at: "2026-10-22T01:26:03Z"
status: draft
---

# Overview

`skills/linkml-author/references/schema-design.md` is for an author who designs the model as well as the schema. It says what to decide so that another schema can import this one, and a later version can add to it without breaking the data already written. It distils Damien Goutte-Gattat's *LinkML guidelines: authoring extensible and reusable schemas*, a 2026 draft under CC BY-SA 4.0. The page calls it one practitioner's view, not a LinkML project document. Where linkml-author's rules table and the page meet, the table is the rule and the page gives the reason.

## What it recommends

- Import a schema rather than copy its classes. Every name in the import closure shares one flat namespace, so names are chosen with that in mind.
- In a minor release, only add. Never remove, rename or tighten anything. A change that breaks data is a major release.
- In a schema meant to be imported, give class names a schema-specific prefix, end a mixin's name in `Mixin`, and name an enum in the singular with no `Enum` suffix.
- Start every class with attributes, and lift a field to a top-level slot only when a second class needs the same field with the same meaning.
- Put fields that unrelated classes share in a mixin.
- Model variants of one thing as subclasses under a base class with a type designator, not as one class with a kind enum.
- Do not inherit one enum from another.
- Type a reference to another class by its range, with `identifier: true` on the target's key.

A schema retrofitted to data that already exists cannot follow all of it: slot names and enum values stay as the data spells them.
