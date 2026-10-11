# Upstream proposal: a `layout` answer for linkml-project-copier

A draft for an issue on [linkml/linkml-project-copier](https://github.com/linkml/linkml-project-copier), to file when the maintainer of this skill decides to. It follows the maintainer's reply on issue #151 (2026-05-24) that a layout putting "everything except `.github` into a single folder" should be doable, and the sidecar item on the v1.0.0 wishlist in issue #93. Filing it is a person's call, not the skill's.

## Title

A `layout` answer that keeps everything except `.github/` under one folder

## Body

The template renders a repository root. A project that already has a root (a domain codebase adopting LinkML for its data model) has to install it into a subfolder and then undo what assumes the root: the workflows land where GitHub never reads them, `just setup` creates a nested repository, `just deploy` pushes the host's `gh-pages` root, the README describes "the repository", and `CODE_OF_CONDUCT.md` and `CONTRIBUTING.md` duplicate the host's. The [linkml-sidecar](https://github.com/noelmcloughlin/linkml-sidecar) skill does that undoing today, from a catalogue of the assumptions. Most rows of that catalogue would disappear with one answer:

- `layout`: `root` (today's behaviour) or `sidecar`.
- `sidecar_dir`: the folder name, default `.linkml`, asked only when `layout` is `sidecar`.
- With `sidecar`: render the workflows at the repository root as `linkml-<name>.yaml` with `defaults.run.working-directory: <sidecar_dir>` and `cache-dependency-glob: "<sidecar_dir>/uv.lock"`; render no `CODE_OF_CONDUCT.md`, `CONTRIBUTING.md` or `dependabot.yml`; make `setup` skip `_git-init`, `_git-add` and the commit; make `deploy` publish under a subpath or refuse; render a README variant that says the folder is a sidecar; change `_message_after_copy` to name `just install` and the gate; set `site_url` to the host's Pages URL plus `/<sidecar_dir>/`.

Copier itself already handles the subfolder: `copier update` scopes its dirty check and its `_skip_if_exists` patterns to the subproject. Only the template's rendering assumes a root.

I can open a pull request for this if the shape is right.
