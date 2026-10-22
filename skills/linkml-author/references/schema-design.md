# Designing a schema others can import and extend

This page is for the author who designs the model as well as the schema: what to decide so that another schema can import this one, and a later version can add to it without breaking the data already written. It distils Damien Goutte-Gattat's *LinkML guidelines: authoring extensible and reusable schemas*, a 2026 draft (CC BY-SA 4.0) written from the SSSOM and PIDInst schemas. It is one practitioner's view, not a LinkML project document, and it was still being revised when this page was written. Weigh it as advice from someone who has published reusable schemas. Where [SKILL.md](../SKILL.md)'s rules table and this page meet, the table is the rule and this page the reason.

A schema retrofitted to data that already exists cannot follow all of it. Slot names and enum values stay as the data spells them, and `.linkmllint.yaml` excuses them from `standard_naming`; class and enum names are still free.

## Reuse the schema, not the model

A schema is a formal description of a model. Copying another schema's classes into yours reuses the model, and leaves no link between the two. Importing the schema reuses the schema itself: `imports: [person]` for a file beside yours, or a published schema by its IRI. That is the form worth designing for.

Every name in the import closure shares one flat namespace, so a schema that imports two others with a `Person` each has a clash. Which definition wins is unsettled upstream: the observed behaviour is that the importing schema's element masks the imported one, but parts of the reference implementation differ. The defence is on the author's side, in the names.

## Compatibility and versions

Call a change compatible when data valid under the old schema stays valid under the new one. A minor release only adds: classes, attributes, enums, permissible values. It never removes an element, renames one, tightens a range, a pattern or a cardinality, or makes an optional field required. A rename counts as an addition plus a removal. Loosening is fine, and so is deprecating an element that stays in place with its data still accepted. A change that breaks data is a major release, which owes the old one nothing. A migration between the two is a LinkML-Map job outside the schema.

Three versions coexist. The `version:` metaslot is informational, no tool reads it, and it should carry the full version. The URI the schema is published at is the one that controls which version an importer gets, because LinkML has no versioned import; a URI that names only the major version can point at the newest compatible release. The element IRIs that `default_prefix` builds should carry only the component that breaks compatibility, the major version, so that a minor release does not rename every term in RDF.

An addition can be recorded in the schema itself. Declare a metamodel extension: a class whose attributes are the annotations you want, such as `AcmeVersionable` with `added_in: {range: AcmeVersion}`, where `AcmeVersion` is an enum of the released versions. On each new element, write `instantiates: [acme:AcmeVersionable]` and `annotations: {added_in: "1.1"}`. `instantiates` names the class by URI, not by name, unlike every other class reference. LinkML ignores it; a small layer over LinkML, as SSSOM's implementations have, reads it to tell the lowest version a document conforms to. The same device serves any fact the metamodel has no metaslot for: a structured annotation whose shape the schema declares, rather than a sentence in a description. The validator does not enforce `instantiates` ([generators.md](generators.md)).

## Names

Only some names reach the data. Slot and attribute names are the keys of every serialised object, and permissible values are its values; class and enum names never appear, except through a type designator. So a class or an enum can be renamed without touching a single record, and a slot or a value cannot.

- **Classes** are `PascalCase`, and in a schema meant to be imported they carry a schema-specific prefix as part of the name (`PIDInstOwner`, `PIDInstManufacturer`), not a CURIE prefix. When the prefix is unwanted in RDF, where the namespace already makes the term unique, set `class_uri: pidinst:Owner` explicitly. A mixin ends in `Mixin` (`AcmeIdentifiableMixin`): a non-mixin class may not `is_a` a mixin, and most tools do not flag it, so the name is the guard. A class that only ever serves one attribute of one class is named after both (`AcmePersonAccountInfo`).
- **Slots and attributes** are `snake_case` and never prefixed, since the prefix would appear in every record. The clash is avoided by not making them global (next section).
- **Enums** are named like classes, in the singular, saying what one value is (`MappingCardinality`), with no `Enum` suffix. Values keep one style throughout the schema (this skill's rule is `snake_case`) and avoid spaces and punctuation. Some values must carry punctuation (`1:1`), start with a digit, or differ from another only by case (`mV`, `MV`). Give each of those a `title` free of them. A generator that derives code symbols from the text makes an unreadable or colliding name for such a value, and the title is where a readable one can be read from.

## Classes

- **Attributes first.** A slot and an attribute describe the same thing. The difference is that a slot is global and an attribute belongs to its class. Start every class with `attributes:`, and lift a field to a top-level slot only when a second class needs the same field with the same meaning. Global slots fill the namespace with names that appear in data, and they scatter a class's definition across the file.
- **A mixin for fields unrelated classes share.** When `name`, `identifier` and `identifier_type` recur in classes with no common parent, declare them once as attributes of `AcmeIdentifiableMixin` (`mixin: true`) and list it under each class's `mixins:`. The schema gains one global name instead of three, and a class name at that, so no new name appears in data. A `rules:` entry on the mixin, such as "an `identifier` requires an `identifier_type`", is inherited with the fields.
- **Not `alias`.** The metamodel itself defines `slot_definitions` with `alias: slots` to avoid a clash between two meanings of `slots`. The two could have been attributes. Declaring global slots and aliasing them around a clash is the anti-pattern the attribute form removes.
- **A list of type-designated parts, not a field per kind.** A `Computer` with `keyboard`, `mouse`, `monitors` and `printer` grows a field for every new kind of device and changes whenever one is added. Give it one `devices` field, `multivalued`, with range `AcmeDevice`, whose `type` attribute is `designates_type: true` (range `string` or `uriorcurie`), and a subclass per kind. A new kind is a new subclass and the holder is unchanged. The cost is per-kind cardinality: "at least one keyboard" can no longer be said on the holder.
- **Variants of one thing are subclasses, not a kind enum.** One `Vehicle` class with a `type: VehicleType` enum and fields whose descriptions say "only when type is car" leaves the constraint to prose, or to rules that grow with every kind. A base class carrying the type designator, with `MotorizedVehicle` adding `power` and `Car` adding `windshield_surface`, says it in the structure: the designator's allowed values are the descendants' names, and each kind admits the fields its class declares. The enum disappears.

## Enums

Do not inherit one enum from another. Two metaslots exist for it, `is_a` and `inherits`, and the metamodel and the documentation disagree on which is meant (linkml issues 3957 and 3958 are open). The reference implementation does not compute inherited values, and the generators differ: `gen-owl` has an opt-in flag, and the rest do not apply it. Repeat the values, or bind both enums' values to the same `meaning` terms so the shared meaning is still declared.

## References between objects

An attribute of range `string` whose description says "the value must match an author's `id`" states an intention and checks nothing. Mark the target's key `identifier: true` and give the referring attribute `range: Author`: a range class with an identifier is referenced by key unless `inlined: true`, so the same `authored_by` now takes author identifiers and a validator can check them. Where the objects themselves live (the collection on the `tree_root` class), write `inlined: true` and `inlined_as_list: true` explicitly, since the specification leaves `inlined_as_list`'s default open. [metamodel.md](metamodel.md) has the inlining table.

## Before the gate

- Does every class start with attributes, and is each top-level slot used by more than one class?
- Would any class, slot or enum name clash with a schema likely to be imported beside this one?
- Is every reference typed by its range, and is every collection explicitly inlined as a list?
- Is any field's applicability stated only in a description, when a subclass would state it?
- Does the change only add? If not, is the version a major one, and is the removal a deprecation first?
