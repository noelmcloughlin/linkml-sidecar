# What linkml-project-copier assumes of a repository root, and what the sidecar does about it

This page is for whoever maintains this skill: it is the catalogue the scaffold implements, row by row, at template **v0.5.0**. The template is built for a repository that *is* a schema project, so it renders workflows, governance files, a README and a `setup` recipe for a repository root. In a sidecar each of those is wrong, inert or harmful. The skill neutralises them one by one; the last column says which rows an upstream `layout: sidecar` answer would remove ([upstream-proposal.md](upstream-proposal.md)). Bump the heading and re-walk the rows when the pin moves.

| # | Root-install assumption in v0.5.0 | What the skill does | Gone with an upstream `layout: sidecar` |
| --- | --- | --- | --- |
| 1 | `just setup` runs `git init`, `git add .` and a commit | Never run; `just install` then the gate. The scaffold fails if `.linkml/.git` appears | yes |
| 2 | `.github/workflows/main.yaml` and `deploy-docs.yaml` are rendered inside the project, where GitHub never reads them | Left in place as the template's copies; the hoisted `linkml-sidecar.yaml` runs the gate from the root with `working-directory: .linkml` | yes |
| 3 | `.github/dependabot.yml` and `.pre-commit-config.yaml` inside the project are inert there | Documented in the sidecar README; a root `uv` Dependabot entry is suggested, not scaffolded | yes |
| 4 | `just deploy` builds the site and runs `mkd-gh-deploy`, which pushes the host's `gh-pages` branch root | Never run; the Step 5 docs job builds an artifact and publishes under the `linkml/` subpath only, gated by `LINKML_DOCS_ENABLED` | yes |
| 5 | `mkdocs.yml` sets `site_url` and `repo_url` from `project_name` | The scaffold patches both lines to `DOCS_URL` and `REPO_URL`; copier merges the file on update | partly |
| 6 | The example schema's `id` is `https://w3id.org/<org>/<project_name>` and its `name` is the project name | A skill-owned dummy with `SCHEMA_ID` and `name: <slug>` (`_skip_if_exists` keeps copier off `src/<slug>/schema/`) | no |
| 7 | `LICENSE`, `CODE_OF_CONDUCT.md` and `CONTRIBUTING.md` are generated as the repository's | `LICENSE` is the host's, pre-seeded (`existing_license_file: LICENSE`); the other two stay as template copies and the README says the host's own govern | yes |
| 8 | `README.md` describes "the repository", and the after-copy message says to run `just setup` | A skill-owned README; the scaffold prints its own next step and drops that line | yes |
| 9 | `project_name` doubles as the GitHub repository name in URLs | `PROJ_NAME` is the host repository's name | yes |
| 10 | The upstream example fails `just lint` (`ALIVE/DEAD/UNKNOWN` and an undescribed slot under the recommended rules) | `add_example: false` and a skill-owned dummy that lints clean; a deleted `_skip_if_exists` file would come back on update, so the example is never generated at all | partly |
| 11 | uv-dynamic-versioning reads the repository's git tags for the package version | Documented: the sidecar's version is the host's tag, `0.0.0` without one | no |
| 12 | A root `.python-version` is read inside `.linkml/` too | The preflight warns when it pins below 3.10 | no |
| 13 | A five-version CI matrix, PyPI publishing and a docs preview on by default | One Python version in the hoisted workflow; `gh_action_pypi` and `gh_action_docs_preview` answered `false` | yes |
| 14 | ruff, codespell, typos and pytest are configured for "the repository" | The nested `pyproject.toml` scopes them to `.linkml/`; pytest skips dot-directories from the host root; the host excludes `.linkml/` from its Markdown and link checks | partly |
| 15 | `--trust` is required (jinja2_time and migrations run template code) | The tag and the commit it names are verified before copier runs; a moved tag stops the scaffold | no |
| 16 | `just update` bumps `linkml` in `uv.lock` as well as the template; `copier update --pretend` fails in a subproject (a git pathspec run from the wrong directory), so there is no dry run | Documented: run the real update on a clean tree, read the diff, commit the lock with it | no |
| 17 | `linkml-lint` walks the import closure, so a schema that imports LOKF's inherits its camelCase slot names | KTL mode writes `.linkmllint.yaml` excusing those names, read from the pinned `lokf.yaml` | no |
| 18 | A relative `imports:` entry resolves from the working directory under `linkml.validator.validate()` (the validator drops the schema's path; fixed by linkml PR 3855, released in 1.12.0) | KTL mode's `.lokf/justfile` recipes run `lokf validate` from the schema's directory ([ktl.md](ktl.md)) | no |

Rows marked *no* are facts about LinkML, uv or git rather than about the template, and stay whatever upstream does.
