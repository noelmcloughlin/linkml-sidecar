---
type: Policy
id: https://noelmcloughlin.github.io/linkml-sidecar/knowledge/policies/releasing
title: Releasing
description: "How a release is cut: a maintainer tags it by hand once Unreleased in CHANGELOG.md becomes a dated version heading, both skills release together under that tag, installers read the tag, and the plugin marketplace reads main."
resource: CONTRIBUTING.md
tags:
  - release
  - changelog
  - tag
sources:
  - resource: CONTRIBUTING.md
  - resource: CHANGELOG.md
  - resource: .claude-plugin/plugin.json
generated:
  by: process:ktl-librarian
  at: "2026-10-21T22:30:32Z"
status: draft
verified:
  - by: process:ktl-librarian
    at: "2026-10-22T01:26:03Z"
---

# Overview

A maintainer tags a release by hand once `## [Unreleased]` in `CHANGELOG.md` has been promoted to a version heading with its date. Both skills release together under that tag.

Installers read the tag. The plugin marketplace reads `main`, and `plugin.json` carries no `version`, so that it always does.

`CHANGELOG.md` follows Keep a Changelog. A change that alters what a skill does adds a line or two under `## [Unreleased]`, and the contract fails when one released version has two headings.
