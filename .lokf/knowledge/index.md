---
lokf_version: "0.2"
okf_version: "0.2"
base_iri: https://noelmcloughlin.github.io/linkml-sidecar/knowledge/
context: https://w3id.org/lokf/context.jsonld
title: linkml-sidecar Knowledge Bundle
description: "Two Agent Skills that give a code repository a LinkML data model as a sidecar: linkml-sidecar installs a hidden .linkml/ project from linkml-project-copier without touching the host's build, and linkml-author turns its dummy schema into the real model and keeps it generated, documented and tested."
license: https://creativecommons.org/licenses/by/4.0/
publisher:
  type: Person
  id: https://noelmcloughlin.github.io/linkml-sidecar/knowledge/person/noel-mcloughlin
  name: Noel McLoughlin
---

# linkml-sidecar Knowledge Bundle

A [LOKF](https://lokf.nolan-nichols.com) knowledge base for linkml-sidecar. Every Markdown file under `knowledge/` is one concept; together they form a queryable knowledge graph, derived from this repository's code and docs.

# Services

* [linkml-scaffold.sh](services/linkml-scaffold.md) - The scaffold script that does Steps 1 to 3 of linkml-sidecar in one deterministic run: it verifies the template pin, pre-seeds the skill's own files, runs copier, neutralises root assumptions, wires a KTL bundle, adds the root pointers, and exits 0, 2, 3, 4 or 5.
* [linkml-preflight.sh](services/linkml-preflight.md) - The read-only preflight both skills run first: one screen of ok, warn, missing and info lines about the host's shell, git, forge, uv, copier, just, network, an existing sidecar, a .lokf/ bundle and Pages, ending in a summary line of what is missing and which steps that disables.
* [linkml-sidecar workflow](services/linkml-sidecar-workflow.md) - The one GitHub Actions workflow the sidecar installs at .github/workflows/linkml-sidecar.yaml: lint and test in .linkml/ from the locked environment, build the docs site on the default branch, and publish it under the linkml/ subpath of gh-pages only while LINKML_DOCS_ENABLED is true.
* [Repository contract](services/repository-contract.md) - scripts/validate-repository.sh and the validate.yml workflow: the checks every pull request runs on this repository, covering skill shape, links, word budgets, the one template pin, shared action pins, prerequisites rows, the changelog, invisible characters, plus pytest, ShellCheck, actionlint, markdownlint, lychee, codespell and the install smoke test.

# Playbooks

* [linkml-sidecar skill](playbooks/linkml-sidecar-skill.md) - The installer skill: it runs once to put a hidden .linkml/ LinkML schema project from linkml-project-copier into a host repository without touching the host's build, repairs one file it owns, and hands off to linkml-author.
* [linkml-author skill](playbooks/linkml-author-skill.md) - The authoring skill: it adds, changes or deprecates LinkML classes, slots, enums and types, replaces the dummy schema with the host's real model, and runs lint, gen-project and test after every change, in a .linkml/ sidecar, a visible linkml/ one or a copier project at the root.
* [Installing the skills](playbooks/installing-the-skills.md) - How to install linkml-sidecar and linkml-author with npx skills or as a Claude Code plugin, and how to run the preflight and the scaffold by hand without an agent.
* [Contributing](playbooks/contributing.md) - The contributor checklist: development setup, the fast and slow tests, the install smoke test, what to run before a pull request, how to move the linkml-project-copier template pin, and how action pins in the workflow template follow Dependabot.
* [Knowledge sources](playbooks/knowledge-sources.md) - Map of the repository locations this bundle was derived from, the classes each yields, the files left out on purpose, and how to re-check each on a future refresh.

# Explanation

* [Two patterns, one skill](explanation/two-patterns.md) - Why there are two ways to give a repository a LinkML schema: a repository that is itself a schema project runs copier at its root and needs nothing here, while a domain codebase whose maintainers do not want a schema project in their root gets the hidden .linkml/ sidecar.
* [KTL mode](explanation/ktl-mode.md) - What changes when the host carries a .lokf/ Knowledge Trust Ladder bundle: the sidecar's schema becomes the bundle's domain schema, the scaffold pins .lokf/lokf.yaml, lays down an ExampleConcept dummy, excuses LOKF's camelCase slots in the linter and wires .lokf/justfile so lokf validate --schema runs from the schema's directory.

# References

* [Template assumptions catalogue](references/template-assumptions.md) - The catalogue, at template v0.5.0, of the eighteen things linkml-project-copier assumes of a repository root (just setup, just deploy, nested workflows, the governance files, mkdocs URLs, --trust, just update and more), what the scaffold does about each, and which an upstream layout answer would remove.
* [Upstream layout proposal](references/upstream-proposal.md) - A draft, not yet filed, for an issue on linkml/linkml-project-copier proposing a layout answer (root or sidecar) and a sidecar_dir, which would remove most rows of the template assumptions catalogue; filing it is a person's call.
* [linkml-project-copier](references/linkml-project-copier.md) - The upstream copier template (MIT) that every sidecar is made from, pinned at tag v0.5.0 and verified against the commit the scaffold driver records before it runs with --trust.
* [LinkML](references/linkml.md) - LinkML, the modelling language the sidecar's schema is written in; linkml.io is the canonical site for what it means, its schemas and its generators (JSON Schema, Pydantic, OWL, SHACL, TypeScript, docs).
* [Agent Skills specification](references/agent-skills-specification.md) - The Agent Skills format both skills follow: a folder with a SKILL.md whose frontmatter carries name, description, license and compatibility, checked in CI with gh skill publish --dry-run.
* [Knowledge Trust Ladder](references/knowledge-trust-ladder.md) - The Knowledge Trust Ladder (KTL), whose bundle is a .lokf/ folder in the host; beside one, the sidecar's schema becomes the bundle's domain schema, and ktl-librarian's domain-schema page is the authority on what lokf validate expects.

# Policies

* [AI covenant](policies/ai-covenant.md) - Community norms for AI use: contributors own what they submit whatever tools helped, AI review comments are suggestions, AI systems must not post comments or replies in issues, discussions, chat or mail, and AI co-authorship in commit messages is discouraged.
* [Code of conduct](policies/code-of-conduct.md) - The Contributor Covenant code of conduct that covers participation in this repository.
* [Releasing](policies/releasing.md) - How a release is cut: a maintainer tags it by hand once Unreleased in CHANGELOG.md becomes a dated version heading, both skills release together under that tag, installers read the tag, and the plugin marketplace reads main.

# Glossary

* [Sidecar](glossary/sidecar.md) - A hidden folder, .linkml/, that holds a complete schema project beside a host's own code, with nothing in the host's build depending on it.
* [Doorway](glossary/doorway.md) - The linkml_schema link at the host's root that shows the hidden sidecar's schema folder under an ordinary, visible name.
* [Dummy schema](glossary/dummy-schema.md) - The small placeholder schema a fresh sidecar holds, a Person example or, beside a KTL bundle, ExampleConcept, which lints clean and which linkml-author replaces with the host's real model.
* [Template pin](glossary/template-pin.md) - The one place the linkml-project-copier version is fixed: LINKML_TEMPLATE_REF and LINKML_TEMPLATE_SHA in the scaffold driver, a tag verified against its commit before copier runs with --trust.
* [Domain schema](glossary/domain-schema.md) - A LinkML schema that imports LOKF's core schema so its is_a Concept classes become types a .lokf/ bundle's concepts may carry, checked by lokf validate --schema; beside a KTL bundle the sidecar's schema is one.
* [The gate](glossary/the-gate.md) - linkml-author's check after every schema edit: just lint, then just gen-project, then just test, run through the project's justfile, with lokf validate after it beside a KTL bundle.
