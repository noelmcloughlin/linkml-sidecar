# Portability: the sidecar on another host

The scaffold writes files, so any directory tree works. What varies is the shell, the version control, the forge, the network, and what each step can do there. **Run the preflight first.** Before the sidecar exists it is `bash <skill>/templates/scripts/linkml-preflight.sh <host-root>`, where `<skill>` is this skill's directory; afterwards it is `.linkml/scripts/linkml-preflight.sh`. Its last line names your case. If a line names something you cannot fix yourself, [prerequisites.md](prerequisites.md) says who can, and what to send them.

| Host | Works | Lost | Substitute |
| --- | --- | --- | --- |
| Linux, git, GitHub | everything | - | - |
| macOS | everything, on the stock bash 3.2 | - | - |
| RHEL 9 or 8 | everything | RHEL 8's `python3`, 3.6, which the scaffold passes over | a Python of 3.10 or later for the project: uv downloads one, or `dnf install python3.12` (below) |
| WSL2 | everything | - | `JUST_TEMPDIR` for the template's `just clean` (below) |
| Windows, Git for Windows | everything from its bash; the template's justfile already names that shell | the `ln -s` doorway | a junction (below) |
| Windows, PowerShell | uv, copier, just, the generators | the two scripts, which are bash | run them through Git for Windows' bash (below) |
| Behind a company proxy or package mirror | everything | github.com and PyPI | a company copy of the template, the mirror, and uv told to trust the company's certificates (below) |
| Codeberg, Forgejo | everything; the site is published on Codeberg only | the GitHub Actions workflow | the Forgejo workflow ([automation.md](automation.md#forgejo-and-codeberg)) |
| GitLab, Gitea | the sidecar, the gate, the docs build | the GitHub Actions workflow | the gate as a job of the host's CI ([automation.md](automation.md#other-forges)) |
| No forge, git only | everything local; `just update` | the workflow, pull requests | the host's own review |
| git installed, the folder not a repository | the sidecar, the gate, the docs | `copier update`, which needs the destination under git; the package version (`0.0.0`) | re-run the scaffold into a scratch clone to see what a new template version changes, and copy by hand |
| git not installed | nothing: copier fetches the template with git, and the scaffold checks the tag with it | the sidecar | install git; the preflight reports it as `missing` |
| A uv workspace at the root | untested | - | the preflight warns; try `just install` and report |

## RHEL

RHEL 9's `python3` is 3.9: enough for the scaffold, which needs 3.8, and for copier, but not for the project, which needs 3.10. uv downloads a Python for the project when it may. Where it may not, install one from the system's packages, `sudo dnf install python3.12`, and uv finds it. RHEL 10's `python3` is 3.12 already.

RHEL 8's `python3` is 3.6, which the scaffold passes over: it runs through `uv run`, which finds the newer Python. Set `UV_PYTHON=3.12` there as well, or uv builds copier and just on the old `python3` and downloads a Python for them.

A company's root certificate goes into the system's store (`/etc/pki/ca-trust/source/anchors/`, then `update-ca-trust extract`), where git and curl read it. uv reads it only when told to ([below](#behind-a-company-proxy-or-package-mirror)).

## WSL2

Under WSL2 the template's justfile refuses `just clean`, and warns on a bare `just`, until `JUST_TEMPDIR` is set: `export JUST_TEMPDIR=/tmp`, in `~/.bashrc` to keep it. `install`, `lint`, `test` and `gen-doc` need nothing. Keep the repository on the Linux file system rather than under `/mnt/c`, as Microsoft advises for speed. WSL's `autoProxy` setting, on by default on Windows 11, passes the Windows proxy to the distribution as `HTTPS_PROXY` and the other proxy variables.

## Windows

Git for Windows' bash runs both scripts. From PowerShell: `& "C:\Program Files\Git\bin\bash.exe" -lc "bash skills/linkml-sidecar/scripts/linkml-scaffold.sh --dry-run"`, with the facts exported in that shell. The doorway is a junction, which needs no elevated rights: `mklink /J linkml_schema .linkml\src\<slug>\schema` from the host root, in `cmd`. The template's justfile sets its shell to Git for Windows' bash already, so `just --justfile .linkml/justfile lint` works from PowerShell once `just` is installed (`uv tool install rust-just`). It names `C:/Program Files/Git/bin/bash`, so where Git for Windows is installed for one user only, run the recipes from Git Bash itself.

## Behind a company proxy or package mirror

Each of these is a setting on the machine or the runner, never in the repository. The preflight's `network` line asks the template's source and the index as git and uv reach them, so it shows whether a setting took.

- **The proxy.** git, curl and uv read `HTTPS_PROXY`, `HTTP_PROXY` and `NO_PROXY`.

- **The company's certificates.** A proxy that inspects TLS signs traffic with the company's own root certificate. Once that is in the system's store, git and curl trust it. uv trusts its own bundled roots until `UV_SYSTEM_CERTS=true` is set (uv 0.11 or later; `UV_NATIVE_TLS=1` before that). `SSL_CERT_FILE` serves too, when it names the system's bundle: `/etc/pki/ca-trust/extracted/pem/tls-ca-bundle.pem` on RHEL, `/etc/ssl/certs/ca-certificates.crt` on Debian and Ubuntu. A path that does not exist makes uv trust nothing. The preflight's `copier` line says when certificates are the cause.

- **The package mirror.** `UV_DEFAULT_INDEX` names it, or an `[[index]]` entry with `default = true` in a user `uv.toml` (`~/.config/uv/uv.toml`) or the system's (`/etc/uv/uv.toml`). Credentials stay in the environment (`UV_INDEX_<NAME>_USERNAME` and `_PASSWORD`) or in `~/.netrc`. Nothing in the sidecar names `exclude-newer`, so a mirror that serves no upload times works.

- **A Python.** uv downloads one from releases.astral.sh when the machine has none it can use. `UV_PYTHON_INSTALL_MIRROR` names a company copy; or install one from the system's packages.

- **uv itself.** Its installer downloads from releases.astral.sh. Through the mirror, `python3 -m pip install --user uv` installs it instead.

**Make the lock where CI installs from.** `uv.lock` records the index it was made against, and every file's address there. A lock made against PyPI fails `uv sync --locked`, the workflow's install step, on a machine whose index is a mirror, and `just install` there rewrites every address in it to the mirror's. A lock made behind the mirror fails on GitHub's runners, and names the mirror's host in the repository. So make the lock against PyPI for GitHub's runners, and against the mirror for runners that install through it. The preflight's `lock` line says when the lock and this machine's index differ. uv has no setting yet that lets one lock serve both ([astral-sh/uv#6349](https://github.com/astral-sh/uv/issues/6349)).

## The template without github.com

A company copy of linkml-project-copier takes the place of github.com in one of two ways. Either way the scaffold checks that the copy's tag names the commit it pins, so the copy must carry the template's tags.

- A git rule, which every clone on the machine follows. The answers file still names the template as `gh:linkml/linkml-project-copier`, so a teammate who reaches GitHub can run `just update` too:

  ```bash
  git config --global url."https://git.example.com/mirrors/linkml-project-copier.git".insteadOf https://github.com/linkml/linkml-project-copier.git
  ```

- `LINKML_TEMPLATE_SRC`, for one run: a URL or a local clone. The answers file then records that source, and `just update` reads from it.

## No git

`copier update` refuses a destination that is not inside a git repository, so the template's own files cannot be updated in place. Everything else works: `uv sync`, the generators, the tests, the docs. The package's version falls back to `0.0.0`. When version control arrives later, the sidecar needs nothing: commit `.linkml/` and `just update` starts working.

## Synced or shared folders

OneDrive, Dropbox, Drive and iCloud carry `.linkml/` but drop the `linkml_schema` link, so the doorway is per machine; `just --justfile .linkml/justfile linkml-link` recreates it. Exclude `.linkml/.venv/` from the sync: it is large, machine-specific, and `just install` rebuilds it.

## Another forge

Step 5 has a workflow for GitHub and one for Forgejo, which Codeberg runs. [automation.md](automation.md) says how to set up the Forgejo one, which steps port unchanged to any other CI (all the shell), and what GitLab's Pages needs instead of the publish job.

## What is tested

CI runs the tests on Ubuntu. The scripts are written for bash 3.2 and POSIX tools, so macOS, RHEL and Git for Windows are covered by design rather than by a run there. Run the preflight once on such a host, and report a difference as an issue. CI checks the Forgejo workflow's shape, not a run of it; [CONTRIBUTING.md](https://github.com/noelmcloughlin/linkml-sidecar/blob/main/CONTRIBUTING.md) says how a change to it is run with Forgejo's own runner.
