# Change Log

## 2026-10-29

* **Changed**: KTL mode says the scaffold also writes the schema's path as `[tool.lokf] schema`, that the `cd` workaround is needed only at a lokf 0.8.0 floor, and that removal drops the table's line.

## 2026-10-26

* **Changed**: the assumptions catalogue links linkml-project-copier#187 from its body, not its `references`, because a typed relation names a concept and the federation gate fails on a target no member owns.

## 2026-10-24

* **Changed**: The bundle's namespace is now the persistent identifier `https://w3id.org/ktl/linkml-sidecar/knowledge/`, and every concept's id moves with it. Knowledge website names `https://w3id.org/ktl/linkml-sidecar/` as the site's address.

## 2026-10-22

* **Changed**: Template pin: the contract now holds the pin's mentions under `docs/` and in `CONTRIBUTING.md` too, as check 8 and the scaffold driver's header say.
* **Changed**: linkml-sidecar skill: Step 5 now offers a Forgejo Actions workflow beside the GitHub one.
* **Changed**: Preflight: it now checks the template's source and the package index as git and uv reach them, says why copier failed, warns on a new `lock` line when `uv.lock` names another index, and looks for workflows in the folder the forge reads.
* **Changed**: Scaffold: the driver now runs its Python half through `uv run` on the half's own script header, then a python3 or python of 3.8 or later, and exits 2 when it finds none.
* **Changed**: Sidecar workflow: Step 5 now has a Forgejo Actions template beside the GitHub one, which runs the same gate and publishes to Codeberg Pages. A pin bump is copied into both templates, and the other forges follow `automation.md`.
* **Changed**: Repository contract: check 9 now covers both workflow templates, and check 8 reads `docs/` and `CONTRIBUTING.md` for the template pin as well.
* **Changed**: Contributing now gives the slow-test clone command and the CI job list. Its action-pin rule covers the Forgejo template beside the GitHub one, and a new step says how the Forgejo template is checked.
* **Changed**: KTL mode: PR 3855 is described as its source states it, and the README source moves to `docs/architecture.md`.
* **Changed**: Knowledge Trust Ladder: `docs/architecture.md` joins the sources, since the README no longer names the `.lokf/` folder.
* **Changed**: linkml-project-copier: the README source moves to `docs/architecture.md`, which carries the MIT credit, and the concept adds that a company copy's tag must name the same commit.
* **Changed**: Three cases: re-pointed from the README to `docs/architecture.md` and `layouts.md`, and the adopt clause and the list of root assumptions now follow those pages.
* **Changed**: Sidecar: the resource moves from the README to `docs/architecture.md`, and the body follows that page for the doorway, the workflow and the build output.
* **Changed**: Installing the skills now follows `docs/install.md`: gh skill first, npx with `--global`, the `/plugin` commands, a copy of the repository, user or project scope, the pin, the workflow switch and what each skill needs.
* **Added**: Who owns which file, from the ownership, never-run and keeping-current sections of `docs/architecture.md`, which no concept covered.
* **Added**: Portability, the reference page on which hosts the sidecar works on and what each loses: RHEL, WSL2, Windows, a company proxy or package mirror, other forges, and the template from a company copy.
* **Changed**: Knowledge sources: `docs/` joins the map, its two pages take over what the README stated, and the Forgejo workflow template joins the workflow row.
* **Changed**: the assumptions catalogue cites linkml-project-copier#187, where the layout proposal is filed, in place of the draft that left the skill.
* **Removal**: Upstream layout proposal; the draft left `skills/linkml-sidecar/references/` once it was filed as linkml-project-copier#187.
* **Prose**: reworded 6 concept bodies in plain English. No fact, link, number or frontmatter changed.
* **Changed**: The linkml-sidecar skill playbook drops the claim that most schema repositories have no project, as SKILL.md has.
* **Changed**: Releasing now describes the semantic-release and publish.yml workflows that replaced tagging by hand, as CONTRIBUTING.md states.
* **Changed**: Two patterns no longer claims that most schema repositories have no project, and names the files that mark a schema, as README.md now does.
* **Changed**: Schema layouts follows layouts.md, which no longer says most schemas were made without a template.
* **Changed**: KTL mode says a bundle beside a schema may be about the repository, where ktl.md no longer says often.
* **Changed**: the preflight concept drops the repository count, which the authors line no longer prints.
* **Changed**: the schema design concept says that a name defined twice across imports passes lint but fails the gate's gen-project, as the page now does.
* **Changed**: the publishing concept follows the page's corrected importmap rules: the base directory of a relative value, and gen-project's route through generator_args.
* **Changed**: the preflight concept says the authors line counts bot commits apart and quotes the names it prints.
* **Changed**: the linkml-author playbook says how the skill reads the authors line.
* **Added**: the publishing page, on where a schema is served, how an importer takes it, the importmap and lokf's adapt.
* **Changed**: the schema design page gained the collision gradient, a core plus modules, and the refactoring moves that touch no record.
* **Changed**: the linkml-author playbook names the refactor offer, the preflight's `authors` line and the publishing page.
* **Changed**: the preflight prints an `authors` line with the people in the schema folder's history and the repository's.
* **Changed**: the scaffold renames the template's config.yaml to generators.yaml, and `--repair generators.yaml` moves an existing project's file.
* **Changed**: the preflight's generators line offers to move a project's config.yaml to .linkml/generators.yaml.
* **Changed**: the linkml-sidecar skill keeps the generators' settings in .linkml/generators.yaml, and offers the move to an existing project.
* **Changed**: the linkml-author skill edits generators.yaml as the project's own, and offers the move from config.yaml.
* **Changed**: the gate's gen-project reads generators.yaml, or config.yaml before the move.
* **Changed**: the catalogue has a twentieth row, on the generators' settings and what copier update leaves alone after the move.
* **Changed**: where a LinkML schema lives says both uses of .linkml/ keep the generators' settings at .linkml/generators.yaml.
* **Changed**: the copier reference cites the catalogue for why the template needs --trust.
* **Changed**: schema design for reuse follows its source page, now written in its own words and examples.
* **Prose**: reworded 3 concept bodies in plain English. No fact, link, number or frontmatter changed.
* **Changed**: the linkml-author skill finds a schema by what files say in any repository, runs tools through the host's justfile, Makefile or environment, and follows the new design rules.
* **Changed**: the linkml-sidecar skill now covers three cases, adopts a schema the host already holds, and installs around configuration files in .linkml/.
* **Changed**: the preflight finds a schema project or schema file by what files say, in any layout, and names how the tools run on it.
* **Changed**: the scaffold stages its output, never removes .linkml/, refuses a clash, and adopts a schema in place with --adopt.
* **Changed**: KTL mode says an adopted schema, or any schema beside a bundle, is the domain schema only when .lokf/justfile names it or it imports lokf.yaml.
* **Changed**: two patterns became three cases: a schema the repository already holds gets the sidecar around it.
* **Changed**: a schema beside a bundle is a domain schema only when .lokf/justfile names it or it imports lokf.yaml.
* **Changed**: the sidecar term covers adoption and a .linkml/ folder that also holds LinkML configuration files.
* **Changed**: an adopted schema gets no dummy, and --dummy asks for one beside an existing schema.
* **Changed**: the gate runs through any project's justfile or Makefile, and has a form for a schema with no project.
* **Changed**: an adopted schema gets no doorway.
* **Changed**: the catalogue has a nineteenth row, on config.public.mk and its possible retirement.
* **Changed**: the upstream proposal carries the caveat that .linkml/ is also proposed for LinkML's configuration files.
* **Changed**: the KTL reference says an adopted schema is not made the domain schema.
* **Changed**: the workflow concept says an adopted schema's folder joins both paths lists.
* **Changed**: the source map names the README's Three cases section.
* **Added**: where a LinkML schema lives, from `skills/linkml-sidecar/references/layouts.md`.
* **Added**: schema design for reuse, from `skills/linkml-author/references/schema-design.md`.
* **Prose**: reworded 3 concept bodies in plain English. No fact, link, number or frontmatter changed.

## 2026-10-21

* **Added**: the knowledge website, from `website/README.md`, `site.config.mjs` and `knowledge-website.yaml`.
* **Changed**: the knowledge sources map lists `website/` and its workflow, which the new website playbook covers.
* **Prose**: reworded 7 concept bodies in plain English. No fact, link, number or frontmatter changed.
* **Added**: the linkml-sidecar skill, from `skills/linkml-sidecar/SKILL.md`.
* **Added**: the linkml-author skill, from `skills/linkml-author/SKILL.md`.
* **Added**: installing the skills, from the README's Install and Run it yourself sections.
* **Added**: the contributor checklist, from `CONTRIBUTING.md`.
* **Added**: the scaffold script, from its header and Step 1 of the linkml-sidecar skill.
* **Added**: the preflight script, from its header, Step 0 of the linkml-sidecar skill and the prerequisites page.
* **Added**: the hoisted workflow, from the template and `references/automation.md`.
* **Added**: the repository contract, from `scripts/validate-repository.sh` and `validate.yml`.
* **Added**: the two patterns, from the README and the linkml-sidecar skill.
* **Added**: KTL mode, from `references/ktl.md` and the author's KTL page.
* **Added**: the template assumptions catalogue, from `references/template-assumptions.md`.
* **Added**: the upstream layout proposal, from `references/upstream-proposal.md`.
* **Added**: the upstream template, from the linkml-sidecar skill and the scaffold driver.
* **Added**: LinkML, as both skills cite it.
* **Added**: the Agent Skills specification, as the README and the contract cite it.
* **Added**: the Knowledge Trust Ladder, as the README and `references/ktl.md` cite it.
* **Added**: the AI covenant, from `AI_COVENANT.md`.
* **Added**: the code of conduct, from `CODE_OF_CONDUCT.md`.
* **Added**: the release policy, from `CONTRIBUTING.md`.
* **Added**: the sidecar term, from the README.
* **Added**: the doorway term, from Step 2 of the linkml-sidecar skill.
* **Added**: the dummy schema term, from linkml-author and the assumptions catalogue.
* **Added**: the template pin term, from the scaffold driver and `CONTRIBUTING.md`.
* **Added**: the domain schema term, from `references/ktl.md` and linkml-author.
* **Added**: the gate term, from linkml-author.
* **Added**: the knowledge sources map.
* **Removal**: Example Service A, the sidecar's placeholder.
* **Removal**: Example Service B, the sidecar's placeholder.
* **Initialization**: Scaffolded the LOKF bundle for linkml-sidecar with placeholder
  services. Real concepts to follow.
