# Architecture

This page explains how linkml-sidecar gives a repository a LinkML data model without touching its build, what each of its two skills does, and why. [Install](install.md) says how to get them.

## A sidecar beside the code

A **sidecar** is one hidden folder, `.linkml/`, beside the host's code. It holds a complete [linkml-project-copier](https://github.com/linkml/linkml-project-copier) project: the schema in one file, and a `just` recipe for every generator, from JSON Schema and Pydantic models to OWL, SHACL, TypeScript and a documentation site. One visible doorway, `linkml_schema`, links to the schema's folder for file managers that hide dot-folders. One workflow checks the schema on every pull request that touches it. Nothing in the host's build depends on any of it, and the README inside says how to remove it.

The schema is the source: everything the generators write is build output.

## Two skills

| Skill | Role | Runs |
| --- | --- | --- |
| [`linkml-sidecar`](../skills/linkml-sidecar/SKILL.md) | **The installer.** It runs the preflight, gathers the project's facts from its manifests, README and git remote, runs one scaffold script, validates the result with the project's own tools, and hands off with a list of what it guessed. It also repairs a file it owns. | once |
| [`linkml-author`](../skills/linkml-author/SKILL.md) | **The author.** It replaces the dummy schema with the host's model and keeps it linted, generated, documented and tested, in a sidecar or in any repository that holds a LinkML schema. | often |

The installer never writes a class, and the author never installs or repairs the sidecar.

## Three cases

- A repository that *is* a schema project, such as [lmodel/gist](https://github.com/lmodel/gist), runs copier at its root and needs no sidecar. linkml-author works there as it is.

- A codebase whose maintainers do not want a schema project in their root folder gets the sidecar, around a small dummy schema that linkml-author replaces.

- A repository that holds a LinkML schema but no project gets the sidecar around that schema (`--adopt`), and the schema is neither moved nor changed.

Both skills find a schema by its files, never by its folder's name, as [layouts.md](../skills/linkml-sidecar/references/layouts.md) sets out.

## Who owns which file

The template owns most of `.linkml/`: the justfile, `pyproject.toml`, `mkdocs.yml` and the rest that copier renders, and only `just update` changes them. The host owns the schema, its tests and example data, the sidecar's README, license and docs pages, and `generators.yaml`. The skill owns the preflight it installed, and `.linkmllint.yaml` beside a KTL bundle. Its repair rewrites them. [The README every sidecar carries](../skills/linkml-sidecar/templates/linkml/README.md) maps every file to its owner.

The template assumes it owns a repository root, so it renders workflows, governance files, a `setup` recipe and a `deploy` recipe that are inert or harmful in a subfolder. The scaffold switches each of them off, and [template-assumptions.md](../skills/linkml-sidecar/references/template-assumptions.md) says how, row by row. Its last column marks the rows that a `layout: sidecar` answer would remove. [linkml-project-copier#187](https://github.com/linkml/linkml-project-copier/issues/187) proposes that answer upstream.

## The scaffold trusts the template only at its pin

Copier runs template code while it renders (`--trust`), so the scaffold first checks that the pinned tag still names the commit it records, and stops if the tag has moved. A company copy of the template works the same way: its tag must name the same commit. The scaffold renders into a staging folder beside `.linkml/` and moves the files in only when no name clashes with a file already there. A failure removes the staging folder and nothing else.

## What never runs

`just setup` runs `git init` and commits, which would nest a repository inside the host, and `just deploy` pushes the root of the host's `gh-pages` branch. Neither ever runs. The workflow builds the site and publishes it under the `linkml/` subpath only, once a repository variable says so: to GitHub Pages, or to Codeberg Pages with the Forgejo workflow.

## With Knowledge Trust Ladder

Beside a [Knowledge Trust Ladder (KTL)](https://w3id.org/ktl/) bundle, `.lokf/`, the sidecar's schema becomes the bundle's domain schema. It imports LOKF's core schema. Each of its own classes that is `is_a: Concept` is a type the bundle's concepts may carry, and `lokf validate --schema` checks the bundle against both schemas. [ktl.md](../skills/linkml-sidecar/references/ktl.md) says what each piece does. Without a bundle, the sidecar stands alone.

## Keeping it current

`cd .linkml && just update` moves the template to its latest release and upgrades LinkML in `uv.lock`. Run it on a clean tree, read the diff, and commit `uv.lock` and `.copier-answers.yml` with it. The preflight says which release a sidecar is at.

## Read on

| | |
| --- | --- |
| How to install the two skills, pin them and turn on the workflow | [install.md](install.md) |
| Another operating system or forge, a company network, or no git | [portability.md](../skills/linkml-sidecar/references/portability.md) |
| What each preflight line means, and who fixes it | [prerequisites.md](../skills/linkml-sidecar/references/prerequisites.md) |
| The workflow's jobs, and the Forgejo version | [automation.md](../skills/linkml-sidecar/references/automation.md) |
| Designing a schema that others can import | [schema-design.md](../skills/linkml-author/references/schema-design.md) |
| Contributing, and what each release changed | [CONTRIBUTING.md](../CONTRIBUTING.md), [CHANGELOG.md](../CHANGELOG.md) |

## Credits

- The [LinkML community](https://linkml.io/), creators of LinkML and of [linkml-project-copier](https://github.com/linkml/linkml-project-copier), the template every sidecar is made from, under the MIT License.
- [copier](https://copier.readthedocs.io/), which renders a sidecar and keeps it current.

## License

[Apache License 2.0](../LICENSE). The generated projects carry the host's own license.
