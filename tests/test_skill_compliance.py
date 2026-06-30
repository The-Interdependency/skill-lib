from __future__ import annotations

import unittest

from tools.check_skill_compliance import collect_findings


class SkillComplianceCheckerTest(unittest.TestCase):
    def test_no_skill_compliance_findings(self) -> None:
        self.assertEqual([], collect_findings())


if __name__ == "__main__":
    unittest.main()
