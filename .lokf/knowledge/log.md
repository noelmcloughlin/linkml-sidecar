# Change Log

## 2026-10-22

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
