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

* [linkml-scaffold.sh](services/linkml-scaffold.md) - The scaffold script that does Steps 1 to 3 of linkml-sidecar in one deterministic run: it verifies the template pin, stages the skill's files and copier's output, moves them into .linkml/ around what is already there, keeps the generators' settings in generators.yaml, adopts a schema the host holds with --adopt, names the schema in a KTL bundle's justfile, adds the root pointers, and exits 0, 2, 3, 4 or 5.
* [linkml-preflight.sh](services/linkml-preflight.md) - The read-only preflight both skills run first: one screen of ok, warn, missing and info lines about the host's shell, git, forge, uv, copier, just and network, where a LinkML schema project or schema file sits, how to run the tools on it and how many people have committed to it, a .lokf/ bundle and Pages, ending in a summary line of what is missing and which steps that disables.
* [linkml-sidecar workflow](services/linkml-sidecar-workflow.md) - The one GitHub Actions workflow the sidecar installs at .github/workflows/linkml-sidecar.yaml: lint and test in .linkml/ from the locked environment, build the docs site on the default branch, and publish it under the linkml/ subpath of gh-pages only while LINKML_DOCS_ENABLED is true.
* [Repository contract](services/repository-contract.md) - scripts/validate-repository.sh and the validate.yml workflow: the checks every pull request runs on this repository, covering skill shape, links, word budgets, the one template pin, shared action pins, prerequisites rows, the changelog, invisible characters, plus pytest, ShellCheck, actionlint, markdownlint, lychee, codespell and the install smoke test.

# Playbooks

* [linkml-sidecar skill](playbooks/linkml-sidecar-skill.md) - The installer skill: it runs once to put a hidden .linkml/ LinkML schema project from linkml-project-copier into a host repository, around a dummy schema or around a schema the host already holds (--adopt), without touching the host's build, repairs one file it owns, and hands off to linkml-author.
* [linkml-author skill](playbooks/linkml-author-skill.md) - The authoring skill: it adds, changes or deprecates LinkML classes, slots, enums and types, replaces the dummy schema with the host's real model, and runs lint, gen-project and test after every change, in any repository that holds a schema: the .linkml/ sidecar, a copier or cookiecutter project wherever it sits, or a schema file on its own.
* [Installing the skills](playbooks/installing-the-skills.md) - How to install linkml-sidecar and linkml-author with npx skills or as a Claude Code plugin, and how to run the preflight and the scaffold by hand without an agent.
* [Contributing](playbooks/contributing.md) - The contributor checklist: development setup, the fast and slow tests, the install smoke test, what to run before a pull request, how to move the linkml-project-copier template pin, and how action pins in the workflow template follow Dependabot.
* [Knowledge sources](playbooks/knowledge-sources.md) - Map of the repository locations this bundle was derived from, the classes each yields, the files left out on purpose, and how to re-check each on a future refresh.
* [Knowledge website](playbooks/knowledge-website.md) - How the website in website/ is built, previewed and published: an Astro Starlight site with a page per concept and its trust label, the lokf export files under knowledge/, and the README as its home page, deployed to GitHub Pages by knowledge-website.yaml once KNOWLEDGE_WEBSITE_ENABLED is true.

# Explanation

* [Three cases, one skill](explanation/two-patterns.md) - Why there are three ways to give a repository a LinkML schema: a repository that is itself a schema project runs copier at its root and needs nothing here, a domain codebase whose maintainers do not want a schema project in their root gets the hidden .linkml/ sidecar, and a repository holding a schema but no project gets the sidecar around that schema.
* [KTL mode](explanation/ktl-mode.md) - What changes when the host carries a .lokf/ Knowledge Trust Ladder bundle: the sidecar's dummy schema becomes the bundle's domain schema, and the scaffold pins .lokf/lokf.yaml, writes an ExampleConcept dummy, excuses LOKF's camelCase slots in the linter and names the schema in .lokf/justfile; an adopted schema is not made the domain schema.

# References

* [Template assumptions catalogue](references/template-assumptions.md) - The catalogue, at template v0.5.0, of the twenty things linkml-project-copier assumes of a repository root (just setup, just deploy, nested workflows, the governance files, mkdocs URLs, --trust, just update, config.public.mk, the generators' settings and more), what the scaffold does about each, and which an upstream layout answer would remove.
* [Upstream layout proposal](references/upstream-proposal.md) - A draft, not yet filed, for an issue on linkml/linkml-project-copier proposing a layout answer (root or sidecar) and a sidecar_dir, which would remove most rows of the template assumptions catalogue, with a caveat that .linkml/ is also proposed for LinkML's configuration files; filing it is a person's call.
* [linkml-project-copier](references/linkml-project-copier.md) - The upstream copier template (MIT) that every sidecar is made from, pinned at tag v0.5.0 and verified against the commit the scaffold driver records before it runs with --trust.
* [LinkML](references/linkml.md) - LinkML, the modelling language the sidecar's schema is written in; linkml.io is the canonical site for what it means, its schemas and its generators (JSON Schema, Pydantic, OWL, SHACL, TypeScript, docs).
* [Agent Skills specification](references/agent-skills-specification.md) - The Agent Skills format both skills follow: a folder with a SKILL.md whose frontmatter carries name, description, license and compatibility, checked in CI with gh skill publish --dry-run.
* [Knowledge Trust Ladder](references/knowledge-trust-ladder.md) - The Knowledge Trust Ladder (KTL), whose bundle is a .lokf/ folder in the host; beside one, the sidecar's schema becomes the bundle's domain schema, and ktl-librarian's domain-schema page is the authority on what lokf validate expects.
* [Where a LinkML schema lives](references/schema-layouts.md) - The rule both skills apply to find a LinkML schema in any repository: copier answers naming linkml-project-copier, a config.public.mk, or a schema file found by content; where the preflight looks; and how --adopt gives a found schema the toolchain in place.
* [Schema design for reuse](references/schema-design.md) - linkml-author's page on designing a LinkML schema that others can import and extend: which names reach the data and how a name defined twice across imports is caught (by the gate's gen-project, not by lint), attributes before slots with fundamental names kept as attributes, mixins, prefixed class names, a core plus modules as the shape importers can take a slice of, type designators instead of kind enums, typed references, no enum inheritance, minor releases that only add, and when a schema that exists can still be refactored.
* [Publishing a schema others can import](references/publishing.md) - linkml-author's page on how a schema reaches an importer: two addresses under its id (every module at schema/module.yaml and one merged file with no imports), a tagged release with a checksummed asset, a vendored copy at a tag or an import by persistent identifier and never by a code-host URL, the importmap and the order an import resolves in, and lokf's adapt for a vocabulary that shares names with yours.

# Policies

* [AI covenant](policies/ai-covenant.md) - Community norms for AI use: contributors own what they submit whatever tools helped, AI review comments are suggestions, AI systems must not post comments or replies in issues, discussions, chat or mail, and AI co-authorship in commit messages is discouraged.
* [Code of conduct](policies/code-of-conduct.md) - The Contributor Covenant code of conduct that covers participation in this repository.
* [Releasing](policies/releasing.md) - How a release is cut: semantic-release.yml waits for a reviewer of the release environment and then promotes Unreleased in CHANGELOG.md to the next version, a maintainer runs publish.yml by hand with that version, gh skill publish creates the tag and the release for both skills, installers read the tag, and the plugin marketplace reads main.

# Glossary

* [Sidecar](glossary/sidecar.md) - A hidden folder, .linkml/, that holds a complete schema project beside a host's own code, around a dummy schema or a schema the host already holds, with nothing in the host's build depending on it.
* [Doorway](glossary/doorway.md) - The linkml_schema link at the host's root that shows the hidden sidecar's schema folder under an ordinary, visible name.
* [Dummy schema](glossary/dummy-schema.md) - The small placeholder schema a fresh sidecar holds, a Person example or, beside a KTL bundle, ExampleConcept, which lints clean and which linkml-author replaces with the host's real model.
* [Template pin](glossary/template-pin.md) - The one place the linkml-project-copier version is fixed: LINKML_TEMPLATE_REF and LINKML_TEMPLATE_SHA in the scaffold driver, a tag verified against its commit before copier runs with --trust.
* [Domain schema](glossary/domain-schema.md) - A LinkML schema that imports LOKF's core schema so its is_a Concept classes become types a .lokf/ bundle's concepts may carry, checked by lokf validate --schema; a schema is one only when .lokf/justfile names it or it imports lokf.yaml, as the sidecar's dummy does in KTL mode.
* [The gate](glossary/the-gate.md) - linkml-author's check after every schema edit: lint, then gen-project, then test, through the project's justfile or Makefile, or the three LinkML tools directly for a schema with no project, with lokf validate after it beside a KTL bundle that names the schema.
