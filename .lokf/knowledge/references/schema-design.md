---
type: Document
id: https://noelmcloughlin.github.io/linkml-sidecar/knowledge/references/schema-design
title: Schema design for reuse
description: "linkml-author's page on designing a LinkML schema that others can import and extend: which names reach the data, attributes before slots, mixins, prefixed class names, type designators instead of kind enums, typed references, no enum inheritance, and minor releases that only add."
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
  at: "2026-10-22T07:43:04Z"
status: draft
---

# Overview

`skills/linkml-author/references/schema-design.md` is for an author who designs the model as well as the schema. It collects the decisions that settle whether another schema can import this one, and whether a later release can add to it without breaking the data already written. Where linkml-author's rules table and the page meet, the table is the rule and the page gives the reason. The page grows as more sources are folded in.

## What it recommends

- Remember which names reach the data: slot names and permissible values appear in every record, and class and enum names do not. Every name in the import closure shares one namespace.
- Start every class with attributes, and lift a field to a top-level slot only when a second class needs the same field with the same meaning.
- Put fields that unrelated classes share in a mixin.
- In a schema meant to be imported, give class names a prefix of the schema's own, end a mixin's name in `Mixin`, and name an enum in the singular with no `Enum` suffix.
- Model the kinds of one thing as subclasses under a base class with a type designator, not as one class with a kind enum.
- Type a reference to another class by its range, with `identifier: true` on the target's key.
- Do not inherit one enum from another.
- In a minor release, only add. A change that breaks data is a major release.

A schema written to fit data that already exists keeps the data's slot names and enum values.
