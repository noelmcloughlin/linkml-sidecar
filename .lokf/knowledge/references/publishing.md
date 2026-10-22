---
type: Document
id: https://noelmcloughlin.github.io/linkml-sidecar/knowledge/references/publishing
title: Publishing a schema others can import
description: "linkml-author's page on how a schema reaches an importer: two addresses under its id (every module at schema/module.yaml and one merged file with no imports), a tagged release with a checksummed asset, a vendored copy at a tag or an import by persistent identifier and never by a code-host URL, the importmap and the order an import resolves in, and lokf's adapt for a vocabulary that shares names with yours."
genre: reference
resource: skills/linkml-author/references/publishing.md
tags:
  - schema design
  - imports
  - distribution
  - importmap
references:
  - https://noelmcloughlin.github.io/linkml-sidecar/knowledge/playbooks/linkml-author-skill
relatedTo:
  - https://noelmcloughlin.github.io/linkml-sidecar/knowledge/references/schema-design
sources:
  - resource: skills/linkml-author/references/publishing.md
generated:
  by: process:ktl-librarian
  at: "2026-10-22T12:03:24Z"
status: draft
verified:
  - by: process:ktl-librarian
    at: "2026-10-22T15:14:26Z"
---

# Overview

`skills/linkml-author/references/publishing.md` is for the author whose schema will be imported, vendored or loaded by someone else's project. It says how a schema reaches an importer, which addresses to serve it at, how an importer takes it, and how a vocabulary that was not designed to sit beside yours is brought in. Each behaviour is stamped with the LinkML version it was seen on. The schema design page decides the shape of the schema; this page decides where it is read from.

## What it says

- LinkML leaves distribution open. Its documentation says a release that keeps relative imports must keep every module at the same relative path, and that `--mergeimports` folds the closure into one file before distribution. A schema reaches an importer as a copy in the importer's repository, as the data files of a Python package, or through a persistent identifier that serves the file.
- Serve two addresses under the schema's `id`: every source file at `schema/<module>.yaml`, at the same relative paths as in the repository, and one merged file with no imports, which `gen-linkml --mergeimports` writes and `gen-project` does not.
- On LinkML 1.12.1 a module imported by URL or CURIE resolves its own relative imports from its own address, so a modular root imports over HTTP when every module is served at the same relative path. The merged file serves an offline build, a checksum pin and a direct load, because `SchemaView(url)` appends nothing. A tag in the path pins a release.
- A tagged release attaches the schema with its checksum; KTL's knowledge-release workflow and gist do this. The sidecar's own workflow does not yet.
- An importer vendors a copy pinned to a tag and upgrades on purpose, or imports by the persistent identifier; never by a raw code-host URL.
- An importmap bridges import strings and file locations. An import resolves through the importmap first, then as a URL, then as a CURIE, else relative to the importing file, with `.yaml` appended in every case. A key is a CURIE, an IRI or a namespace; a value omits `.yaml` and resolves against the directory of the schema the tool was given, nested imports included. Each generator takes `--importmap`; `gen-project` takes it as `importmap` in a generator's `generator_args` in `generators.yaml`; `linkml-validate` takes none yet.
- lokf's `adapt`, experimental and unreleased, makes a copy of a vocabulary that can sit beside `lokf.yaml`: it folds the imports, drops the identifier and type designator, renames every other shared name with the IRI pinned, and re-roots the top classes. Its `--check` says in CI when the published vocabulary has moved.

The page cites the lmodel redirect table as a worked example and says that lmodel is an experiment area, not a standard.
