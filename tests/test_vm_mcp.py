"""Expose vm-mcp's self-contained unittest suites to skill-lib root CI discovery.

Usage guidance:
    python -m unittest discover -s tests

The canonical tests remain beside the skill under ``vm-mcp/tests``. This root
adapter only imports those TestCase classes so the existing repository CI gate
executes them without duplicating assertions.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VM_MCP = ROOT / "vm-mcp"
VM_MCP_TESTS = VM_MCP / "tests"
sys.path.insert(0, str(VM_MCP))
sys.path.insert(0, str(VM_MCP_TESTS))

from test_assets import VmMcpAssetTests  # noqa: E402,F401
from test_policy import VmMcpPolicyTests  # noqa: E402,F401
