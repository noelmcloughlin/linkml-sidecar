## Summary

## Which skill(s) changed?

- [ ] linkml-sidecar
- [ ] linkml-author
- [ ] repository packaging only (CI, docs, tests unrelated to skill content)

## Checklist

- [ ] `bash scripts/validate-repository.sh` passes locally, and so does `pytest` (`tests/conftest.py` says how to run it)
- [ ] `gh skill publish --dry-run` passes locally (or CI's `validate-skills` job is green)
- [ ] `CHANGELOG.md` has a line or two under `[Unreleased]` if this changes skill behavior
- [ ] A moved template pin re-walked `references/template-assumptions.md` and passed the slow tests
- [ ] A changed action pin in `templates/github/` names a commit, with its version in the comment

## AI Assistance

If you used AI tools while preparing this PR, you are still the author and responsible for understanding, verifying, and defending your submission. Please engage with reviewers personally rather than through your agent during feedback and revisions. See the [AI Covenant](https://github.com/noelmcloughlin/linkml-sidecar/blob/main/AI_COVENANT.md).
