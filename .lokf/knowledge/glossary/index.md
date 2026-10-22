# Glossary

* [Sidecar](sidecar.md) - A hidden folder, .linkml/, that holds a complete schema project beside a host's own code, around a dummy schema or a schema the host already holds, with nothing in the host's build depending on it.
* [Doorway](doorway.md) - The linkml_schema link at the host's root that shows the hidden sidecar's schema folder under an ordinary, visible name.
* [Dummy schema](dummy-schema.md) - The small placeholder schema a fresh sidecar holds, a Person example or, beside a KTL bundle, ExampleConcept, which lints clean and which linkml-author replaces with the host's real model.
* [Template pin](template-pin.md) - The one place the linkml-project-copier version is fixed: LINKML_TEMPLATE_REF and LINKML_TEMPLATE_SHA in the scaffold driver, a tag verified against its commit before copier runs with --trust.
* [Domain schema](domain-schema.md) - A LinkML schema that imports LOKF's core schema so its is_a Concept classes become types a .lokf/ bundle's concepts may carry, checked by lokf validate --schema; a schema is one only when .lokf/justfile names it or it imports lokf.yaml, as the sidecar's dummy does in KTL mode.
* [The gate](the-gate.md) - linkml-author's check after every schema edit: lint, then gen-project, then test, through the project's justfile or Makefile, or the three LinkML tools directly for a schema with no project, with lokf validate after it beside a KTL bundle that names the schema.
