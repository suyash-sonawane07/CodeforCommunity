"""Export the FastAPI OpenAPI spec to docs/api/openapi/openapi.json.

Run: `make openapi-export` (from backend/: python scripts/export_openapi.py).
CI diffs this file to catch contract drift.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.main import app  # noqa: E402

OUT = Path(__file__).resolve().parents[2] / "docs" / "api" / "openapi" / "openapi.json"


def main() -> None:
    spec = app.openapi()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(spec, indent=2, sort_keys=False) + "\n")
    print(f"OpenAPI spec written to {OUT} ({len(spec.get('paths', {}))} paths)")


if __name__ == "__main__":
    main()
