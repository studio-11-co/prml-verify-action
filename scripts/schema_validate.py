"""Validate a PRML manifest YAML against the v0.1 / v0.2-RFC JSON Schema.

Invoked by `mode: schema-only` in the composite action. Fetches the schema
from the published URL (the same ones in the SchemaStore catalog) so the
validation is always against the current canonical version, no schema files
shipped in the action repo.

Usage:
    python schema_validate.py <schema_url> <manifest_path> <schema_label>

Exit codes:
    0   PASS — manifest validates
    10  FAIL — schema validation error
    2   IO / unexpected error
"""

from __future__ import annotations

import json
import sys
import urllib.error
import urllib.request


def main() -> int:
    if len(sys.argv) != 4:
        sys.stderr.write(
            "usage: schema_validate.py <schema_url> <manifest_path> <schema_label>\n"
        )
        return 2

    schema_url, manifest_path, schema_label = sys.argv[1], sys.argv[2], sys.argv[3]

    try:
        import yaml  # type: ignore[import-not-found]
        import jsonschema  # type: ignore[import-not-found]
    except ImportError as exc:
        sys.stderr.write(f"missing dependency: {exc}\n")
        return 2

    try:
        with urllib.request.urlopen(schema_url, timeout=30) as r:
            schema = json.loads(r.read())
    except (urllib.error.URLError, json.JSONDecodeError, OSError) as exc:
        sys.stderr.write(f"could not fetch schema from {schema_url}: {exc}\n")
        return 2

    try:
        with open(manifest_path, encoding="utf-8") as f:
            manifest = yaml.safe_load(f)
    except (OSError, yaml.YAMLError) as exc:
        sys.stderr.write(f"could not parse manifest {manifest_path}: {exc}\n")
        return 2

    try:
        jsonschema.validate(instance=manifest, schema=schema)
    except jsonschema.ValidationError as exc:
        print(f"FAIL - schema validation error against PRML {schema_label}")
        print(f"  at path: {list(exc.absolute_path)}")
        print(f"  message: {exc.message}")
        return 10

    print(f"PASS - manifest validates against PRML {schema_label}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
