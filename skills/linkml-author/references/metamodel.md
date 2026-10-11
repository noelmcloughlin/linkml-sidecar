# The metamodel, as an author uses it

This page is the detail [SKILL.md](../SKILL.md) points to: the parts of the LinkML metamodel a schema author reaches for, with one example each. The language reference at <https://linkml.io/linkml/schemas/> is the authority; this page is the short form. Separate the major sections of a schema (`prefixes`, `imports`, `types`, `subsets`, `enums`, `classes`, `slots`) and each element with a blank line.

## The header

```yaml
id: https://example.org/schema/acme        # the schema's IRI; every element IRI starts with its prefix
name: acme                                 # the slug: snake_case, same as the file and the package
title: Acme
description: >-
  One sentence saying what the model covers.
license: Apache-2.0
see_also:
  - https://acme.example/linkml/            # the published docs
version: 1.2.0                             # optional; the vendor or spec version the model renders

prefixes:
  acme: https://example.org/schema/acme/    # the schema's own namespace: the id plus /
  linkml: https://w3id.org/linkml/
  schema: http://schema.org/
  dcterms: http://purl.org/dc/terms/
  skos: "http://www.w3.org/2004/02/skos/core#"
default_prefix: acme
default_range: string

imports:
  - linkml:types
  - ./acme_enums                           # a module beside this file
```

A prefix key is an NCName: no hyphens. When the schema's name has one, the key takes an underscore and the IRI keeps the hyphen, so CURIEs expand to the path a redirect serves.

## Classes

Names are `PascalCase`. The slots a class uses: `is_a` (single parent; slots inherit down), `mixins` (cross-cutting behaviour, `mixin: true` on the mixin), `abstract: true` (never instantiated), `tree_root: true` (the containment root for serialisation), `slots` (top-level slots the class uses), `attributes` (slots only this class owns, declared inline), `slot_usage` (per-class refinement), `id_prefixes` (CURIE namespaces its instances carry), `class_uri`, `*_mappings`, `see_also`, `aliases`, `annotations`, `comments`, `in_subset`, `union_of`, `rules`, `deprecated`.

```yaml
classes:

  NamedThing:
    abstract: true
    description: Anything with an identity and a name.
    slots: [id, name, description]
    class_uri: schema:Thing

  Control:
    is_a: NamedThing
    description: A safeguard an organisation applies.
    slots: [implementation_groups]
    slot_usage:
      description:
        description: What the control requires, in one sentence.
    id_prefixes: [CIS]
    exact_mappings: [WIKIDATA:Q1632136]
    in_subset: [core_controls]

  ControlCollection:
    tree_root: true
    description: A holder for Control objects.
    attributes:
      controls:
        description: The controls in this collection.
        range: Control
        multivalued: true
        inlined_as_list: true
```

Inheritance is monotonic: `slot_usage` adds constraints and never removes one. `union_of` on a class is a choice type; see the generator note on `any_of` in [generators.md](generators.md).

## Slots

Names are `snake_case`. Define a shared slot once at the top level and refine it per class with `slot_usage`. The fields: `range` (a type, class or enum; `default_range` otherwise), `identifier: true` (the key; one per class), `required`, `recommended`, `multivalued`, `inlined` and `inlined_as_list`, `slot_uri`, `inverse` (declared on both sides), `any_of`, `values_from`, `pattern`, `minimum_value`, `maximum_value`, `ifabsent`, `unit`, `deprecated`, `aliases`, and the logical flags `transitive`, `symmetric`, `antisymmetric`, `reflexive`.

```yaml
slots:

  id:
    identifier: true
    range: uriorcurie
    description: A unique identifier for a thing.
    slot_uri: schema:identifier

  name:
    description: A human-readable name.
    slot_uri: schema:name

  depends_on:
    description: Something this thing needs.
    range: NamedThing
    inverse: depended_on_by
    multivalued: true

  topic:
    description: The topic, from the curated list or free text.
    any_of:
      - range: TopicEnum
      - range: string

  height_in_cm:
    range: float
    unit:
      ucum_code: cm
```

### Cardinality

| UML | LinkML |
| --- | --- |
| `1` | `required: true` |
| `0..1` | neither required nor multivalued |
| `1..*` | `required: true`, `multivalued: true` |
| `*` | `multivalued: true` |
| `n` | `multivalued: true`, `exact_cardinality: n` |
| `m..n` | `multivalued: true`, `minimum_cardinality: m`, `maximum_cardinality: n` |

### Defaults

```yaml
slots:
  status:
    range: StatusEnum
    ifabsent: StatusEnum(active)
  retries:
    range: integer
    ifabsent: int(3)
```

### Inlining

| Data shape | Schema |
| --- | --- |
| reference by key: `parts: [part:1]` | `inlined: false` (the default for a class with an identifier) |
| a list of objects | `inlined: true`, `inlined_as_list: true` |
| a dict keyed by identifier | `inlined: true`, `inlined_as_list: false` (the range needs an identifier) |

A range class with no identifier is always inlined.

## Enums

Names are `PascalCase`; values are `snake_case`, each with a `description` and, where a public term exists, a `meaning` (a CURIE whose prefix is declared). Enums cannot be inlined.

```yaml
enums:

  VitalStatus:
    description: Whether a person is living.
    permissible_values:
      alive:
        description: The person is living.
        meaning: PATO:0001421
      dead:
        description: The person is deceased.
        meaning: PATO:0001422
      unknown:
        description: Not known.

  ExtendedStatus:                 # composition
    inherits: [VitalStatus]
    permissible_values:
      presumed_dead:
        description: Missing beyond the legal period.
```

A dynamic enum (`reachable_from` with a `source_ontology` and `source_nodes`) is populated by query; validators do not resolve it at run time, so materialise it first ([generators.md](generators.md)).

## Types and subsets

```yaml
types:

  ControlId:
    uri: xsd:string
    base: str
    pattern: "^CIS-[0-9]+\\.[0-9]+$"
    description: A CIS control identifier.

  KilogramValue:
    typeof: float
    unit:
      ucum_code: kg

subsets:

  core_controls:
    description: The foundational controls.
```

A subset partitions the schema for documentation and filtering (`in_subset: [core_controls]`) and has no semantic effect.

## Identity and mappings

| Key | On | Meaning | RDF/OWL |
| --- | --- | --- | --- |
| `class_uri`, `slot_uri`, `enum_uri`, a type's `uri` | element | the element's identity | the term IRI generators emit |
| `exact_mappings` | class, slot, enum | one-to-one equivalence | `owl:equivalentClass` / `owl:equivalentProperty` |
| `close_mappings` | class, slot | substantially similar | `skos:closeMatch` |
| `narrow_mappings`, `broad_mappings` | class, slot | this term is more specific or more general | `skos:narrowMatch`, `skos:broadMatch` |
| `related_mappings` | class, slot | related, no precise fit | `skos:relatedMatch` |
| `meaning` | enum value | the public term | `owl:sameAs` |
| `id_prefixes` | class | the CURIE namespaces instances carry | |
| `values_from` | slot | an open vocabulary's namespace | |

The identity keys (`class_uri`, `slot_uri`) use the schema's own prefix, which `gen-doc` renders as the element's IRI and which should resolve, through a w3id redirect, to the docs. The upstream identifier goes in `exact_mappings`. When an element *is* a public term (a Dublin Core property, a schema.org class), keep that term as its identity rather than shadowing it. Local names match the LinkML names (`PascalCase` classes, `snake_case` slots) so the docs' URL slugs and the IRIs agree. Never guess a mapping; leave it out, or use `related_mappings` with a comment.

## Constraints and rules

```yaml
classes:

  Isotope:
    unique_keys:
      main:
        unique_key_slots: [atomic_number, mass_number]

  Address:
    slots: [street, country, postal_code, telephone]
    rules:
      - preconditions:
          slot_conditions:
            country:
              any_of:
                - equals_string: USA
                - equals_string: USA_territory
        postconditions:
          slot_conditions:
            postal_code:
              pattern: "[0-9]{5}(-[0-9]{4})?"

slots:

  phone:
    pattern: "^[\\d\\(\\)\\-]+$"

  age_in_years:
    range: integer
    minimum_value: 0
    maximum_value: 150
    equals_expression: "{age_in_months} / 12"

  full_name:
    string_serialization: "{first} {last}"

  vital_status:
    required: true
    range: Any
    any_of:
      - range: MissingValueEnum
      - range: VitalStatusEnum
```

The boolean forms, on a class or a slot: `any_of` (at least one holds), `all_of` (every one), `none_of` (none), `exactly_one_of` (exactly one). Reusable sub-patterns go under `settings:` and are used through `structured_pattern` with `interpolated: true`. `defining_slots` on a class makes membership follow from the slots' ranges (an equivalence axiom in OWL).

## Annotations

Annotations are opaque key-value metadata on any element; generators ignore them, and a custom template or a script reads them.

```yaml
classes:
  WorkflowStep:
    annotations:
      standard_clause: "6.1"       # a string
      functions:                   # a nested value: say in a comment who parses it
        - name: check_rating
          inputs: [rating, query]
```

Prefer one list-valued key over many keys with a prefix, so "every X on this class" is one lookup.

## Arrays (LinkML 1.8+)

```yaml
slots:
  grid:
    range: integer
    array:
      exact_number_dimensions: 2
      dimensions:
        - alias: rows
        - alias: columns
          exact_cardinality: 3
```

`array: {}` allows any shape; `minimum_number_dimensions` and `maximum_number_dimensions` bound it. The Pydantic generator supports arrays; check the others before relying on them.

## Modules and imports

A module is a schema file beside the main one, imported as `./module`; a module's name is `snake_case`. Never redeclare an imported class or slot: refine an imported slot with `slot_usage` on the class that uses it. `linkml:types` is the built-in type library.
