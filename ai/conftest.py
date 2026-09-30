"""Pytest root configuration for ai test suite."""

import sys
from pathlib import Path

# Ensure repo root is on sys.path so `import ai` works whether invoked from repo root or ai/
_repo_root = Path(__file__).resolve().parent.parent
if str(_repo_root) not in sys.path:
    sys.path.insert(0, str(_repo_root))
