# Usage Guide: Gasby Skill & Code Schema

## 1. Referencing Contexts in Your Data

To make your data self-describing and interoperable, always include the appropriate `@context` at the top of your JSON-LD files:

```json
{
  "@context": "../contexts/skill_profile_context.jsonld",
  ...
}
```

or for code classification:

```json
{
  "@context": "../contexts/code_classification_context.jsonld",
  ...
}
```

## 2. Validating Your Data

Use the JSON Schema files in `/schemas/` to validate your data for correctness. You can use tools like [ajv](https://ajv.js.org/), [jsonschema](https://python-jsonschema.readthedocs.io/en/stable/), or online validators.

Example (using Python):

```python
import json
import jsonschema

with open('examples/skill_profile_example.json') as f:
    data = json.load(f)
with open('schemas/skill_profile.schema.json') as f:
    schema = json.load(f)

jsonschema.validate(instance=data, schema=schema)
```

## 3. Using and Extending Vocabularies

- All enum-like fields (e.g., `type`, `scope`, `code_type`, `system_layer`) are defined in `/vocab/` as JSON-LD files.
- You may extend these vocabularies by adding new entries, but try to keep them MECE (mutually exclusive, collectively exhaustive).
- If you add new values, update both the vocab file and the corresponding JSON Schema if you want strict validation.

## 4. Example Data

See `/examples/` for sample JSON-LD files for both skill profiles and code classification.

## 5. Contributing

- Fork the repo and submit a pull request for changes to vocabularies, schemas, or documentation.
- For major changes, open an issue to discuss first.

## 6. Questions?

See `/docs/taxonomy.md` for definitions, or open an issue in the repo. 