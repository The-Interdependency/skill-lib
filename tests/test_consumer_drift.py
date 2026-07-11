from __future__ import annotations

import hashlib
import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location(
    "check_consumer_drift", ROOT / "tools" / "check_consumer_drift.py"
)
ccd = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = ccd  # dataclass introspection needs the module registered
_spec.loader.exec_module(ccd)


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


class ConsumerDriftTest(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        base = Path(self._tmp.name)
        self.canon = base / "canon"
        self.consumer = base / "consumer"
        # canonical skill with a SKILL.md and a helper file
        _write(self.canon / "msdmd" / "SKILL.md", "canonical spec\n")
        _write(self.canon / "msdmd" / "parsers" / "universal.py", "print('x')\n")
        # a second canonical skill the consumer does NOT vendor
        _write(self.canon / "doc-build" / "SKILL.md", "docs\n")
        # consumer vendors msdmd verbatim
        _write(self.consumer / ".agents/skills" / "msdmd" / "SKILL.md", "canonical spec\n")
        _write(
            self.consumer / ".agents/skills" / "msdmd" / "parsers" / "universal.py",
            "print('x')\n",
        )

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def _report(self, **kw):
        return ccd.check_consumer(self.consumer, canon_root=self.canon, **kw)

    def test_verbatim_copy_is_clean(self) -> None:
        report = self._report()
        self.assertEqual([s.name for s in report.skills], ["msdmd"])
        self.assertTrue(all(s.ok for s in report.skills))

    def test_only_vendored_intersection_is_checked(self) -> None:
        # doc-build exists canonically but is not vendored -> not reported
        report = self._report()
        self.assertNotIn("doc-build", [s.name for s in report.skills])

    def test_differing_file_is_drift(self) -> None:
        _write(self.consumer / ".agents/skills" / "msdmd" / "SKILL.md", "tampered\n")
        report = self._report()
        msdmd = next(s for s in report.skills if s.name == "msdmd")
        self.assertFalse(msdmd.ok)
        self.assertTrue(any("differs: SKILL.md" in r for r in msdmd.drift))

    def test_missing_canonical_file_is_drift(self) -> None:
        (self.consumer / ".agents/skills" / "msdmd" / "parsers" / "universal.py").unlink()
        report = self._report()
        msdmd = next(s for s in report.skills if s.name == "msdmd")
        self.assertTrue(any("missing:" in r for r in msdmd.drift))

    def test_local_addition_is_ignored(self) -> None:
        # a repo-local extra file must not count as drift
        _write(self.consumer / ".agents/skills" / "msdmd" / "runner.py", "local\n")
        report = self._report()
        self.assertTrue(all(s.ok for s in report.skills))

    def test_local_only_skill_is_ignored(self) -> None:
        _write(self.consumer / ".agents/skills" / "repo-local" / "SKILL.md", "local\n")
        report = self._report()
        self.assertNotIn("repo-local", [s.name for s in report.skills])

    def test_manifest_pin_stale_is_drift(self) -> None:
        _write(self.canon / "manifest" / "SKILL.md", "m\n")
        _write(self.canon / "manifest" / "generate.py", "GEN\n")
        _write(self.consumer / ".agents/skills" / "manifest" / "SKILL.md", "m\n")
        _write(self.consumer / ".agents/skills" / "manifest" / "generate.py", "GEN\n")
        _write(
            self.consumer / ".agents/skills" / "manifest" / "generate.py.sha256",
            "deadbeef  generate.py\n",
        )
        report = self._report()
        manifest = next(s for s in report.skills if s.name == "manifest")
        self.assertTrue(any("stale pin" in r for r in manifest.drift))

    def _manifest_with_pin(self, pin_text: str) -> None:
        _write(self.canon / "manifest" / "SKILL.md", "m\n")
        _write(self.canon / "manifest" / "generate.py", "GEN\n")
        _write(self.consumer / ".agents/skills" / "manifest" / "SKILL.md", "m\n")
        _write(self.consumer / ".agents/skills" / "manifest" / "generate.py", "GEN\n")
        _write(self.consumer / ".agents/skills" / "manifest" / "generate.py.sha256", pin_text)

    def test_manifest_pin_wrong_filename_is_drift(self) -> None:
        digest = hashlib.sha256(b"GEN\n").hexdigest()
        self._manifest_with_pin(f"{digest}  wrong.py\n")  # correct digest, wrong name
        report = self._report()
        manifest = next(s for s in report.skills if s.name == "manifest")
        self.assertTrue(any("malformed pin" in r for r in manifest.drift))

    def test_manifest_pin_extra_line_is_drift(self) -> None:
        digest = hashlib.sha256(b"GEN\n").hexdigest()
        self._manifest_with_pin(f"{digest}  generate.py\n{digest}  other.py\n")
        report = self._report()
        manifest = next(s for s in report.skills if s.name == "manifest")
        self.assertTrue(any("malformed pin" in r for r in manifest.drift))

    def test_manifest_pin_binary_marker_is_clean(self) -> None:
        digest = hashlib.sha256(b"GEN\n").hexdigest()
        self._manifest_with_pin(f"{digest} *generate.py\n")  # sha256sum binary mode
        report = self._report()
        manifest = next(s for s in report.skills if s.name == "manifest")
        self.assertTrue(manifest.ok)

    def test_manifest_pin_current_is_clean(self) -> None:
        _write(self.canon / "manifest" / "SKILL.md", "m\n")
        _write(self.canon / "manifest" / "generate.py", "GEN\n")
        _write(self.consumer / ".agents/skills" / "manifest" / "SKILL.md", "m\n")
        _write(self.consumer / ".agents/skills" / "manifest" / "generate.py", "GEN\n")
        digest = hashlib.sha256(b"GEN\n").hexdigest()
        _write(
            self.consumer / ".agents/skills" / "manifest" / "generate.py.sha256",
            f"{digest}  generate.py\n",
        )
        report = self._report()
        manifest = next(s for s in report.skills if s.name == "manifest")
        self.assertTrue(manifest.ok)

    def test_sha_citation_warning(self) -> None:
        report = self._report(sha="abc1234")
        self.assertIsNotNone(report.sha_warning)
        _write(
            self.consumer / ".agents/skills" / "README.md",
            "Source commit: `skill-lib` @ `abc1234`\n",
        )
        report = self._report(sha="abc1234")
        self.assertIsNone(report.sha_warning)

    def test_no_skills_dir_reports_nothing_vendored(self) -> None:
        empty = Path(self._tmp.name) / "empty"
        empty.mkdir()
        report = ccd.check_consumer(empty, canon_root=self.canon)
        self.assertEqual(report.skills, [])
        self.assertIn("nothing vendored", report.sha_warning or "")

    def test_require_vendored_empty_fails(self) -> None:
        empty = Path(self._tmp.name) / "empty2"
        empty.mkdir()
        report = ccd.check_consumer(empty, canon_root=self.canon)
        _text, failed = ccd.format_report(report, strict_sha=False, require_vendored=True)
        self.assertTrue(failed)

    def test_require_vendored_with_subset_is_clean(self) -> None:
        report = self._report()  # vendors msdmd
        _text, failed = ccd.format_report(report, strict_sha=False, require_vendored=True)
        self.assertFalse(failed)

    def test_no_require_vendored_empty_is_clean(self) -> None:
        empty = Path(self._tmp.name) / "empty3"
        empty.mkdir()
        report = ccd.check_consumer(empty, canon_root=self.canon)
        _text, failed = ccd.format_report(report, strict_sha=False, require_vendored=False)
        self.assertFalse(failed)

    def test_format_and_exit_code(self) -> None:
        _write(self.consumer / ".agents/skills" / "msdmd" / "SKILL.md", "tampered\n")
        report = self._report()
        _text, failed = ccd.format_report(report, strict_sha=False)
        self.assertTrue(failed)


if __name__ == "__main__":
    unittest.main()
