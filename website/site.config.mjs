// The site's values and options, in one place. scripts/config.mjs reads this
// file, fills in every option left out, settles each "auto" against the
// repository and checks the required values; `node scripts/config.mjs`
// prints the result. Nothing here runs code, so the pages that show the
// title import it too.
//
// The first five values are required. The rest are optional: leave one out,
// or set it to "auto", and the site shows that part of the repository when
// the repository has it; set it to null to leave that part out.

// The repository, as owner/name, and the site's address: the owner's GitHub
// Pages domain and the path under it. A user site (the <owner>.github.io
// repository) or a custom domain sets BASE to "".
export const REPO = "noelmcloughlin/linkml-sidecar";
export const SITE = "https://noelmcloughlin.github.io";
export const BASE = "/linkml-sidecar";

// The site's title, in the header and on every social card, and its
// description, for search engines and as the home page's tagline when
// HOME.tagline is not set.
export const TITLE = "linkml-sidecar";
export const DESCRIPTION = "Two Agent Skills that give a code repository a LinkML data model as a sidecar: linkml-sidecar installs a hidden .linkml/ project from linkml-project-copier without touching the host's build, and linkml-author turns its dummy schema into the real model and keeps it generated, documented and tested.";

// The branch an "Edit page" link opens.
export const BRANCH = "main";

// A custom domain, which the sync writes to public/CNAME, or null for a
// Pages address. The domain's DNS stays the repository's own business.
export const CUSTOM_DOMAIN = null;

// The logo, as paths from the repository root: a light version, a dark one
// (the light one again when left out) and a favicon (the light logo when it
// is an SVG, else the site's own ladder mark). "auto" takes the Knowledge
// Trust Ladder logo: a knowledge-trust-ladder-logo.svg the repository
// already has, or else the copy in src/assets/. A single path is the light
// version alone. null shows the title as text.
//   export const LOGO = { light: ".assets/logo.svg", dark: ".assets/logo-dark.svg" };
export const LOGO = "auto";

// The folder of figures the README and the docs pages show, served under
// /assets/. "auto" takes .assets/ when there is one.
export const ASSETS = "auto";

// The docs pages: a folder, and the sidebar groups its pages sit in, each
// page named by its path under the folder without .md. With no groups, every
// page sits in one Guides group, by title. With groups, the sync stops with
// an error when a group names a missing page or a page has no group, so a new
// page cannot go missing from the sidebar. "auto" takes docs/ when there is
// one; null shows no docs pages.
//   export const DOCS = { dir: "docs", groups: [{ label: "Guides", pages: ["install", "usage"] }] };
export const DOCS = "auto";

// A Keep a Changelog file, read as a page per release. "auto" takes
// CHANGELOG.md when it holds a released version.
export const CHANGELOG = "auto";

// The tag a release carries, with {version} for its number. A release page
// links the repository, the docs and the bundle at that tag, and the release
// itself, when git has the tag. A repository whose tags carry no "v" sets
// "{version}"; null links nothing.
export const RELEASE_TAG = "v{version}";

// Pages from files outside the docs folder, each at /<slug>/, listed in the
// Guide sidebar after Home under its label. An entry's `retells` names the
// file whose page it retells, and `level` the words for its reading level
// (the label when left out): both pages then offer each other under their
// titles.
//   export const PAGES = [{ slug: "simple", source: "docs/overview.en-simple.md", label: "In short", retells: "docs/overview.md" }];
export const PAGES = [];

// The LinkML schema's pages, which gen-doc writes, under a Schema topic: a
// folder, and the command that writes it, which the sync runs when the
// folder is missing. "auto" takes the first of the root, a linkmo project
// and .linkml/ whose justfile has a gen-doc recipe; null shows no schema.
//   export const SCHEMA = { dir: "docs/elements", build: "just gen-doc" };
export const SCHEMA = "auto";

// The data: a folder of SQLite databases and their Datasette metadata, served
// under /browse/ with a page that opens each in Datasette Lite, and the
// command that writes it. The databases go on the public site, so it is null
// until set; "auto" takes a linkmo project's browse/ folder.
//   export const BROWSE = { dir: "browse", build: "just build-browse" };
export const BROWSE = null;

// The workspace of a domain host, which the knowledge-federation workflow
// serves at workspace/ under the site, and which the graph page offers to
// draw beside the bundle's own graph. "auto" offers it when the repository
// has that workflow; true offers it always, and null never.
export const WORKSPACE = "auto";

// The home page: its source, from the file's `# ` title down ("auto" takes
// the README when it has one, else the bundle's own introduction); the
// tagline under the title (a string, { boldLineOf: <file> } for the first
// line of that file that is bold throughout, or DESCRIPTION when null); and
// the buttons, with site-relative links (Browse the bundle, Architecture when
// the docs have an architecture page, Bundle health and Knowledge graph when
// null).
export const HOME = { source: "auto", tagline: null, actions: null };
