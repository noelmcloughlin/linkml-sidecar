---
type: GlossaryTerm
id: https://noelmcloughlin.github.io/linkml-sidecar/knowledge/glossary/doorway
title: Doorway
description: The linkml_schema link at the host's root that shows the hidden sidecar's schema folder under an ordinary, visible name.
definition: A relative symbolic link, linkml_schema, from the host's root to .linkml/src/<slug>/schema, so a person can open the schema folder where Finder and folder pickers hide dot-directories.
resource: skills/linkml-sidecar/SKILL.md
tags:
  - linkml_schema
  - symlink
sources:
  - resource: skills/linkml-sidecar/SKILL.md
generated:
  by: process:ktl-librarian
  at: "2026-10-22T01:26:03Z"
status: draft
verified:
  - by: process:ktl-librarian
    at: "2026-10-22T15:14:26Z"
---

# Overview

The **doorway** is `linkml_schema`, made with `ln -s .linkml/src/<slug>/schema linkml_schema`: the schema folder under an ordinary, visible name beside the hidden `.linkml/`. Finder and most folder pickers hide dot-directories, so the doorway is the one name a person needs to know.

The target is relative, which keeps the link valid after a clone or a move. `just --justfile .linkml/justfile linkml-link` recreates it where a sync service dropped it. On Windows a junction does the job (`mklink /J`); on a filesystem without links, it is skipped. It is committed beside a tracked `.linkml/`, or added to the root `.gitignore` with `--gitignored`.

An adopted schema gets no doorway, because it is already visible where it lies.
