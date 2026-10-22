# Step 5 automation: the hoisted workflow

`templates/github/linkml-sidecar.yaml` is the one workflow the sidecar installs, at `.github/workflows/linkml-sidecar.yaml` of the host. It has no placeholders, so every host carries the same bytes and a later fix is a plain copy. The template's own workflows under `.linkml/.github/` stay as inert copies: GitHub reads `.github/workflows/` at the root only.

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

## Other forges

The `uv sync --locked --group dev`, `just lint`, `just test` and `mkdocs build` steps port unchanged: all are plain shell in `.linkml/`. The publishing has to be rewritten. GitLab Pages serves a `public/` artifact from the pipeline, so copy `.linkml/site` to `public/linkml/` and let the host's own Pages job pick it up. Forgejo and Gitea have no Pages of their own, so publish the artifact wherever the host publishes docs. Run the gate as a job of the host's existing CI with `.linkml` as its working directory.
