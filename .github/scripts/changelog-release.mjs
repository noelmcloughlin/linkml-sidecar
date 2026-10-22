#!/usr/bin/env node
// Reads and rewrites this repository's own CHANGELOG.md "## [Unreleased]"
// section for the semantic-release pipeline in
// .github/workflows/semantic-release.yml. Plain Node, no dependencies:
// reviewable in one read, matching this project's preference for a fixed,
// in-repo script over an inline command string (see knowledge-librarian.sh).
//
// Usage:
//   node changelog-release.mjs check [version]
//       Exits 1 if "## [Unreleased]" is empty. Used as semantic-release's
//       verifyReleaseCmd, so a release with nothing written up never goes out.
//       With a version arg, an empty section passes when that version is
//       already promoted and waits for publish.yml: a push with nothing
//       to release, such as a docs merge after a feat, still finds the feat
//       since the last tag, and its notes are already written.
//
//   node changelog-release.mjs notes [version]
//       Prints the Unreleased section's body to stdout; it becomes the
//       release notes when used as generateNotesCmd. With a version arg,
//       also appends `next_version=<version>` to $GITHUB_OUTPUT if that
//       env var is set (a side channel a caller can read even from a
//       --dry-run invocation, where nothing else is written anywhere).
//       It appends nothing when the section is empty and that version is
//       already promoted, so the workflow commits no promotion.
//
//   node changelog-release.mjs promote <version> <date>
//       Retitles "## [Unreleased]" to "## [<version>] - <date>" and
//       inserts a fresh, empty "## [Unreleased]" above it. The top released
//       section is still pending when no tag `v<its version>` exists,
//       because publish.yml has not been run since the last promotion. Then
//       the Unreleased entries are folded into it, subsection by subsection,
//       and it takes the new version and date, so two qualifying pushes
//       between publishes never leave two headings for one release. Used
//       as semantic-release's prepareCmd (never called in --dry-run). Also
//       appends `released=true` and `version=<version>` to $GITHUB_OUTPUT
//       if set.

import { readFileSync, writeFileSync, appendFileSync } from "node:fs";
import { execFileSync } from "node:child_process";

const FILE = "CHANGELOG.md";
const HEADING = "## [Unreleased]";
const RELEASED = /^## \[(\d+\.\d+\.\d+)\] - \d{4}-\d{2}-\d{2}$/;

function readUnreleased() {
  const text = readFileSync(FILE, "utf8");
  const start = text.indexOf(HEADING);
  if (start === -1) {
    throw new Error(`${FILE} has no "${HEADING}" heading - this pipeline expects one.`);
  }
  const bodyStart = start + HEADING.length;
  const next = text.indexOf("\n## [", bodyStart);
  const bodyEnd = next === -1 ? text.length : next;
  return { text, start, body: text.slice(bodyStart, bodyEnd).trim(), end: bodyEnd };
}

// The released section directly under Unreleased, when no tag carries its
// version. publish.yml is this repository's one tag creator, so "no tag" is
// exactly "promoted, not yet published".
function pendingSection(text, from) {
  if (from === text.length) return null;
  const lineEnd = text.indexOf("\n", from + 1);
  const heading = text.slice(from + 1, lineEnd === -1 ? text.length : lineEnd);
  const m = RELEASED.exec(heading);
  if (!m) return null;
  let tagged;
  try {
    tagged = execFileSync("git", ["tag", "-l", `v${m[1]}`], { encoding: "utf8", stdio: "pipe" });
  } catch (e) {
    throw new Error(`could not list tags to tell whether ${m[1]} shipped - promote runs inside the repository checkout: ${e.message.split("\n")[0]}`);
  }
  if (tagged.trim()) return null;
  const bodyStart = lineEnd === -1 ? text.length : lineEnd;
  const next = text.indexOf("\n## [", bodyStart);
  const end = next === -1 ? text.length : next;
  return { version: m[1], body: text.slice(bodyStart, end).trim(), end };
}

// A section body as its "### " subsections, blank edges trimmed, so two
// bodies merge by subsection title rather than by concatenation.
function subsections(body) {
  const parts = [];
  let current = { title: null, lines: [] };
  for (const line of body.split("\n")) {
    if (line.startsWith("### ")) {
      parts.push(current);
      current = { title: line, lines: [] };
    } else {
      current.lines.push(line);
    }
  }
  parts.push(current);
  for (const p of parts) {
    while (p.lines.length && !p.lines[0].trim()) p.lines.shift();
    while (p.lines.length && !p.lines[p.lines.length - 1].trim()) p.lines.pop();
  }
  return parts.filter((p) => p.title !== null || p.lines.length);
}

// Keep a Changelog's order for the subsections; a preamble stays first and an
// unlisted title goes last, in the order met.
const ORDER = ["### Added", "### Changed", "### Deprecated", "### Removed", "### Fixed", "### Security"];
const rank = (p) => (p.title === null ? -1 : ORDER.includes(p.title) ? ORDER.indexOf(p.title) : ORDER.length);

// An entry the pending section already holds is left out: a branch stacked
// on another still carries the other's entries under Unreleased after the
// first one's promotion, and folding them again listed each one twice.
function mergeBodies(older, newer) {
  const merged = subsections(older);
  const held = new Set(merged.flatMap((m) => m.lines).filter((l) => l.startsWith("- ")));
  for (const part of subsections(newer)) {
    const lines = part.lines.filter((l) => !l.startsWith("- ") || !held.has(l));
    if (!lines.some((l) => l.startsWith("- ")) && part.lines.some((l) => l.startsWith("- "))) continue;
    const same = merged.find((m) => m.title === part.title);
    if (same) same.lines.push(...lines);
    else merged.push({ ...part, lines });
  }
  merged.sort((a, b) => rank(a) - rank(b));
  return merged
    .map((p) => (p.title === null ? p.lines : [p.title, "", ...p.lines]).join("\n"))
    .join("\n\n");
}

function writeOutput(line) {
  if (process.env.GITHUB_OUTPUT) appendFileSync(process.env.GITHUB_OUTPUT, line);
}

// The promoted section that already holds `version`'s notes, when the
// Unreleased section is empty: the case where a push has nothing new to
// describe. Null otherwise, including when the version differs, since then
// something new would release with no notes.
function alreadyPromoted(version) {
  const { text, body, end } = readUnreleased();
  if (body || !version) return null;
  const pending = pendingSection(text, end);
  return pending && pending.version === version ? pending : null;
}

// semantic-release prints a failing command's error with its stack, so also
// write the reason as a GitHub annotation, which the run's summary shows
// on its own line.
function fail(message) {
  if (process.env.GITHUB_ACTIONS) console.log(`::error title=${FILE}::${message}`);
  console.error(message);
  process.exit(1);
}

const [, , cmd, ...args] = process.argv;

switch (cmd) {
  case "check": {
    const [version] = args;
    const { body } = readUnreleased();
    if (!body && alreadyPromoted(version)) {
      console.error(`ok - nothing new since "## [${version}]", which waits for publish.yml.`);
      break;
    }
    if (!body) {
      fail(
        `${FILE}'s "${HEADING}" section is empty. This pipeline only releases what a ` +
          "person or agent has already described there - write it before merging to main."
      );
    }
    console.error(`ok - "${HEADING}" has ${body.length} characters to release.`);
    break;
  }

  case "notes": {
    const [version] = args;
    const { body } = readUnreleased();
    const pending = alreadyPromoted(version);
    if (pending) {
      process.stdout.write(pending.body + "\n");
      break;
    }
    if (version) writeOutput(`next_version=${version}\n`);
    process.stdout.write(body + "\n");
    break;
  }

  case "promote": {
    const [version, date] = args;
    if (!version || !date) {
      console.error("usage: changelog-release.mjs promote <version> <date>");
      process.exit(1);
    }
    const { text, start, body, end } = readUnreleased();
    if (!body) {
      console.error(`${FILE}'s "${HEADING}" section is empty; refusing to promote nothing.`);
      process.exit(1);
    }
    const pending = pendingSection(text, end);
    let promoted;
    if (pending) {
      const section = `${HEADING}\n\n## [${version}] - ${date}\n\n${mergeBodies(pending.body, body)}\n`;
      promoted = text.slice(0, start) + section + text.slice(pending.end);
      console.error(
        `folded "${HEADING}" into the unpublished "## [${pending.version}]" section, ` +
          `now "## [${version}] - ${date}" in ${FILE}`
      );
    } else {
      promoted = text.replace(HEADING, `${HEADING}\n\n## [${version}] - ${date}`);
      console.error(`promoted "${HEADING}" to "## [${version}] - ${date}" in ${FILE}`);
    }
    if (promoted === text) {
      throw new Error(`Replacement had no effect - is "${HEADING}" definitely in ${FILE}?`);
    }
    writeFileSync(FILE, promoted);
    writeOutput(`released=true\nversion=${version}\n`);
    break;
  }

  default:
    console.error("usage: changelog-release.mjs <check|notes|promote> ...");
    process.exit(1);
}
