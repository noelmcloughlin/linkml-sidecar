---
type: Playbook
id: https://noelmcloughlin.github.io/linkml-sidecar/knowledge/playbooks/knowledge-website
title: Knowledge website
description: "How the website in website/ is built, previewed and published: an Astro Starlight site with a page per concept and its trust label, the lokf export files under knowledge/, and the README as its home page, deployed to GitHub Pages by knowledge-website.yaml once KNOWLEDGE_WEBSITE_ENABLED is true."
genre: how-to
resource: website/README.md
tags:
  - website
  - github pages
  - astro
  - KNOWLEDGE_WEBSITE_ENABLED
references:
  - https://noelmcloughlin.github.io/linkml-sidecar/knowledge/references/knowledge-trust-ladder
sources:
  - resource: website/README.md
  - resource: website/site.config.mjs
  - resource: .github/workflows/knowledge-website.yaml
  - resource: website
generated:
  by: process:ktl-librarian
  at: "2026-10-21T22:47:54Z"
status: draft
---

# Overview

The folder `website/` builds the site that the Knowledge website workflow publishes to GitHub Pages at `https://noelmcloughlin.github.io/linkml-sidecar/`. Every page comes from a file the repository already holds, so a change to the site is a change to that file.

- Each concept in `.lokf/knowledge/` becomes a page under `knowledge/`, with its trust label from `knowledge-report.sh`, its sources and its typed relations both ways.
- The four files `lokf export` writes are served under `knowledge/`, beside each concept's own Markdown file and its JSON-LD. The bundle log is served as an Atom feed, `knowledge/log.xml`.
- The README becomes the home page.

The README of `website/` also describes pages for `docs/`, `CHANGELOG.md` releases, the LinkML schema and SQLite data. `site.config.mjs` leaves each of these on `"auto"` or empty, and an `"auto"` part shows only when the repository has it.

## Preview it

Preview the site with Node.js 22.12 or later and [uv](https://docs.astral.sh/uv/):

```bash
cd website
npm ci --ignore-scripts
npm run dev        # http://localhost:4321/linkml-sidecar/
npm run build      # dist/, then checks every link between its pages
```

Both commands run `npm run sync` first. It runs `lokf export` from the sidecar's own environment in `.lokf/` and writes the generated pages, and nothing it writes is committed. `node scripts/config.mjs` prints what the sync will read.

## What to edit

- **A page's words:** edit the file it comes from, the README or a concept. A concept changes through the librarian and the curator like any other change to the bundle.
- **The site's values and options:** edit `site.config.mjs`. A comment above each option says what it takes.
- **Its look:** edit `src/styles/custom.css`, which is this repository's own and is loaded last.

## Publishing

`.github/workflows/knowledge-website.yaml` builds the site on a pull request that touches its inputs, with the link check, and deploys nothing. A weekly run rebuilds it from the default branch. The `deploy` job runs for the default branch only, once the repository variable `KNOWLEDGE_WEBSITE_ENABLED` is `true`. Before setting it, tell Pages once to take its site from Actions, under Settings, Pages, Source. Set the variable under Repository variables, not on an environment, because a job's `if:` sees only repository and organization variables.
