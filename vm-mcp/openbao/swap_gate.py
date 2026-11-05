#!/usr/bin/env python3
# ratios: loc_comments=hmmm imports_exports=hmmm calls_definitions=hmmm
"""Usage: python3 -I swap_gate.py; refuses service startup with active swap."""
from pathlib import Path
import sys

if len(Path('/proc/swaps').read_text().splitlines()) != 1:
    print('OpenBao startup refused: active swap requires a reviewed memory policy.', file=sys.stderr)
    sys.exit(1)
# ratios: loc_comments=hmmm imports_exports=hmmm calls_definitions=hmmm
