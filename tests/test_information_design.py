import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUDIT_PATH = ROOT / "data-visualization" / "information_design_audit.py"
EXAMPLE_PATH = ROOT / "data-visualization" / "examples" / "information-design-manifest.json"

spec = importlib.util.spec_from_file_location("information_design_audit", AUDIT_PATH)
audit = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(audit)


class InformationDesignAuditTests(unittest.TestCase):
    def test_example_manifest_passes(self):
        manifest = json.loads(EXAMPLE_PATH.read_text(encoding="utf-8"))
        report = audit.audit_manifest(manifest)
        self.assertEqual(report["status"], "pass")
        self.assertEqual(report["errors"], [])

    def test_color_only_state_fails(self):
        manifest = {
            "message": "state distinction",
            "semantic_dimensions": {"state": "hue"},
            "text_pairs": [],
            "nontext_pairs": [],
            "states": [{"name": "bad", "color": "#D55E00", "redundancy": ["color"]}],
            "manual_gates": {"grayscale": "hmmm", "cvd": "hmmm", "semantic": "hmmm"},
        }
        report = audit.audit_manifest(manifest)
        self.assertEqual(report["status"], "fail")
        self.assertIn("color_only_state", {item["code"] for item in report["errors"]})

    def test_hue_cannot_encode_two_independent_dimensions(self):
        manifest = {
            "message": "overloaded hue",
            "semantic_dimensions": {"component": "hue", "status": "hue"},
            "text_pairs": [],
            "nontext_pairs": [],
            "states": [],
            "manual_gates": {"grayscale": "hmmm", "cvd": "hmmm", "semantic": "hmmm"},
        }
        report = audit.audit_manifest(manifest)
        self.assertEqual(report["status"], "fail")
        self.assertIn("hue_overloaded", {item["code"] for item in report["errors"]})

    def test_low_contrast_text_fails(self):
        manifest = {
            "message": "contrast gate",
            "semantic_dimensions": {"component": "shape"},
            "text_pairs": [{"foreground": "#F0E442", "background": "#FFFFFF", "size": "normal"}],
            "nontext_pairs": [],
            "states": [],
            "manual_gates": {"grayscale": "hmmm", "cvd": "hmmm", "semantic": "hmmm"},
        }
        report = audit.audit_manifest(manifest)
        self.assertEqual(report["status"], "fail")
        self.assertIn("text_contrast", {item["code"] for item in report["errors"]})


if __name__ == "__main__":
    unittest.main()
