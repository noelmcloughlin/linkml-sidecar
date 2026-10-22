# Step 5 automation: the hoisted workflow

`templates/github/linkml-sidecar.yaml` is the workflow the sidecar installs on GitHub, at `.github/workflows/linkml-sidecar.yaml` of the host; on Forgejo and Codeberg, `templates/forgejo/linkml-sidecar.yaml` takes its place ([below](#forgejo-and-codeberg)). It has no placeholders, so every host carries the same bytes and a later fix is a plain copy. The template's own workflows under `.linkml/.github/` stay as inert copies: GitHub reads `.github/workflows/` at the root only.

## Jobs

| Job | Runs when | Does |
| --- | --- | --- |
| `lint-and-test` | a pull request or a push to any branch touching `.linkml/**`, `.lokf/lokf.yaml` or the workflow; dispatch | in `.linkml/`: `uv sync --locked --group dev`, `just lint`, `just test`, on Python 3.12 |
| `docs` | the same triggers as `lint-and-test`, on the repository's default branch only, after `lint-and-test` passes | `just gen-doc`, `mkdocs build`; the site kept as the `linkml-docs` artifact |
| `publish-docs` | after `docs`, only while the repository variable `LINKML_DOCS_ENABLED` is `true` | the artifact published under the `linkml/` subpath of the host's `gh-pages` branch; peaceiris replaces that subpath and nothing else, so a site the host already publishes there is left alone and the page of a deleted class is removed |

`--locked` means the lock the host committed is what runs; a sidecar whose `uv.lock` is not in git fails at the install step with an error. The preflight warns about that case.

## Setting it up

1. Commit `.linkml/` with its `uv.lock` (Step 4) and the workflow.
2. To publish the docs, create the repository variable `LINKML_DOCS_ENABLED` with the value `true` (Settings, Secrets and variables, Actions, Variables), and point Pages at the `gh-pages` branch if it is not already. The site appears at the host's Pages URL plus `/linkml/`, which is what `DOCS_URL` should have been set to.
3. A root `dependabot.yml` can keep the sidecar's Python dependencies current with a `uv` entry whose `directory` is `/.linkml`. The hoisted workflow's own action pins are bumped by the host's existing `github-actions` entry, if it has one.

## Pins

Every `uses:` names a commit, with the version in a trailing comment for Dependabot. `peaceiris/actions-gh-pages`'s pin was read from the release tag on 2026-10-07. Dependabot updates only linkml-sidecar's own workflows, so its `scripts/validate-repository.sh` fails until a bump is copied into this template too.

## Forgejo and Codeberg

`templates/forgejo/linkml-sidecar.yaml` runs the same gate on Forgejo Actions, as Codeberg runs them; its header says what differs from the GitHub template and why. To set it up:

1. Put it in the folder the preflight's `workflows` line names. Forgejo reads only the first of `.forgejo/workflows/`, `.gitea/workflows/` and `.github/workflows/` that exists, so a new `.forgejo/workflows/` beside an existing `.github/workflows/` would hide every workflow there from it.
2. On Codeberg, turn on Actions in the repository's settings, under Units, Overview; they are off by default. The jobs run on Codeberg's `codeberg-small` runner, which Codeberg offers to public repositories under a free licence. On a self-hosted Forgejo, change the two `runs-on` lines to a label its runners carry; the host owns that copy from then on.
3. To publish, set the repository variable `LINKML_DOCS_ENABLED` to `true`. The site appears at `https://<owner>.codeberg.page/<repo>/linkml/`, which is what `DOCS_URL` should have been set to. A self-hosted Forgejo has no Pages, so leave the variable unset there; the docs job then builds the site and stops.

## Other forges

On GitLab, Gitea or a forge with no CI of its own, the `uv sync --locked --group dev`, `just lint`, `just test` and `mkdocs build` steps port unchanged: all are plain shell in `.linkml/`. Run them as a job of the host's existing CI with `.linkml` as its working directory. GitLab Pages serves a `public/` folder from the pipeline, so copy `.linkml/site` to `public/linkml/` in the host's own Pages job. Gitea runs the GitHub Actions syntax, so the Forgejo template is the nearer start there, but it has not been run on Gitea.

A self-hosted runner that installs through a company package mirror needs a lock made against that mirror: [portability.md](portability.md) has the rule.
