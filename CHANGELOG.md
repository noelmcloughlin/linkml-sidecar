# Changelog

All notable changes to this project are documented here. The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

## [0.3.0] - 2026-10-23

### Added

- **The website's home page offers an Install button**, which opens the install page, beside the four default buttons.
- **linkml-author names the adapt route beside a KTL bundle.** A schema published on its own stays as it is, and the copy `lokf adapt` writes is the domain schema; the preflight's `lokf` line says when the justfile names such a copy.

## [0.2.0] - 2026-10-22

### Added

- **A Step 5 workflow for Forgejo, as Codeberg runs it.** It runs the same gate on Codeberg's runners and publishes the site under `linkml/` on Codeberg Pages once `LINKML_DOCS_ENABLED` is `true`. The preflight names the one workflow folder Forgejo reads.
- **An install page and an architecture page under `docs/`.** The install page puts the GitHub CLI first, for work machines, and ends with installing from a company copy of this repository. The portability page now covers RHEL, WSL2, a company proxy or package mirror, and a template copy for hosts without github.com.
- **The preflight asks the template's source and the package index that git and uv actually use**, a company copy or mirror included, and prints only their host names. It warns when `uv.lock` was made against another index than uv reads, and says why uvx cannot run copier, such as a certificate uv does not trust.

### Removed

- **The upstream layout proposal leaves linkml-sidecar's references.** It is filed as [linkml-project-copier#187](https://github.com/linkml/linkml-project-copier/issues/187), which the assumptions catalogue links instead.

### Fixed

- **The scaffold runs its Python half through `uv run` first**, then through a `python3` or `python` of 3.8 or later, as KTL's scripts do. An older `python3`, such as RHEL 8's 3.6, no longer stops it at its first line.

## [0.1.1] - 2026-10-22

### Fixed

- **Both skills' pages lose their dead phrases.** Adoption reads as "neither moved nor changed", and the schema is found by its files, which layouts.md lists, never by its folder. The reference pages were read through for the same faults.
- **The workflow template pins setup-uv v10.3.0**, as the repository's own workflows do.

## [0.1.0] - 2026-10-22

### Added

- **linkml-sidecar installs a `.linkml/` LinkML schema sidecar from linkml-project-copier v0.5.0, pinned and verified, with every root-install assumption of the template neutralised.** One scaffold script pre-seeds the files the skill owns, runs copier for the rest, patches what assumes a repository root, adds the root pointers and the `linkml_schema` doorway, and prints the hand-off. A preflight says what the host can do first; the catalogue of assumptions is a reference page that shrinks as upstream adopts a sidecar layout.
- **KTL mode: beside a `.lokf/` bundle the sidecar's schema is the bundle's domain schema.** The scaffold pins `.lokf/lokf.yaml`, adds a dummy that imports it, writes a lint config that excuses LOKF's camelCase slots, and edits `.lokf/justfile` so `lokf validate --schema` runs from the schema's directory, which works on linkml 1.11.x and 1.12.0 alike.
- **linkml-author keeps the schema.** This sidecar-aware authoring skill finds the project through the preflight, runs every tool through the project's own environment, and states its rules (snake_case enum values, `dcterms`, slots versus attributes, string annotations, `just test` does not lint). Its references keep the metamodel, generator pitfalls by version, source mapping, the lmodel profile and the KTL rules.
- **A hoisted workflow template** runs `just lint` and `just test` in `.linkml/` from the host's root, builds the docs site as an artifact, and publishes it under the `linkml/` subpath of `gh-pages` only once `LINKML_DOCS_ENABLED` is `true`.
- **Tests and a repository contract.** The scaffold, the preflight and the workflow run on throwaway hosts against an offline stand-in for copier; the slow tests run the real template and both gates.
- **`--adopt` builds the sidecar around a schema the repository already holds.** `config.public.mk` points at the schema's folder, the file is never moved, linked or edited, and no dummy is written. A schema found outside any project is refused until `--adopt` names it or `--dummy` asks for the example beside it.
- **The preflight finds the schema by what files say, wherever it sits.** Copier answers naming the template or a `config.public.mk` make a project at the root, one directory down or where the preflight was started. A schema file on its own is found by content. A `tools` line names how lint and the generators run there. linkml-author works in every one of those layouts.
- **linkml-author designs for reuse.** A reference page and the rules table set the design rules. They ask for attributes before slots, a mixin for shared fields, a type-designated hierarchy instead of a kind enum, typed references instead of described keys, no enum inheritance, prefixed class names, and releases that only add. Descriptions stay one or two plain sentences, since the generators copy them into JSON Schema, Pydantic, OpenAPI and UI hints. A caveat goes in `comments`, and a decision in `notes`.
- **linkml-author says how a schema is published, imported and refactored.** A new publishing page covers the two addresses, the release asset, vendoring, persistent identifiers and `importmap`; the design page gains the collision gradient, a core plus modules, and the refactoring moves that touch no record.
- **The preflight's `authors` line counts the people in the schema folder's history.** linkml-author offers a refactor only when that history is one or two people, and never carries one out unasked.

### Changed

- **The generators' settings are `.linkml/generators.yaml`.** A new sidecar renames the template's `config.yaml` and changes the one line of `config.public.mk` that names it. `--repair generators.yaml` moves an existing sidecar's or root project's file, and the preflight offers it.
- **The scaffold renders into a staging directory and never removes `.linkml/`.** A `.linkml/` that holds only configuration files is installed around; a name both hold is refused, never overwritten; a failed run removes the staging directory alone.
- **A bundle beside a schema does not make it the domain schema.** linkml-author treats a schema as a bundle's domain schema only when `.lokf/justfile` names it or it imports `lokf.yaml`.

- **The README says what the sidecar is in plain words.** The two-patterns section and the sidecar note lose their figures of speech.
- **The link check handles github.com as knowledge-trust-ladder's does.** File links are checked on raw.githubusercontent.com, other github.com pages are paced, and issue and pull request links are checked through GitHub's API, so a burst of 503s no longer fails the job.
- **The workflows and the workflow template pin harden-runner v2.22.1 together.**
