# Explanation

* [Two patterns, one skill](two-patterns.md) - Why there are two ways to give a repository a LinkML schema: a repository that is itself a schema project runs copier at its root and needs nothing here, while a domain codebase whose maintainers do not want a schema project in their root gets the hidden .linkml/ sidecar.
* [KTL mode](ktl-mode.md) - What changes when the host carries a .lokf/ Knowledge Trust Ladder bundle: the sidecar's schema becomes the bundle's domain schema, the scaffold pins .lokf/lokf.yaml, lays down an ExampleConcept dummy, excuses LOKF's camelCase slots in the linter and wires .lokf/justfile so lokf validate --schema runs from the schema's directory.
