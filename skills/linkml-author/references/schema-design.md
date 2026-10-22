# Designing a schema others can import and extend

This page is for the author who designs the model as well as the schema. It collects the decisions that settle whether another schema can import this one, and whether a later release can add to it without breaking the data already written. Where [SKILL.md](../SKILL.md)'s rules table and this page meet, the table is the rule and this page the reason. The page grows as more sources are folded in.

A schema written to fit data that already exists keeps the data's slot names and enum values, and `.linkmllint.yaml` excuses them from `standard_naming`. Its class and enum names are still free, for the reason the next section gives.

## What reaches the data

Slot and attribute names are the keys of every serialised record, and permissible values are its values. Class and enum names never appear in a record, except as the value of a type designator. So renaming a class or an enum touches no data, and renaming a slot or a value breaks every record that uses it.

Every name in a schema's import closure shares one namespace. Two schemas that each define `Person` clash in a third that imports both, so the names a schema adds are a cost to everyone who imports it.

## Fields

- **Attributes first.** Start every class with `attributes:`. Lift a field to a top-level slot only when a second class needs the same field with the same meaning, or when the field carries a `slot_uri` identity. A global slot adds a name to the shared namespace that also appears in data, and it moves part of a class's definition away from the class.
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

## Enums

Do not inherit one enum from another. The metamodel has two ways to say it, `is_a` and `inherits`, and linkml issues 3957 and 3958 ask which is meant. The generators do not apply either, except `gen-owl` behind an opt-in flag. Repeat the values, or bind both enums' values to the same `meaning` terms so the shared meaning is still declared.

## Releases and compatibility

Call a change compatible when data valid under the old schema stays valid under the new one.

- **A minor release only adds**: classes, attributes, enums, permissible values. It never removes an element, renames one, tightens a range, a pattern or a cardinality, or makes an optional field required. A rename counts as an addition plus a removal. Loosening a constraint is compatible, and so is deprecating an element that stays in place with its data still accepted.
- **A change that breaks data is a major release.** A migration between the two is a LinkML-Map transformation, outside the schema.
- **Three version strings coexist.** The `version:` metaslot carries the full release number. An `imports:` entry names a schema, not a release, so the URI a schema is published at decides which release an importer gets; a URI that names only the major version can follow the newest compatible release. The element IRIs that `default_prefix` builds carry only the major version, so a minor release does not rename every term in RDF.

A fact the metamodel has no metaslot for, such as the release an element was added in, goes in a structured annotation rather than a sentence in a description. Declare a class whose attributes are the annotation keys (`AcmeChangeNote` with `introduced_in`), and on each annotated element write `instantiates: [acme:AcmeChangeNote]` and `annotations: {introduced_in: "1.2"}`. `instantiates` names the class by URI, not by name. Generators ignore the annotation, and the validator does not enforce `instantiates` ([generators.md](generators.md)), so a small tool of the project's own reads it.

## Before the gate

- Does every class start with attributes, and is each top-level slot used by more than one class?
- Would any class, slot or enum name clash with a schema likely to be imported beside this one?
- Is every reference typed by its range, and is every collection explicitly inlined as a list?
- Is any field's applicability stated only in a description, when a subclass would state it?
- Does the change only add? If not, is the release a major one, and was the removal a deprecation first?
