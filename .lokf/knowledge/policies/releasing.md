---
type: Policy
id: https://noelmcloughlin.github.io/linkml-sidecar/knowledge/policies/releasing
title: Releasing
description: "How a release is cut: semantic-release.yml waits for a reviewer of the release environment and then promotes Unreleased in CHANGELOG.md to the next version, a maintainer runs publish.yml by hand with that version, gh skill publish creates the tag and the release for both skills, installers read the tag, and the plugin marketplace reads main."
resource: CONTRIBUTING.md
tags:
  - release
  - changelog
  - tag
sources:
  - resource: CONTRIBUTING.md
  - resource: CHANGELOG.md
  - resource: .claude-plugin/plugin.json
  - resource: .github/workflows/semantic-release.yml
  - resource: .github/workflows/publish.yml
  - resource: .releaserc.json
generated:
  by: process:ktl-librarian
  at: "2026-10-22T15:14:26Z"
status: draft
verified:
  - by: process:ktl-librarian
    at: "2026-10-22T09:04:50Z"
---

# Overview

A merge to `main` that carries a `feat:`, `fix:`, `security:` or breaking commit waits in `semantic-release.yml` for a reviewer of the `release` environment. Once a reviewer approves it, the workflow promotes `## [Unreleased]` in `CHANGELOG.md` to the next version.

A maintainer then runs `publish.yml` by hand with that version. It checks the contract and the tests again, and `gh skill publish` creates the tag and the release. Both skills release together under that tag.

A pull request whose commits would release needs a typed title, because a squash merge takes its subject from the title.

Installers read the tag. The plugin marketplace reads `main`, and `plugin.json` carries no `version`, so that it always does.

`CHANGELOG.md` follows Keep a Changelog. A change that alters what a skill does adds a line or two under `## [Unreleased]`, and the contract fails when one released version has two headings.
