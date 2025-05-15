# Gasby Skill Schema

A modern, open standard for representing developer skills and code classification, designed for interoperability, extensibility, and use with JSON-LD.

## Features

- **Skill Taxonomy:** Classifies skills by type (technical, cognitive, behavioral, contextual) and scope (general, specialized)
- **Code Classification:** Classifies code by type (business logic, infra, security, etc.) and system layer (frontend, backend, etc.)
- **JSON-LD Compatible:** Self-describing, machine-readable, and ready for linked data
- **Extensible Vocabularies:** All enums and types are open for extension
- **Validation:** JSON Schema files for data validation
- **Prompt Templates:** LLM prompt templates for extraction and synthesis

## Quickstart

1. **Reference the context in your JSON-LD:**
   ```json
   {
     "@context": "contexts/skill_profile_context.jsonld",
     ...
   }
   ```

2. **Validate your data:**
   ```bash
   python scripts/validate_jsonld.py examples/skill_profile_example.json schemas/skill_profile.schema.json
   ```

3. **See `/docs/usage.md` for more details.**

## Directory Structure

- `contexts/` — JSON-LD context files
- `vocab/` — Enum vocabularies (types, layers, etc.)
- `schemas/` — JSON Schema for validation
- `examples/` — Example data files
- `docs/` — Taxonomy and usage documentation
- `prompts/` — LLM prompt templates
- `scripts/` — Validation and tooling scripts

## Extending the Schema

- Add new types or layers to the vocab files in `/vocab/`
- Update the corresponding JSON Schema in `/schemas/` if you want strict validation
- See `/docs/taxonomy.md` for definitions

## Contributing

- Fork the repo and submit a pull request
- For major changes, open an issue to discuss first

## License

[MIT](LICENSE)

## Questions?

See `/docs/usage.md` and `/docs/taxonomy.md`, or open an issue. 