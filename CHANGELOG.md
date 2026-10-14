# Changelog

All notable changes to this project are documented here. The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### Added

- **linkml-sidecar installs a `.linkml/` LinkML schema sidecar from linkml-project-copier v0.5.0, pinned and verified, with every root-install assumption of the template neutralised.** One scaffold script pre-seeds the files the skill owns, runs copier for the rest, patches what assumes a repository root, adds the root pointers and the `linkml_schema` doorway, and prints the hand-off. A preflight says what the host can do first; the catalogue of assumptions is a reference page that shrinks as upstream adopts a sidecar layout.
- **KTL mode: beside a `.lokf/` bundle the sidecar's schema is the bundle's domain schema.** The scaffold pins `.lokf/lokf.yaml`, lays down a dummy that imports it, writes a lint config that excuses LOKF's camelCase slots, and wires `.lokf/justfile` so `lokf validate --schema` runs from the schema's directory, which works on linkml 1.11.x and 1.12.0 alike.
- **linkml-author keeps the schema.** One sidecar-aware authoring skill that finds the project through the preflight, runs every tool through the project's own environment, states its rules (snake_case enum values, `dcterms`, slots versus attributes, string annotations, `just test` does not lint), and keeps the metamodel, generator pitfalls by version, source mapping, the lmodel profile and the KTL rules as references.
- **A hoisted workflow template** runs `just lint` and `just test` in `.linkml/` from the host's root, builds the docs site as an artifact, and publishes it under the `linkml/` subpath of `gh-pages` only once `LINKML_DOCS_ENABLED` is `true`.
- **Tests and a repository contract.** The scaffold, the preflight and the workflow run on throwaway hosts against an offline stand-in for copier; the slow tests run the real template and both gates.

### Changed

- **The README says what the sidecar is in plain words.** The two-patterns section and the sidecar note lose their figures of speech.
