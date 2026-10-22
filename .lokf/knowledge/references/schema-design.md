---
type: Document
id: https://noelmcloughlin.github.io/linkml-sidecar/knowledge/references/schema-design
title: Schema design for reuse
description: "linkml-author's page on designing a LinkML schema that others can import and extend: which names reach the data and why a clash under import is silent, attributes before slots with fundamental names kept as attributes, mixins, prefixed class names, a core plus modules as the shape importers can take a slice of, type designators instead of kind enums, typed references, no enum inheritance, minor releases that only add, and when a schema that exists can still be refactored."
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
  at: "2026-10-22T10:56:45Z"
status: draft
---

# Overview

`skills/linkml-author/references/schema-design.md` is for an author who designs the model as well as the schema. It collects the decisions that settle whether another schema can import this one, and whether a later release can add to it without breaking the data already written. Where linkml-author's rules table and the page meet, the table is the rule and the page gives the reason. The page grows as more sources are folded in.

## What it recommends

- Remember which names reach the data: slot names and permissible values appear in every record, and class and enum names do not. Every name in the import closure shares one namespace, and a clash is silent: of two imports in one list, the one listed last wins, and lint says nothing.
- Start every class with attributes, and lift a field to a top-level slot only when a second class needs the same field with the same meaning.
- Put fields that unrelated classes share in a mixin.
- Keep a fundamental name (`id`, `name`, `type`, `description`) as an attribute, or in one mixin, because such names clash first. A base slot the schema means to share carries a `slot_uri`, so the IRI survives a rename by an importer.
- Give same-named attributes in different modules one shared slot, or a `slot_uri` each, because they otherwise induce one IRI.
- In a schema meant to be imported, give class names a prefix of the schema's own, end a mixin's name in `Mixin`, and name an enum in the singular with no `Enum` suffix.
- Model the kinds of one thing as subclasses under a base class with a type designator, not as one class with a kind enum.
- Type a reference to another class by its range, with `identifier: true` on the target's key.
- Do not inherit one enum from another.
- Write a schema that expects importers as a core module, topic modules that import it and lint alone, and an umbrella that holds only the tree root, with no import cycle. A module is the only slice an importer can take.
- In a minor release, only add. A change that breaks data is a major release.
- Offer a refactor when the schema folder's history is one or two people, read from the preflight's `authors` line, and never carry one out unasked. Folding a single-class slot into an attribute, splitting or merging modules and pinning IRIs touch no record. Renaming a slot, a value or a designator class is a major release.

A schema written to fit data that already exists keeps the data's slot names and enum values.
