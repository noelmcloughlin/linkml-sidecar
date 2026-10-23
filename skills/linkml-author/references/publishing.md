# Publishing a schema others can import

This page is for the author whose schema will be imported, vendored or loaded by someone else's project. It says how a schema reaches an importer today, which address to serve it at, how an importer takes it, and how a vocabulary that was not designed to sit beside yours is brought in. Each behaviour is stamped with the LinkML version it was seen on; re-check a stamp before relying on it. [schema-design.md](schema-design.md) decides the shape of the schema; this page decides where it is read from.

## What LinkML leaves open

LinkML's own documentation says two things about distribution: a release that keeps relative imports must keep every module at the same relative path, and `--mergeimports` folds the import closure into one file "prior to distribution", which removes the network from a build. linkml-registry lists schemas found on GitHub and serves none. A proposal for schema package management, by DOIs on Zenodo or on npm and PyPI (linkml discussion 727), had no reply. So a schema reaches an importer in one of three ways: a copy in the importer's repository, the data files of a Python package, or a persistent identifier that serves the file. `linkml:types` has such an address (`https://w3id.org/linkml/types.yaml`), though the runtime reads it from its own package.

Package data serves code that is released with the schema. ai-atlas-nexus puts its schema files in its PyPI package and loads them by package path, and ai-linkmo, a consumer, reads the same installed files through an importmap. The sssom-py maintainers argued the other way (sssom-py issue 659): a LinkML schema should not have to come from a Python package, and a vendored copy is acceptable only when its version is tracked. Both hold. A project whose code is released with the schema packages it; an importer that writes its own schema needs an address or a copy.

## Two addresses

A schema that expects importers is served at two kinds of address under its `id`:

- `<id>/schema/<module>.yaml` for every source file, the umbrella included, at the same relative paths the files have in the repository;
- `<id>/<name>.yaml` for one merged file with no imports, which `gen-linkml --mergeimports -f yaml <umbrella>` writes. `gen-project` does not write it, so the project adds a recipe of its own.

Why both. An `imports:` entry written as a URL or a CURIE is fetched with `.yaml` appended, and on 1.12.1 the module's own `./core` imports are then fetched from the module's address, not looked for beside the importing file. So a modular root imports over HTTP as long as every module is served at the same relative path, which is what the first address does. Older releases resolved those imports differently, and not the same way from release to release. The changes are in linkml-runtime pull request 368 and linkml pull requests 2576, 3645 and 3855, so a build that imports by URL pins its toolkit.

The merged file is the address for everything else. It takes one request instead of one per module, and it suits an offline build, an importer that pins by checksum, and a tool that loads the file directly. Such a tool needs the full file name, because `SchemaView(url)` appends nothing.

A tag in the path pins a release: `<id>/v1.2.5/schema/common.yaml`. An `imports:` entry names a schema and not a release ([schema-design.md](schema-design.md)), so a tagged address is how an importer that needs one release says so.

lmodel, an experiment area for these patterns and not a standard, gives a worked example. Its w3id rules send `<schema>/schema/<path>.yaml` to the raw file in the repository's schema folder, on the branch and in the layout (the root or a `.linkml/` sidecar) each repository records, and a bare `<schema>/<anything>.yaml` to the root file. A further route expects a merged file the project builds itself. The counter-example is `w3id.org/ai-atlas-nexus`, which sends every path to the docs site, so its modules have no address and `imports: [nexus:common]` fails on a 404.

## A release asset

A tagged release that attaches the schema is the address a vendoring importer copies from and checks. KTL's knowledge-release workflow attaches `schema-<tag>-<name>.yaml` and its `.sha256` when `.lokf/justfile` names a domain schema, after rewriting the relative `lokf` import to the package's name, and it stops on any other local import. gist attaches `gist-linkml-lokf-<tag>.yaml` the same way. The tag is the version (linkml-project-copier issue 121 says so for its projects too). The sidecar's own workflow attaches nothing yet.

## How an importer takes it

An import by URL fetches someone else's server on every build, so a copy comes first. In order of preference:

1. **A vendored copy, pinned.** Copy the module tree, or the merged file, into the importer's repository at a tag. Record the tag and the checksum, and upgrade on purpose. linkml discussion 3298 describes the same pattern from the Ontology Development Kit: the local mirror is the source of truth, and one recipe moves it. KTL pins `lokf.yaml` beside the domain schema this way, and refreshes it when the `lokf` floor moves. For an adapted vocabulary, `lokf adapt --check` says when the copy is stale.
2. **A persistent identifier.** `imports: [biolink:biolink-model]` with `biolink: https://w3id.org/biolink/` declared, as biolink-model issue 1278 describes; w3id serves the file. The identifier is the schema's `id` namespace, which is the rule the sidecar applies to `SCHEMA_ID` as well.
3. **Never a raw code-host URL.** A branch moves, a file is renamed, and the IRI it builds is not the project's to keep.

## importmap

When the strings in `imports:` and the places the files are differ, an importmap bridges them: a JSON object from import string to location. The specification and the runtime resolve an import in this order: an importmap entry, then a URL, then a CURIE expanded through the schema's prefixes, else a path relative to the importing file; `.yaml` is appended in every case. Seen on 1.12.1:

- a key may be the CURIE (`"nx:common"`), the expanded IRI, or a namespace (`"nx:"` mapped to a folder);
- a value omits `.yaml`; a value that ends in it fails on `common.yaml.yaml`;
- a relative value resolves against the directory of the schema the tool was given, even for an import that a module elsewhere makes; not against the map file's directory, and not against the working directory;
- each generator takes `--importmap` (`-im`). `gen-project` takes it as `importmap` in a generator's `generator_args` block of `generators.yaml`, as a path read from the working directory, which `just` sets to the project's; linkml-project-copier issue 175 asks the template to set it up. `linkml-validate` takes none yet (linkml pull request 3707 is open). The format is undocumented upstream (linkml issue 3844).

```json
{ "nx:": "vendor/ai-atlas-nexus/" }
```

With `prefixes: {nx: https://w3id.org/ai-atlas-nexus/}` and `imports: [nx:common, nx:ai_risk]`, that map reads the vendored tree and keeps the identifiers the published schema would have.

## Bringing in a vocabulary that was not designed to sit beside yours

When the vocabulary you need shares names with the schema it must sit beside, a raw import gives the silent merge that [schema-design.md](schema-design.md) describes. lokf's `adapt` makes a copy that can sit beside `lokf.yaml`. It is experimental, in lokf's main branch and not yet released, and was tried on Biolink 4.4.4, over fifteen thousand lines in one file. It makes six moves:

1. fold the vocabulary's imports into one file;
2. drop its identifier slot and its `type` designator, because the host's `id` and `type` take over;
3. detach what inherited from them, and demote the other designators;
4. rename every other shared name to `<prefix>_<name>` or `<Prefix><Name>`, pin the original IRI, and keep the old name in `aliases`;
5. re-root the top classes on the host's base class;
6. give every element one canonical form of name.

The command is `lokf adapt VOCAB -o OUT --root Class --lokf PATH --prefix P`. `--dry-run` shows the moves, and `--check` in CI says when the published vocabulary has moved. gist does the same without the toolkit, with a rename list in its justfile and a script that checks the names. Either way the moves are the rules of [schema-design.md](schema-design.md) applied after the fact, which is why a schema written to those rules asks none of this of its importers. Beside a KTL bundle, the copy can be the bundle's domain schema itself: [ktl-domain-schema.md](ktl-domain-schema.md) calls that the adapt route.

## Before a release

- The `id` is a persistent-identifier namespace the project controls.
- Every module has an address under it, and so does the merged file.
- The release is tagged, and the schema is attached with a checksum.
- The README says which address an importer uses, and which tag.
- CI checks the closure for duplicate names, and a vendored copy for staleness.
