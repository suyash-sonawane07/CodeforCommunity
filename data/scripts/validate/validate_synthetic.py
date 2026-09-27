#!/usr/bin/env python3
"""Validate data/synthetic/*.json against data/schemas/*.json (FR-039).

- Schema check (draft-07) + range checks.
- Invalid rows are written to quarantine/, never silently dropped.
- Exit code 1 if anything invalid → CI/`make validate-data` fails loudly.

Stdlib-only (no jsonschema dependency) so it runs anywhere: implements the
subset of draft-07 the schemas use (type/required/enum/pattern/const/min/max).
Run: `make validate-data` or `python3 data/scripts/validate/validate_synthetic.py`.
"""

from __future__ import annotations

import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parents[2]
SYNTH_DIR = DATA_DIR / "synthetic"
SCHEMA_DIR = DATA_DIR / "schemas"
QUARANTINE_DIR = SYNTH_DIR / "_quarantine"

DATASETS = {
    "requests/requests_v0.1.json": "request.schema.json",
    "demographics/demographics_v0.1.json": "demographic_indicator.schema.json",
    "infrastructure/infrastructure_v0.1.json": "infrastructure_asset.schema.json",
    "projects/projects_v0.1.json": "project.schema.json",
}

TYPE_MAP = {
    "object": dict,
    "array": list,
    "string": str,
    "integer": int,
    "number": (int, float),
    "boolean": bool,
    "null": type(None),
}


def check(value, schema, path="$"):
    """Yield human-readable errors for the draft-07 features our schemas use."""
    errors: list[str] = []
    expected = schema.get("type")
    if expected:
        options = expected if isinstance(expected, list) else [expected]
        py_types = [TYPE_MAP[o] for o in options]
        # bool is an int subclass — guard the integer/number case
        ok = any(isinstance(value, t) and not (t in (int, float) and isinstance(value, bool)) for t in py_types)
        if not ok:
            return [f"{path}: expected type {expected}, got {type(value).__name__}"]
    if "const" in schema and value != schema["const"]:
        errors.append(f"{path}: must equal {schema['const']!r}")
    if "enum" in schema and value not in schema["enum"]:
        errors.append(f"{path}: {value!r} not in {schema['enum']}")
    if isinstance(value, str):
        if "pattern" in schema and not re.search(schema["pattern"], value):
            errors.append(f"{path}: {value!r} fails pattern {schema['pattern']}")
        if "minLength" in schema and len(value) < schema["minLength"]:
            errors.append(f"{path}: shorter than {schema['minLength']}")
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        if "minimum" in schema and value < schema["minimum"]:
            errors.append(f"{path}: {value} < minimum {schema['minimum']}")
        if "maximum" in schema and value > schema["maximum"]:
            errors.append(f"{path}: {value} > maximum {schema['maximum']}")
    if isinstance(value, dict):
        for req in schema.get("required", []):
            if req not in value:
                errors.append(f"{path}: missing required property {req!r}")
        for key, sub in schema.get("properties", {}).items():
            if key in value:
                errors.extend(check(value[key], sub, f"{path}.{key}"))
    if isinstance(value, list) and "items" in schema:
        for i, item in enumerate(value):
            errors.extend(check(item, schema["items"], f"{path}[{i}]"))
    return errors


def validate_file(rel: str, schema_name: str) -> tuple[int, int, list[str]]:
    """Returns (rows_ok, rows_invalid, problem_descriptions)."""
    fpath = SYNTH_DIR / rel
    schema = json.loads((SCHEMA_DIR / schema_name).read_text())
    envelope = json.loads(fpath.read_text())

    problems: list[str] = []
    manifest = json.loads((SCHEMA_DIR / "dataset_manifest.schema.json").read_text())
    for err in check(envelope, {k: v for k, v in manifest.items() if k != "$id"}):
        problems.append(f"[{rel} envelope] {err}")
    if envelope.get("synthetic") is not True:
        problems.append(f"[{rel}] dataset is not labelled synthetic=true (FR-057)")

    ok = invalid = 0
    for i, row in enumerate(envelope.get("rows", [])):
        errs = check(row, schema, f"{rel}.rows[{i}]")
        if errs:
            invalid += 1
            problems.extend(errs)
        else:
            ok += 1
    return ok, invalid, problems


def quarantine(rel: str, problems: list[str]) -> Path | None:
    """Copy the offending file + error report into quarantine (FR-039)."""
    if not problems:
        return None
    QUARANTINE_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    src = SYNTH_DIR / rel
    dest = QUARANTINE_DIR / f"{stamp}_{Path(rel).name}"
    if src.exists():
        dest.write_text(src.read_text())
    (QUARANTINE_DIR / f"{stamp}_{Path(rel).stem}.errors.json").write_text(
        json.dumps(problems, indent=2)
    )
    return dest


def main() -> int:
    total_ok = total_bad = 0
    any_problems: list[str] = []
    for rel, schema_name in DATASETS.items():
        ok, invalid, problems = validate_file(rel, schema_name)
        total_ok += ok
        total_bad += invalid
        status = "OK" if not problems else "INVALID"
        print(f"{status:>8}  {rel}: {ok} valid, {invalid} invalid")
        if problems:
            any_problems.extend(problems)
            q = quarantine(rel, problems)
            print(f"          quarantined → {q}")

    print(f"\nSummary: {total_ok} valid rows, {total_bad} invalid rows")
    if any_problems:
        print("FAILED — fix the rows above (they were quarantined, not dropped).")
        return 1
    print("All synthetic datasets valid. (All data remains SYNTHETIC — FR-057.)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
