"""Keep the documented active-consumer list aligned with the drift workflow."""

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class ConsumerMatrixTests(unittest.TestCase):
    def test_ptcna_is_an_active_drift_consumer(self) -> None:
        distribution = (ROOT / "ORG_DISTRIBUTION.md").read_text(encoding="utf-8")
        active, excluded = distribution.split(
            "**Targets not in the drift matrix**",
            maxsplit=1,
        )
        self.assertIn("`The-Interdependency/ptcna`", active)
        self.assertNotIn("`The-Interdependency/ptcna`", excluded)

        workflow = (
            ROOT / ".github" / "workflows" / "consumer-drift.yml"
        ).read_text(encoding="utf-8")
        consumers = set(
            re.findall(r"^\s{10}- ([a-zA-Z0-9_-]+)$", workflow, re.MULTILINE)
        )
        self.assertIn("ptcna", consumers)


if __name__ == "__main__":
    unittest.main()
