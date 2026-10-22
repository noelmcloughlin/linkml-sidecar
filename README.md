# linkml-sidecar

This repository holds two [Agent Skills](https://agentskills.io) that give a code repository a [LinkML](https://linkml.io) data model without touching its own build. **linkml-sidecar** installs a hidden `.linkml/` folder holding a complete, pinned [linkml-project-copier](https://github.com/linkml/linkml-project-copier) project, around a dummy schema or around a schema the repository already holds. **linkml-author** writes and keeps the schema of any repository that has one, linted, generated, documented and tested.

To install, see [the quick start](docs/install.md#quick-start). [The architecture](docs/architecture.md) says what the sidecar holds, what each skill does in each of three cases, and who owns which file. [Run the scripts without an agent](docs/install.md#run-the-scripts-without-an-agent) gives the commands for a person at a shell.

> **Only want to ask?** Install `ktl-docent` into any agent you use, by a route from [the install page](https://w3id.org/ktl/docs/install/), and ask it about this project. It answers from the bundle and says how far each answer has been checked.
>
> **Agents:** if `.lokf/knowledge/index.md` exists, read it first. `llms.txt` says how to weigh it.

The sidecar stands alone. Beside a [Knowledge Trust Ladder (KTL)](https://w3id.org/ktl/) bundle, its schema becomes the bundle's domain schema, as [the architecture](docs/architecture.md#with-knowledge-trust-ladder) describes.
