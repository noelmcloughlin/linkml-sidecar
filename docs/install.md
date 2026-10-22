# Install

This page gives every way to install the two skills, what each needs on the machine, how to pin them to one release, and how to run the installer's scripts without an agent. A repository that already holds a LinkML project needs only **linkml-author**.

## Quick start

Install both skills for your user, then ask your agent to set up a LinkML sidecar. **linkml-sidecar** runs once and hands off to **linkml-author**, which you keep using.

### GitHub CLI

This route needs [`gh skill`](https://cli.github.com/manual/gh_skill_install) version 2.90.0 or later. It defaults to GitHub Copilot, so pass `--agent` to name yours (`claude-code`, `github-copilot`, `cursor`, `codex`, `gemini-cli`, or another from `gh skill install --help`):

```bash
gh skill install noelmcloughlin/linkml-sidecar --all --scope user --agent claude-code
```

This is the route for a work machine: it needs github.com but no npm registry.

### Open Skills CLI

Install both skills with the Open Skills CLI, [`npx skills`](https://github.com/vercel-labs/skills). This route could fail behind a company proxy or an internal npm registry. Take the GitHub CLI route there instead.

```bash
npx skills add noelmcloughlin/linkml-sidecar --global --yes \
  --skill linkml-sidecar --skill linkml-author
```

In PowerShell or cmd, type the command on one line without the `\` continuation.

### Claude Code plugin

```text
/plugin marketplace add noelmcloughlin/linkml-sidecar
/plugin install linkml-sidecar@linkml-sidecar
```

### From a copy of the repository

Where github.com is out of reach, install from a company copy of this repository, or from a release archive. `npx skills add` and `/plugin marketplace add` take a git URL on any host, or a local path. The GitHub CLI takes a local folder, and needs no network for it:

```bash
git clone https://git.example.com/mirrors/linkml-sidecar.git
gh skill install ./linkml-sidecar/skills --from-local --all --scope user --agent claude-code
```

Point it at the copy's `skills/` folder, not its root: a working copy's `website/node_modules/` can hold other skills.

## Install for your user, not into the repository

The commands above install for your user, which keeps the instructions an agent follows under your control. Install into the repository only when a team wants every member on one version: leave out `--global`, or pass `--scope project`, and commit what the installer writes.

## Pin to one tag

Both skills are released together under one tag, so pin them to the same one. Append it to the skill name (`linkml-author@v0.1.1`) or pass `--pin v0.1.1`. The [changelog](../CHANGELOG.md) says what each release changed.

## Turn on the workflow

The workflow the sidecar installs checks the schema on every pull request that touches `.linkml/`. It publishes the documentation site only once the repository variable `LINKML_DOCS_ENABLED` is set to `true` (on GitHub: Settings, Secrets and variables, Actions, Variables). On Forgejo and Codeberg the sidecar installs a Forgejo workflow instead, and [automation.md](../skills/linkml-sidecar/references/automation.md#forgejo-and-codeberg) says how to set it up.

## Run the scripts without an agent

The two scripts of **linkml-sidecar** work without an agent. From the host's root, with this repository cloned beside it:

```bash
bash ../linkml-sidecar/skills/linkml-sidecar/templates/scripts/linkml-preflight.sh .
export PROJ_NAME="Acme Platform" PROJ_DESC="One sentence." GITHUB_ORG=acme \
  REPO_URL=https://github.com/acme/platform FULL_NAME="A Person" EMAIL=a.person@acme.example \
  LICENSE_ID=Apache-2.0 SCHEMA_ID=https://w3id.org/acme/platform DOCS_URL=https://acme.github.io/platform/linkml/
bash ../linkml-sidecar/skills/linkml-sidecar/scripts/linkml-scaffold.sh --dry-run
bash ../linkml-sidecar/skills/linkml-sidecar/scripts/linkml-scaffold.sh
```

Step 0 of [linkml-sidecar's SKILL.md](../skills/linkml-sidecar/SKILL.md) says where each fact comes from, and Step 1 lists the exit codes, `--repair` and `--pointers-only`.

## What each skill needs

Both skills run from a POSIX shell: on Windows, the bash of Git for Windows. **linkml-sidecar** starts with a preflight that prints what this machine can do, and which steps are switched off by what it lacks.

| Skill | Needs |
| --- | --- |
| `linkml-sidecar` | `git`, and [`uv`](https://docs.astral.sh/uv/), which runs copier, just and the project's Python: 3.10 or later, which uv downloads when the machine has none. Network access once: the template from github.com and packages from PyPI, or a company copy and mirror of each. |
| `linkml-author` | the project's own recipes (`just` or `make`), or `uv`, or the host's own environment where it already installs `linkml` |

Behind a company proxy or package mirror, on RHEL, or under WSL2, [the portability page](../skills/linkml-sidecar/references/portability.md) says what to set. If you cannot act on a line the preflight prints, [the prerequisites page](../skills/linkml-sidecar/references/prerequisites.md) gives a request note for whoever can.
