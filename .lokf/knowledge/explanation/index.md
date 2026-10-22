# Explanation

* [Three cases, one skill](two-patterns.md) - Why there are three ways to give a repository a LinkML schema: a repository that is itself a schema project runs copier at its root and needs nothing here, a domain codebase whose maintainers do not want a schema project in their root gets the hidden .linkml/ sidecar, and a repository holding a schema but no project gets the sidecar around that schema.
* [KTL mode](ktl-mode.md) - What changes when the host carries a .lokf/ Knowledge Trust Ladder bundle: the sidecar's dummy schema becomes the bundle's domain schema, and the scaffold pins .lokf/lokf.yaml, writes an ExampleConcept dummy, excuses LOKF's camelCase slots in the linter and names the schema in .lokf/justfile; an adopted schema is not made the domain schema.
