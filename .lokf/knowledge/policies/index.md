# Policies

* [AI covenant](ai-covenant.md) - Community norms for AI use: contributors own what they submit whatever tools helped, AI review comments are suggestions, AI systems must not post comments or replies in issues, discussions, chat or mail, and AI co-authorship in commit messages is discouraged.
* [Code of conduct](code-of-conduct.md) - The Contributor Covenant code of conduct that covers participation in this repository.
* [Releasing](releasing.md) - How a release is cut: semantic-release.yml waits for a reviewer of the release environment and then promotes Unreleased in CHANGELOG.md to the next version, a maintainer runs publish.yml by hand with that version, gh skill publish creates the tag and the release for both skills, installers read the tag, and the plugin marketplace reads main.
