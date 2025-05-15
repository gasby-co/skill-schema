# Gasby Skill Schema

A modern, open standard for representing developer skills and code classification, designed for interoperability, extensibility, and use with JSON-LD.

## Overview

This repository provides a comprehensive schema system for:
- **Developer Skill Profiling**: Structured representation of technical and soft skills with evidence and confidence metrics
- **Code Classification**: Systematic categorization of code by type and system layer
- **Repository Context**: Standardized profiles for project requirements and contribution prerequisites

The schema is built on JSON-LD for semantic interoperability and includes JSON Schema validation for data integrity.

## Features

- **Multi-Dimensional Skill Taxonomy**: Classifies skills by type (technical, cognitive, behavioral, contextual) and scope (general, specialized)
- **Comprehensive Code Classification**: Categories code by type (business logic, infrastructure, security, etc.) and system layer (frontend, backend, data, etc.)
- **Repository Profiling**: Captures tech stack, contribution prerequisites, and key skills for projects
- **JSON-LD Compatible**: Self-describing, machine-readable, and ready for linked data ecosystems
- **Extensible Vocabularies**: All enums and classifications are open for extension
- **Schema Validation**: JSON Schema files ensure data consistency and correctness
- **LLM Integration**: Purpose-built prompt templates for AI-powered skill extraction and analysis

## Schema Types

### 1. Skill Profile Schema
Represents individual or aggregate developer skills with:
- **name**: Skill identifier (e.g., "Terraform on AWS", "Critical thinking")
- **type**: technical | cognitive | behavioral | contextual
- **scope**: general | specialized
- **family**: Skill category grouping
- **frequency**: Quantified usage metric
- **unit**: Measurement unit for frequency
- **confidence**: Evidence strength (0-1)
- **evidence**: Supporting description

### 2. Code Classification Schema
Categorizes code files with:
- **code_type**: business_logic | application_glue | abstractions_frameworks | integration | infrastructure | testing_observability | documentation | scaffolding_setup | security
- **system_layer**: frontend | backend | infra | data | devops | shared
- **file_path**: Code location
- **evidence**: Classification rationale

### 3. Repository Profile Schema
Describes project context with:
- **description**: One-line project summary
- **tech_stack**: Technologies, languages, frameworks
- **contribution_prerequisites**: Setup and knowledge requirements
- **key_skills**: Critical technical areas with importance levels
- **domain_knowledge**: Specific expertise areas

## Quick Start

### 1. Create a Skill Profile
```json
{
  "@context": "contexts/skill_profile_context.jsonld",
  "skill_profile": [
    {
      "name": "React Development",
      "type": "technical",
      "scope": "specialized",
      "family": "Frontend",
      "frequency": 15,
      "unit": "components",
      "confidence": 0.85,
      "evidence": "Built 15 React components across 3 major features"
    }
  ]
}
```

### 2. Classify Code
```json
{
  "@context": "contexts/code_classification_context.jsonld",
  "code_classification": [
    {
      "code_type": "business_logic",
      "system_layer": "backend",
      "file_path": "src/api/user-service.js",
      "evidence": "Core user management business rules and validation"
    }
  ]
}
```

### 3. Validate Your Data
```bash
python scripts/validate_jsonld.py examples/skill_profile_example.json schemas/skill_profile.schema.json
```

## Project Structure

```
skill-schema/
├── contexts/           # JSON-LD context definitions
│   ├── skill_profile_context.jsonld
│   ├── code_classification_context.jsonld
│   └── repo_profile_context.jsonld
├── schemas/           # JSON Schema validation files
│   ├── skill_profile.schema.json
│   ├── code_classification.schema.json
│   └── repo_profile.schema.json
├── vocab/             # Extensible vocabulary definitions
│   ├── skill_type.jsonld
│   ├── skill_scope.jsonld
│   ├── code_type.jsonld
│   └── system_layer.jsonld
├── examples/          # Sample data files
├── docs/              # Documentation and taxonomy definitions
├── prompts/           # LLM prompt templates
└── scripts/           # Validation and utility scripts
```

## Usage Patterns

### For AI/LLM Applications
- Use prompt templates in `/prompts/` for consistent skill extraction
- Leverage JSON-LD contexts for semantic understanding
- Apply schemas for output validation and quality assurance

### For Developer Tools
- Import schemas for IDE validation and autocomplete
- Extend vocabularies for domain-specific classifications
- Use examples as templates for tool integration

### For Analytics and Insights
- Aggregate skill profiles for team capability mapping
- Track code classification trends across repositories
- Correlate repository profiles with contribution patterns

## Extending the Schema

### Adding New Skill Types
1. Update `/vocab/skill_type.jsonld` with new type definitions
2. Modify `/schemas/skill_profile.schema.json` enum constraints
3. Document new types in `/docs/taxonomy.md`

### Adding Code Classifications
1. Extend `/vocab/code_type.jsonld` or `/vocab/system_layer.jsonld`
2. Update corresponding schema enums
3. Provide examples in documentation

### Custom Vocabularies
All vocabularies are designed for extension. Maintain MECE (mutually exclusive, collectively exhaustive) principles when adding new categories.

## Validation and Quality

Run validation checks:
```bash
# Validate all examples
python scripts/validate_jsonld.py examples/skill_profile_example.json schemas/skill_profile.schema.json
python scripts/validate_jsonld.py examples/code_classification_example.json schemas/code_classification.schema.json
python scripts/validate_jsonld.py examples/repo_profile_example.json schemas/repo_profile.schema.json
```

## Contributing

1. **For vocabulary extensions**: Submit PRs with updated vocab files and corresponding schema changes
2. **For new schema types**: Open an issue to discuss design before implementation
3. **For documentation**: Ensure examples and taxonomy definitions stay current

### Development Setup
- Python 3.8+ (for validation scripts)
- Familiarity with JSON Schema and JSON-LD concepts
- Understanding of skill taxonomy and code classification principles

## Use Cases

- **Team Skill Assessment**: Profile developer capabilities with evidence-based metrics
- **Code Repository Analysis**: Automatically classify and understand codebase structure
- **Project Onboarding**: Define clear contribution requirements and skill expectations
- **AI-Powered Development**: Enable LLMs to understand and work with structured skill and code data
- **Analytics and Insights**: Aggregate data for team planning and project staffing decisions

## Documentation

- [`/docs/taxonomy.md`](docs/taxonomy.md) - Detailed definitions and classification guidelines
- [`/docs/usage.md`](docs/usage.md) - Comprehensive usage examples and integration patterns
- [`/examples/`](examples/) - Real-world sample data for each schema type

## License

[MIT](LICENSE)

## Support

For questions, feature requests, or bug reports:
- Review existing documentation in `/docs/`
- Check example files for usage patterns
- Open an issue for discussion or support 