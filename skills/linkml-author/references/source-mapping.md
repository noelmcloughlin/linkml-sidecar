# Mapping a source document to a schema

This page is for the author: it says what becomes what when a specification, a standard, a code base or a data sample is turned into a LinkML schema, and the checklist to run before the gate.

## The table

| Source element | Schema target |
| --- | --- |
| A persistent noun (a thing with identity) | `class`, concrete; abstract when it is only ever a parent |
| A controlled list of values | `enum`, each value with a `description` and, where a public term exists, a `meaning` |
| A property or attribute | a schema-level `slot`, or a class-owned `attribute` |
| A verb or relationship between things | a `slot` with an object `range`, and its `inverse` declared on both sides |
| A containment root (the document, the collection) | a class with `tree_root: true` |
| An inheritance hierarchy | an `is_a` chain; a shared cross-cutting behaviour becomes a `mixin` |
| A domain-specific scalar (a code, a duration, a unit) | a `type` with `typeof` or `uri`, and a `pattern` when the format is fixed |
| An external code or identifier | `meaning` on an enum value, `*_mappings` on a class or slot, `id_prefixes` on a class whose instances carry CURIEs |
| A grouping of the standard (a chapter, a functional area) | a `subset`, applied with `in_subset` |
| A clause or section reference | an `annotation` (a string), never the clause's text |
| A rule that holds under a condition | `rules` with `preconditions` and `postconditions` |

## The procedure

1. Read the source section by section; list its nouns, its lists, its properties and its relationships before writing any YAML.
2. Decide the identity of each class: which slot is its `identifier`, and what prefix its instances carry.
3. Write classes top-down, parents first; list only the slots a class adds, not the ones it inherits.
4. Write slots once, at the top level, and refine per class with `slot_usage`.
5. Write enums with every value described; bind values to public terms with `meaning` only when the match is sure.
6. Add subsets for the source's own groupings, and `see_also` links to the source's public location.
7. Paraphrase descriptions. A standard's text is its publisher's; a comment may cite the clause, never reproduce it.
8. Write one valid example per class that carries data, and one counter-example per constraint that matters.
9. Run the gate: `lint`, `gen-project`, `test`.

## The checklist

- Every class has a description, and an `identifier` where instances have identity.
- Every slot has a description and a range, and `multivalued`, `required` or `inlined` where the data says so.
- Every enum value has a description; `meaning` is present where a public term exists and absent where none is sure.
- `is_a` matches the source's hierarchy; a mixin is used for behaviour shared across branches, not for a second parent.
- `class_uri` and `slot_uri` use the schema's own prefix; upstream identifiers are in `exact_mappings`.
- No generated file was edited; `docs/index.md` says what the model covers.
