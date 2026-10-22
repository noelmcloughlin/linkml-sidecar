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

Names are `PascalCase`. The slots a class uses:

- `is_a`: the single parent; slots inherit down;
- `mixins`: cross-cutting behaviour, with `mixin: true` on the mixin;
- `abstract: true`: never instantiated;
- `tree_root: true`: the containment root for serialisation;
- `slots`: the top-level slots the class uses;
- `attributes`: slots only this class owns, declared inline;
- `slot_usage`: per-class refinement;
- `id_prefixes`: the CURIE namespaces its instances carry;
- `class_uri`, `*_mappings`, `see_also`, `aliases`, `annotations`, `comments`, `in_subset`, `union_of`, `rules` and `deprecated`.

A class starts with `attributes:`. A top-level slot is for a field more than one class shares ([schema-design.md](schema-design.md)).

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

  Notification:
    description: The base of every kind of notification; type names the kind.
    attributes:
      type:
        description: The kind of notification, one of this class's descendants.
        designates_type: true
        range: string

  EmailNotification:
    is_a: Notification
    attributes:
      subject:
        description: The email's subject line.
```

A `designates_type: true` field is a type designator: its allowed values are the names of the class and its descendants, and a holder's `notifications: {range: Notification, multivalued: true}` then takes every kind, with each subclass declaring the fields its kind admits. Inheritance is monotonic: `slot_usage` adds constraints and never removes one. `union_of` on a class is a choice type; see the generator note on `any_of` in [generators.md](generators.md).

## Slots

Names are `snake_case`. Define a shared slot once at the top level and refine it per class with `slot_usage`. The fields are `range` (a type, class or enum; `default_range` otherwise), `identifier: true` (the key; one per class), `required`, `recommended`, `multivalued`, `inlined` and `inlined_as_list`, `slot_uri` and `inverse` (declared on both sides). The others are `any_of`, `values_from`, `pattern`, `minimum_value`, `maximum_value`, `ifabsent`, `unit`, `deprecated`, `aliases`, and the logical flags `transitive`, `symmetric`, `antisymmetric`, `reflexive`.

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

A range class with no identifier is always inlined. Write `inlined_as_list` explicitly whenever `inlined: true` is set, so the data's shape never rests on a default.

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
```

Enum inheritance (`inherits`, or `is_a`) is unsettled upstream and the generators do not apply it: an enum that extends another repeats the values, or binds them to the same `meaning` terms ([schema-design.md](schema-design.md)). A dynamic enum (`reachable_from` with a `source_ontology` and `source_nodes`) is populated by query; validators do not resolve it at run time, so materialise it first ([generators.md](generators.md)).

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

## Descriptions, comments and notes

`description` is the element's definition (`skos:definition`). `gen-json-schema`, `gen-pydantic` and `gen-openapi` copy it into every schema, model field and UI hint they write, and they copy nothing else from the element. Keep it to one or two plain sentences that say what the element is, as a form field's hint or an API field's help text would.

The rest has a place of its own. `comments` (multivalued, `skos:note`) carries what a user of the schema should know: a caveat, a limit, a usage rule. `notes` (`skos:editorialNote`) carries what its maintainers should know: a decision and why, an open question. `see_also` carries the link, `examples` the sample, and an annotation the clause reference. `gen-doc` renders all of them on the element's page. The JSON Schema and Pydantic generators carry none of them. The rule comes from the KTL Obsidian plugins, whose settings hints showed how a long description renders in a small UI.

```yaml
slots:
  retention_period:
    description: How long a record of this kind is kept, as an ISO 8601 duration.
    range: string
    comments:
      - A period shorter than the legal minimum for the jurisdiction fails review, not validation.
    notes:
      - Kept as a string rather than a duration type until the generators agree on one.
    examples:
      - value: P7Y
```

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

Prefer one list-valued key over many keys with a prefix, so "every X on this class" is one lookup. An annotation the schema itself describes is a metamodel extension: a class whose attributes are the annotation keys, named on each annotated element by URI through `instantiates: [acme:AcmeChangeNote]` ([schema-design.md](schema-design.md)); the validator does not enforce it ([generators.md](generators.md)).

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

An import resolves in this order: an importmap entry, a URL, a CURIE expanded through the schema's prefixes, else a path relative to the importing file, with `.yaml` appended in every case. A module's own imports resolve relative to the module, on disk or behind a URL (1.12.1), so a module tree served at the same relative paths imports over HTTP. [publishing.md](publishing.md) has the addresses and the importmap; [schema-design.md](schema-design.md) has the shape of a core and its modules.
