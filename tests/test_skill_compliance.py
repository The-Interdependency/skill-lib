from __future__ import annotations

import unittest

from tools.check_skill_compliance import collect_findings


class SkillComplianceCheckerTest(unittest.TestCase):
    def test_no_baseline_skill_compliance_errors(self) -> None:
        errors = [finding for finding in collect_findings() if finding.level == "error"]
        self.assertEqual([], errors)


if __name__ == "__main__":
    unittest.main()
