# Generator pitfalls, by version

Each row names the LinkML version the behaviour was seen on. Re-check a row before relying on it on a newer version, and drop it when upstream fixes it. The project's own version is in `uv.lock`.

| Seen on | Generator | Behaviour | What to do |
| --- | --- | --- | --- |
| 1.11.1 | `gen-json-schema` | A class with `union_of:` becomes an empty `{}` definition with `additionalProperties: false`, so every instance of the union fails | On each slot whose range is the union class, add `any_of:` listing each alternative range; the JSON Schema then carries a proper `anyOf` |
| 1.11.1 | `gen-json-schema` | `additionalProperties: false` is set on every definition, so deeply nested polymorphic data may fail even with the `any_of` workaround | Keep the discriminated alternatives as separate concrete classes; validate samples of each |
| 1.11.1 | `gen-owl` | A rule using `none_of: [{equals_string: X}]` on an enum-ranged slot crashes with `AssertionError: Object None must be an rdflib term` | Write `none_of: [{equals_string_in: [X]}]`, which is equivalent and goes through the `owl:oneOf` path |
| 1.11.1 | `gen-python`, `linkml-run-examples` | A slot whose name is a Python keyword (LOKF's `from`) is written as a field name, so the dataclass module does not compile; enum values are escaped, slot names are not. The example runner compiles the same dataclasses to instantiate each valid example, so `just test` fails on any file under `tests/data/valid/` | Do not import the dataclasses of a schema that has one; the Pydantic module compiles; validate data with `linkml.validator`; keep valid examples under `tests/data/problem/valid/`, which the runner skips, until the generator escapes keyword names |
| 1.11.1 | `linkml.validator.validate(instance, path)` | The schema is loaded without its `source_file`, so a relative `imports:` entry resolves from the working directory | Load the schema with `SchemaView(path).schema` and pass that; or run from the schema's directory. Fixed by linkml PR 3855, unreleased at 1.11.1 |
| 1.11.1 | `linkml-lint` | `standard_naming` walks the import closure, so an imported schema's names are linted with the project's | A `.linkmllint.yaml` in the project directory with `standard_naming.exclude` listing those names |
| 1.11.1 | `gen-doc` | Imported elements get no page unless `--render-imports` is passed, so `is_a: Imported` links to nothing | `LINKML_GENERATORS_DOC_ARGS="--render-imports"` in `config.public.mk` |
| 1.11.1 | `gen-project` | Runs neither `gen-pydantic` nor `gen-java`, which the justfile runs separately (linkml issue 2537) | Nothing; the `gen-project` recipe already does |
| 1.11.1 | `linkml-run-examples` | Warns "No counter examples found" once per input format that has no files, even when the other format has them | Nothing; the warning is noise |
| 1.3+ | any | `reachable_from` (dynamic enums) is not resolved at validation time | Materialise first with `vskit expand -s schema.yaml -o schema_expanded.yaml` |
| 1.10 | any | `instantiates:` is not enforced by `linkml-validate` | Treat it as documentation |
| 1.8+ | `gen-pydantic` | Arrays (`array:` on a slot) are supported by the Pydantic generator; other generators lag | Check the generator before relying on array shapes |
