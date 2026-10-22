---
type: Document
id: https://noelmcloughlin.github.io/linkml-sidecar/knowledge/references/portability
title: Portability
description: "Which hosts the linkml sidecar works on and what each one loses: macOS, RHEL 8 and 9, WSL2, Windows with Git for Windows or PowerShell, a company proxy, TLS certificates or package mirror, Codeberg and Forgejo, GitLab, no forge, no git, and the template from a company copy instead of github.com."
genre: reference
resource: skills/linkml-sidecar/references/portability.md
sources:
  - resource: skills/linkml-sidecar/references/portability.md
tags:
  - portability
  - RHEL
  - WSL2
  - Windows
  - proxy
  - package mirror
  - certificates
references:
  - https://noelmcloughlin.github.io/linkml-sidecar/knowledge/services/linkml-preflight
  - https://noelmcloughlin.github.io/linkml-sidecar/knowledge/services/linkml-sidecar-workflow
  - https://noelmcloughlin.github.io/linkml-sidecar/knowledge/references/linkml-project-copier
isPartOf:
  - https://noelmcloughlin.github.io/linkml-sidecar/knowledge/playbooks/linkml-sidecar-skill
generated:
  by: process:ktl-librarian
  at: "2026-10-22T18:19:05Z"
status: draft
---

# Overview

`skills/linkml-sidecar/references/portability.md` says what works on each kind of host and what to use where something is lost. The scaffold writes files, so any directory tree works. The shell, the version control, the forge, the network and what each step can do there all vary.

Run the preflight first. Before the sidecar exists, run `bash <skill>/templates/scripts/linkml-preflight.sh <host-root>`. Afterwards, run `.linkml/scripts/linkml-preflight.sh`. Its last line names your case.

## Hosts

- Linux with git and GitHub runs everything.
- macOS runs everything, on the stock bash 3.2.
- RHEL 9 and 8 run everything. RHEL 9's `python3` is 3.9, which is enough for the scaffold and copier, but the project needs 3.10. uv downloads a Python for the project when it may, or `sudo dnf install python3.12` installs one. RHEL 8's `python3` is 3.6, which the scaffold passes over by running through `uv run`. Set `UV_PYTHON=3.12` there as well.
- WSL2 runs everything. The template's justfile refuses `just clean` until `JUST_TEMPDIR` is set, for example with `export JUST_TEMPDIR=/tmp`. Keep the repository on the Linux file system rather than under `/mnt/c`.
- Windows with Git for Windows runs everything from its bash. The `ln -s` doorway is lost, and a junction made with `mklink /J linkml_schema .linkml\src\<slug>\schema` takes its place.
- Windows PowerShell runs uv, copier, just and the generators. The two scripts are bash, so run them through Git for Windows' bash.
- Codeberg and Forgejo run everything through the Forgejo workflow, and the site is published on Codeberg only.
- GitLab and Gitea run the sidecar, the gate and the docs build. The gate runs as a job of the host's CI.
- A host with git but no forge runs everything local, including `just update`. The host's own review takes the place of the workflow and pull requests.
- A folder that is not a git repository loses `copier update`, and the package version falls back to `0.0.0`. Committing `.linkml/` later makes `just update` work.
- A machine without git gets nothing, because copier fetches the template with git and the scaffold checks the tag with it.
- A uv workspace at the root is untested. The preflight warns.

## Behind a company proxy or package mirror

Each setting belongs on the machine or the runner, never in the repository. The preflight's `network` line shows whether a setting took.

- git, curl and uv read `HTTPS_PROXY`, `HTTP_PROXY` and `NO_PROXY`.
- uv trusts its own bundled roots until `UV_SYSTEM_CERTS=true` is set (uv 0.11 or later; `UV_NATIVE_TLS=1` before that). `SSL_CERT_FILE` serves too when it names the system's bundle. A path that does not exist makes uv trust nothing.
- `UV_DEFAULT_INDEX` names the package mirror, or an `[[index]]` entry with `default = true` in a user or system `uv.toml` does. Nothing in the sidecar names `exclude-newer`, so a mirror that serves no upload times works.
- `UV_PYTHON_INSTALL_MIRROR` names a company copy of uv's Python downloads. `python3 -m pip install --user uv` installs uv itself through the mirror.
- Make `uv.lock` where CI installs from. A lock made against PyPI fails `uv sync --locked` on a machine whose index is a mirror. A lock made behind the mirror fails on GitHub's runners. The preflight's `lock` line says when the lock and the machine's index differ.

## The template without github.com

A company copy of linkml-project-copier can take the place of github.com in one of two ways. The copy must carry the template's tags, because the scaffold checks that the copy's tag names the commit it pins.

- A git `url.<copy>.insteadOf https://github.com/linkml/linkml-project-copier.git` rule applies to every clone on the machine. With this rule, the answers file still names the template as `gh:linkml/linkml-project-copier`.
- `LINKML_TEMPLATE_SRC` names a URL or a local clone for one run. The answers file then records that source, and `just update` reads from it.

## Synced folders and what is tested

OneDrive, Dropbox, Drive and iCloud drop the `linkml_schema` link, and `just --justfile .linkml/justfile linkml-link` recreates it. Exclude `.linkml/.venv/` from the sync.

CI runs the tests on Ubuntu. The scripts are written for bash 3.2 and POSIX tools, so macOS, RHEL and Git for Windows are covered by design rather than by a run there.
