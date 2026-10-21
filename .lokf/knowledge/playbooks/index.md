# Playbooks

* [linkml-sidecar skill](linkml-sidecar-skill.md) - The installer skill: it runs once to put a hidden .linkml/ LinkML schema project from linkml-project-copier into a host repository without touching the host's build, repairs one file it owns, and hands off to linkml-author.
* [linkml-author skill](linkml-author-skill.md) - The authoring skill: it adds, changes or deprecates LinkML classes, slots, enums and types, replaces the dummy schema with the host's real model, and runs lint, gen-project and test after every change, in a .linkml/ sidecar, a visible linkml/ one or a copier project at the root.
* [Installing the skills](installing-the-skills.md) - How to install linkml-sidecar and linkml-author with npx skills or as a Claude Code plugin, and how to run the preflight and the scaffold by hand without an agent.
* [Contributing](contributing.md) - The contributor checklist: development setup, the fast and slow tests, the install smoke test, what to run before a pull request, how to move the linkml-project-copier template pin, and how action pins in the workflow template follow Dependabot.
* [Knowledge sources](knowledge-sources.md) - Map of the repository locations this bundle was derived from, the classes each yields, the files left out on purpose, and how to re-check each on a future refresh.
