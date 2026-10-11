# The lmodel profile

The [lmodel](https://github.com/lmodel) organisation publishes LinkML renderings of standards (ISO, NIST, OSCAL, FIX, gist and others) under one set of conventions. A project opts into them by following them already; this skill never assumes them for a host that does not.

## Identity

- `id: https://w3id.org/lmodel/<schema-name>` (kebab-case) and `name: <schema-name>`; the prefix key is the snake_case form of the same name, and its IRI is the `id` plus `/`, so a CURIE expands to the w3id path the redirect table serves.
- `license: Apache-2.0`; `see_also` names the published docs site.
- `class_uri` and `slot_uri` use the schema's own prefix, which resolves through w3id to the docs; the upstream term goes in `exact_mappings`.

## Shape

- Two abstract bases, defined once per schema: `NamedEntity` (operational entities: `id`, `name`, `description`, `created_date`, `modified_date`, `version`) and `DocumentedInformation` (`is_a: NamedEntity`; policy, procedure and record artefacts, with `document_type`, `owner`, `approved_by`, `effective_date`, `review_date`, `status`, `classification`, `retention_period` and the like). Every concrete class inherits from one of them.
- One subset per functional area of the standard, applied with `in_subset` on every class, slot and enum of that area.
- Annotation values are strings (`mandatory: "true"`, `standard_clause: "6.1"`); a nested annotation names its consumer in a comment.

## Standards text

A comment cites the clause and never reproduces it: `Reference: ISO/IEC 29100:2024 Clause X. ISO/IEC standards text is copyright ISO; not reproduced here.` Descriptions paraphrase.

## Prefixes the family shares

```yaml
prefixes:
  linkml: https://w3id.org/linkml/
  schema: http://schema.org/
  dcterms: http://purl.org/dc/terms/
  skos: "http://www.w3.org/2004/02/skos/core#"
  prov: "http://www.w3.org/ns/prov#"
  # sibling schemas, by their w3id namespaces, when cross-referenced:
  # oscal: https://w3id.org/lmodel/oscal/
```

A sibling schema is referenced by its w3id namespace, never by a `lmodel.github.io` URL: the IRI must match what the redirect table serves.
