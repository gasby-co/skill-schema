import json
import sys
from jsonschema import validate, ValidationError

if len(sys.argv) != 3:
    print("Usage: python validate_jsonld.py <data.json> <schema.json>")
    sys.exit(1)

with open(sys.argv[1]) as f:
    data = json.load(f)
with open(sys.argv[2]) as f:
    schema = json.load(f)

try:
    validate(instance=data, schema=schema)
    print("Validation successful!")
except ValidationError as e:
    print("Validation failed:")
    print(e)
    sys.exit(2) 