# Designing a schema others can import and extend

This page is for the author who designs the model as well as the schema. It collects the decisions that settle whether another schema can import this one, and whether a later release can add to it without breaking the data already written. Where [SKILL.md](../SKILL.md)'s rules table and this page meet, the table is the rule and this page the reason. The page grows as more sources are folded in.

A schema written to fit data that already exists keeps the data's slot names and enum values, and `.linkmllint.yaml` excuses them from `standard_naming`. Its class and enum names are still free, for the reason the next section gives.

## What reaches the data

Slot and attribute names are the keys of every serialised record, and permissible values are its values. Class and enum names never appear in a record, except as the value of a type designator. So renaming a class or an enum touches no data, and renaming a slot or a value breaks every record that uses it.

Every name in a schema's import closure shares one namespace. Two schemas that each define `Person` clash in a third that imports both, so the names a schema adds are a cost to everyone who imports it. The clash is silent. The LinkML FAQ asks for names unique across imports and the specification says a duplicate fails the derivation, but `SchemaView` merges the closure without a word: of two imports in one list, the one listed last wins, and `linkml-lint` says nothing (seen on 1.12.1). A clash is found by reading, or by a check that walks the closure, never by an error.

## Fields

- **Attributes first.** Start every class with `attributes:`. Lift a field to a top-level slot only when a second class needs the same field with the same meaning, or when the field carries a `slot_uri` identity. A global slot adds a name to the shared namespace that also appears in data, and it moves part of a class's definition away from the class.
- **The more fundamental the name, the likelier the clash.** Every vocabulary declares `id`, `name`, `description`, `type`, `url`, `version`, a part-of pair and a date or two; `hasReasonDenial` or `numParameters` clashes with nothing. ai-atlas-nexus's core module shares nine slot names with LOKF's `lokf.yaml` (`id`, `name`, `description`, `url`, `version`, `isPartOf`, `hasPart`, `startDate`, `endDate`) and four class names (`Concept`, `Dataset`, `Organization`, `Policy`); lokf's `adapt` of Biolink dropped `id` and `type` and renamed every other shared name. So a fundamental field is an attribute, or an attribute of one mixin, and a top-level slot only as part of a base vocabulary the schema means to share. Such a slot carries a `slot_uri`, so the IRI survives when an importer has to rename it (`adapt` pins the IRI and keeps the old name in `aliases`). The upstream alternative to importing at all is to define your own class and reuse the `class_uri` (the FAQ, and linkml discussion 1739).
- **A clash can arrive later.** A vocabulary you import may add a name you already use in its next release (discussion 1739 again). A check that walks the closure for duplicate names belongs in CI, not in a one-time review; lokf's `adapt --check` is one, and a short `SchemaView` script is another.
- **An attribute avoids the name clash, not the IRI clash.** Two classes in two modules that each declare an attribute `type` under one `default_prefix` induce one IRI, and `gen-owl` warns `Ambiguous attribute` for each (1.12.1; linkml issues 388 and 2403, both open, ask what the metamodel means by it). When the two mean one thing, declare one slot with a `slot_uri` and use it in both. When they differ, give each attribute its own `slot_uri`.
- **A mixin for fields that unrelated classes share.** When `created_at` and `modified_at` recur in classes with no common parent, declare them once as attributes of `AcmeTrackedMixin` (`mixin: true`) and list it under each class's `mixins:`. The schema gains one class name instead of two slot names, and no new key appears in data. A `rules:` entry on the mixin, such as "`modified_at` is not earlier than `created_at`", is inherited with the fields.
- **No `alias` to get around a clash.** Declaring two global slots and giving one an `alias` so both can appear under one key works, but the two attributes it stands for are simpler.

## Names

- **Classes** are `PascalCase`. In a schema meant to be imported, they carry a prefix of the schema's own as part of the name: `AcmeOrder`, not `Order`. RDF needs no prefix, because the namespace already makes the term unique, so set `class_uri: acme:Order` when the prefix is unwanted there.
- **A mixin** ends in `Mixin` (`AcmeTrackedMixin`). The suffix shows at a glance which classes are mixins, so a class that inherits one through `is_a` stands out in review.
- **A class that serves one field of one class** is named after both: `AcmeOrderShippingAddress` for the value of `Order.shipping_address`.
- **Slots and attributes** are `snake_case` and never prefixed, because a prefix would appear in every record.
- **Enums** are named like classes, in the singular, for what one value is (`OrderStatus`), with no `Enum` suffix.
- **Permissible values** keep one style throughout the schema; this skill's rule is `snake_case`. Some values must keep punctuation (`n/a`), start with a digit (`2fa`), or differ from another only by case (`Gb` and `GB`). Give each of those a `title` that has none of these, so the docs and every tool that reads titles have a readable name for it.

## Kinds of one thing

Model the kinds of one thing as subclasses of a base class whose `type` attribute is `designates_type: true`. A `Notification` base with `EmailNotification` adding `subject` and `SmsNotification` adding `phone_number` says in its structure which fields each kind admits. The designator's allowed values are the names of the base class and its descendants. The alternative, one class with a `channel` enum and fields whose descriptions say "only when the channel is email", leaves the constraint to prose, or to rules that grow with every kind.

A class that holds such things takes one multivalued field whose range is the base class: `notifications: {range: Notification, multivalued: true}`, not one field per kind. A new kind is then a new subclass, and the holder does not change. The cost is that a per-kind count, such as "at most one SMS", can no longer be said on the holder.

## References between objects

A field of range `string` whose description says "an identifier of a customer" checks nothing. Mark the target's key `identifier: true` and give the referring field `range: Customer`. A range class with an identifier is referenced by its key unless the field is `inlined: true`, so a validator can now check that each value names a customer. Where the objects themselves are written, in the collection on the `tree_root` class, set `inlined: true` and `inlined_as_list: true` explicitly. [metamodel.md](metamodel.md) has the inlining table.

## Modules: a core and the rest

An importer rarely wants a whole vocabulary. `imports:` has no selective form (linkml issue 238, open since 2021, and the FAQ's "not yet"), a `subset` partitions the docs and nothing else, and a generator's `--subset` cuts its output, not an import. So the only slice another schema can take is a module, and a schema that expects importers is written as several:

- **A core module** holds the bases, the shared slots, the enums and the prefixes. It imports only `linkml:types`, and it lints on its own.
- **A module per topic** imports the core and the modules it references, nothing more, and lints on its own.
- **An umbrella** imports every module and declares only the `tree_root` container. It is the file the project names, the one a sidecar adopts, and the one the generators run on.
- **No cycle.** Two modules that import each other cannot be taken apart, and a core that uses a class it does not import cannot be loaded alone.

ai-atlas-nexus took this shape, a `common` core and seven topic modules under an umbrella that holds one container, and then let the modules import each other both ways and the core use classes from the modules; a consumer that imported it got a `FileNotFoundError` (its issues 182, 228 and 232). The oscal and gist schemas in lmodel, an experiment area for these patterns, keep the umbrella and the modules acyclic.

The cost of modules is management. Each module is a schema file to the preflight; `gen-doc` needs `--render-imports` and lint walks the closure ([generators.md](generators.md)); a release must carry every module at the same relative path; and each module needs an address of its own to be importable by URL ([publishing.md](publishing.md)). One `default_prefix` across every module puts all their elements in one IRI space, which is where the attribute IRI clash above comes from; a prefix per module avoids it.

## Enums

Do not inherit one enum from another. The metamodel has two ways to say it, `is_a` and `inherits`, and linkml issues 3957 and 3958 ask which is meant. The generators do not apply either, except `gen-owl` behind an opt-in flag. Repeat the values, or bind both enums' values to the same `meaning` terms so the shared meaning is still declared.

## Releases and compatibility

Call a change compatible when data valid under the old schema stays valid under the new one.

- **A minor release only adds**: classes, attributes, enums, permissible values. It never removes an element, renames one, tightens a range, a pattern or a cardinality, or makes an optional field required. A rename counts as an addition plus a removal. Loosening a constraint is compatible, and so is deprecating an element that stays in place with its data still accepted.
- **A change that breaks data is a major release.** A migration between the two is a LinkML-Map transformation, outside the schema.
- **Three version strings coexist.** The `version:` metaslot carries the full release number. An `imports:` entry names a schema, not a release, so the URI a schema is published at decides which release an importer gets ([publishing.md](publishing.md) says how to serve one); a URI that names only the major version can follow the newest compatible release. The element IRIs that `default_prefix` builds carry only the major version, so a minor release does not rename every term in RDF.

A fact the metamodel has no metaslot for, such as the release an element was added in, goes in a structured annotation rather than a sentence in a description. Declare a class whose attributes are the annotation keys (`AcmeChangeNote` with `introduced_in`), and on each annotated element write `instantiates: [acme:AcmeChangeNote]` and `annotations: {introduced_in: "1.2"}`. `instantiates` names the class by URI, not by name. Generators ignore the annotation, and the validator does not enforce `instantiates` ([generators.md](generators.md)), so a small tool of the project's own reads it.

## Refactoring a schema that exists

A schema that exists is not a schema in use. Most LinkML schemas are one maintainer's experiment, and a release count says nothing about users: ai-atlas-nexus has twenty releases and none carries a schema file, and most lmodel schemas, which exist to try patterns, have no release at all. The signal is the people in the schema folder's history. The preflight's `authors` line prints how many have committed to the folder, the names that commit most, and the same count for the repository. One or two people, and the schema can still change shape. A team's history means every change has to be additive, because the habits and the data of people you cannot ask depend on it. A known importer is the second signal: a package that loads the schema, a schema that imports it, a release asset someone fetches. With one, keep to the moves that touch no record, and name the importer in the hand-off.

The offer is made in words and never carried out unasked ([SKILL.md](../SKILL.md)'s guardrails).

Moves that touch no record and change no IRI:

- **Fold a slot one class uses into that class's attribute.** The key in the data is unchanged, and so is the induced IRI. `gen-owl` stops writing an `rdfs:range` for it; the JSON-LD context and the JSON Schema come out identical (1.12.1).
- **Split one file into a core and modules, or merge modules back.** Names and IRIs stay; only an importer's path changes.
- **Pin `class_uri` and `slot_uri`** on every element that may be renamed later, so the IRI outlives the name.

Moves that touch records, each a major release with the two-release deprecation (LinkML's how-to on deprecating elements keeps the retired element in a `deprecated.yaml` so its IRI still resolves; ai-atlas-nexus's pull request 250 renamed slots that way):

- renaming a slot or a permissible value;
- renaming a class that a type designator writes into records. Prefixing class names is safe only where no designator carries them.

As an example and not a verdict: ai-atlas-nexus's single-class slots (`LLMQuestionPolicy`'s three, `Term`'s two, `RiskIncident`'s eight, `BenchmarkMetadataCard`'s forty or so) are attribute candidates, and its nine fundamental names are the ones to pin with a `slot_uri` and expect importers to rename.

## Before the gate

- Does every class start with attributes, and is each top-level slot used by more than one class?
- Would any class, slot or enum name clash with a schema likely to be imported beside this one? Is a fundamental name among the top-level slots, and does it carry a `slot_uri`?
- Is every reference typed by its range, and is every collection explicitly inlined as a list?
- Is any field's applicability stated only in a description, when a subclass would state it?
- Does each module lint alone, and is there no import cycle? Is the umbrella the file the project names?
- Whose schema is this, one person's or a team's, and is a refactor on offer or off the table?
- Does the change only add? If not, is the release a major one, and was the removal a deprecation first?

## Sources

- [github/lmodel](https://github.com/lmodel) and [w3id/ids/lmodel](https://github.com/perma-id/w3id.org/tree/master/ids/lmodel) experiments
- [github linkml projects](https://github.com/linkml/)
- [github gouttegd LinkML guidelines draft](https://github.com/gouttegd/linkml-guidelines/blob/main/linkml-guidelines.xml)
