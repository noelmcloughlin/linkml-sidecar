# Portability: the sidecar on another host

The scaffold writes files, so any directory tree works. What varies is the shell, the version control, the forge, and what each step can do there. **Run the preflight first.** Before the sidecar exists it is `bash templates/scripts/linkml-preflight.sh`; afterwards it is `.linkml/scripts/linkml-preflight.sh`. Its last line names your case. If a line names something you cannot fix yourself, [prerequisites.md](prerequisites.md) says who can, and what to send them.

| Host | Works | Lost | Substitute |
| --- | --- | --- | --- |
| Linux, git, GitHub | everything | - | - |
| macOS | everything, on the stock bash 3.2 | - | - |
| Windows, Git for Windows | everything from its bash; the template's justfile already names that shell | the `ln -s` doorway | a junction (below) |
| Windows, PowerShell | uv, copier, just, the generators | the two scripts, which are bash | run them through Git for Windows' bash (below) |
| GitLab, Forgejo, Gitea | the sidecar, the gate, the docs build | the GitHub Actions workflow | the gate as a job of the host's CI ([automation.md](automation.md)) |
| No forge, git only | everything local; `just update` | the workflow, pull requests | the host's own review |
| No git | the sidecar, the gate, the docs | `copier update`, which needs the destination under git; the package version (`0.0.0`) | re-run the scaffold into a scratch clone to see what a new template version changes, and copy by hand |
| A uv workspace at the root | untested | - | the preflight warns; try `just install` and report |

## Windows

Git for Windows' bash runs both scripts. From PowerShell: `& "C:\Program Files\Git\bin\bash.exe" -lc "bash skills/linkml-sidecar/scripts/linkml-scaffold.sh --dry-run"`, with the facts exported in that shell. The doorway is a junction, which needs no elevated rights: `mklink /J linkml_schema .linkml\src\<slug>\schema` from the host root, in `cmd`. The template's justfile sets its shell to Git for Windows' bash already, so `just --justfile .linkml/justfile lint` works from PowerShell once `just` is installed (`uv tool install rust-just`).

## No git

`copier update` refuses a destination that is not inside a git repository, so the template's own files cannot be updated in place. Everything else works: `uv sync`, the generators, the tests, the docs. The package's version falls back to `0.0.0`. When version control arrives later, the sidecar needs nothing: commit `.linkml/` and `just update` starts working.

## Synced or shared folders

OneDrive, Dropbox, Drive and iCloud carry `.linkml/` but drop the `linkml_schema` link, so the doorway is per machine; `just --justfile .linkml/justfile linkml-link` recreates it. Exclude `.linkml/.venv/` from the sync: it is large, machine-specific, and `just install` rebuilds it.

## Another forge

The workflow is GitHub Actions. [automation.md](automation.md) says which steps port unchanged (all the shell) and what each forge's Pages needs instead of the publish job.
