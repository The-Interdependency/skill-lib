from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from tools.skill_usage import (
    atomic_write,
    effective_designation,
    empty_state,
    load_state,
    parser,
    record_use,
    resolve_critical,
)


class SkillUsageTest(unittest.TestCase):
    def test_exposure_thresholds_and_quality_caps_are_distinct(self) -> None:
        state = empty_state()
        for _ in range(100):
            record_use(state, "canon", "hmmm", False)
        record = state["skills"]["canon"]
        self.assertEqual("field-test", effective_designation(record))

        for _ in range(5):
            record_use(state, "canon", "success", False)
        self.assertEqual("daily-use", effective_designation(record))

    def test_critical_failure_caps_and_resolution_restores_maturity(self) -> None:
        state = empty_state()
        for _ in range(100):
            record_use(state, "canon", "success", False)
        record_use(state, "canon", "failed", True)
        self.assertEqual("field-test", effective_designation(state["skills"]["canon"]))

        resolve_critical(state, "canon")
        self.assertEqual("daily-use", effective_designation(state["skills"]["canon"]))

    def test_state_round_trip_is_atomic_and_schema_checked(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "usage.json"
            state = empty_state()
            record_use(state, "canon", "success", False)
            atomic_write(path, state)
            self.assertEqual(state, load_state(path))

    def test_state_option_works_before_or_after_subcommand(self) -> None:
        path = Path("/tmp/skill-lib-usage-test.json")
        before = parser().parse_args(["--state", str(path), "record", "canon"])
        after = parser().parse_args(["record", "canon", "--state", str(path)])
        self.assertEqual(path, before.state)
        self.assertEqual(path, after.state)


if __name__ == "__main__":
    unittest.main()
