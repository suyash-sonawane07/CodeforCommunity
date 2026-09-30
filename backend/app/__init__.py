"""CivicPulse backend package.

Modular monolith (ADR-001): api/routes → services → repositories → db.
"""

import sys
from pathlib import Path

# Ensure root (containing ai/ layer) is always on sys.path
_root_dir = str(Path(__file__).resolve().parents[2])
if _root_dir not in sys.path:
    sys.path.insert(0, _root_dir)
