# ratios: loc_comments=103:1 imports_exports=6:1 calls_definitions=59:10
"""Exercise the canonical skill catalog in memory, including incomplete declarations."""

import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from skill_lib.mcp_catalog import CatalogError, SkillCatalog


class CatalogTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.rows = {}
        for name in ("root", "left", "right", "base"):
            (self.root / name).mkdir()
            (self.root / name / "SKILL.md").write_bytes(f"# {name}\r\nExact ü\n".encode())
            self.rows[name] = {"name": name, "path": name + "/SKILL.md",
                               "description": "Discover " + name}
        self.rows["root"]["depends_on"] = ["left", "right"]
        self.rows["root"]["load_with"] = ["base"]
        self.rows["left"]["depends_on"] = ["base"]
        self.rows["right"]["depends_on"] = ["base"]
        self.write()

    def write(self):
        index = {"repo": "The-Interdependency/skill-lib", "version": 1,
                 "superseded_skills": [{"name": "old"}], "skills": list(self.rows.values())}
        (self.root / "skills.json").write_text(json.dumps(index), encoding="utf-8")

    def test_discovery_and_activation_are_exact(self):
        catalog = SkillCatalog(self.root)
        self.assertEqual([row["name"] for row in catalog.discover()], ["base", "left", "right", "root"])
        self.assertTrue(all("instructions" not in row for row in catalog.discover()))
        plan = catalog.activate(["root", "root"])
        self.assertEqual(plan["roots"], ["root"])
        rows = plan["skills"]
        self.assertEqual([s["name"] for s in rows], ["base", "left", "right", "root"])
        self.assertEqual(rows[0]["reasons"], [{"kind": "depends_on", "source": "left"},
                                              {"kind": "depends_on", "source": "right"},
                                              {"kind": "load_with", "source": "root"}])
        expected = (self.root / "base/SKILL.md").read_bytes()
        self.assertEqual(rows[0]["instructions"].encode(), expected)
        self.assertEqual(rows[0]["sha256"], hashlib.sha256(expected).hexdigest())
        self.assertEqual([s["name"] for s in catalog.activate(["base"])["skills"]], ["base"])

    def test_receipts_and_disclosure_are_snapshot_bound(self):
        first = SkillCatalog(self.root)
        bodies = {s["name"]: s["sha256"] for s in first.activate(["root"])["skills"]}
        changed = self.root / "base/SKILL.md"
        changed.write_bytes(b"new revision")
        self.assertNotEqual(first.read("base")["instructions"], "new revision")
        self.assertTrue(all("instructions_retained" in s and "instructions" not in s
                            for s in first.activate(["root"], bodies)["skills"]))
        second = SkillCatalog(self.root)
        self.assertNotEqual(first.catalog_sha256, second.catalog_sha256)
        revised = second.activate(["root"], bodies)["skills"]
        self.assertEqual([s["name"] for s in revised if "instructions" in s], ["base"])
        self.assertEqual(revised[0]["instructions"], "new revision")
        self.assertTrue(all("instructions" in s for s in second.activate(["root"])["skills"]))

    def test_scope_refuses_incomplete_closure_without_hidden_identity(self):
        catalog = SkillCatalog(self.root, allowed=["root"])
        self.assertEqual([s["name"] for s in catalog.discover()], ["root"])
        for name in ("left", "old", "../left/SKILL.md"):
            with self.subTest(name=name), self.assertRaises(CatalogError):
                catalog.read(name)
        with self.assertRaisesRegex(CatalogError, "^a required skill is unavailable in this catalog scope$"):
            catalog.activate(["root"])
        with self.assertRaises(CatalogError):
            SkillCatalog(self.root, allowed=["unknown"])

    def test_invalid_relations_and_paths_refuse(self):
        cases = [("load_with", "left"), ("depends_on", ["old"]), ("depends_on", ["missing"]),
                 ("load_with", ["root"]), ("depends_on", ["left", "left"]),
                 ("path", "../left/SKILL.md")]
        clean = self.rows["root"].copy()
        for key, value in cases:
            self.rows["root"] = {**clean, key: value}
            self.write()
            with self.subTest(value=value), self.assertRaises(CatalogError):
                SkillCatalog(self.root)
        self.rows["root"] = clean
        self.rows["base"]["depends_on"] = ["root"]
        self.write()
        with self.assertRaisesRegex(CatalogError, "cycle"):
            SkillCatalog(self.root)

    def test_co_load_cycle_is_one_activation(self):
        self.rows["left"] = {**self.rows["left"], "load_with": ["right"]}
        self.rows["right"] = {**self.rows["right"], "load_with": ["left"]}
        self.write()
        activated = SkillCatalog(self.root).activate(["left"])["skills"]
        self.assertEqual([r["name"] for r in activated], ["base", "left", "right"])

    def test_symlink_and_duplicate_field_refuse(self):
        target = self.root / "base/SKILL.md"
        target.unlink()
        target.symlink_to(self.root / "left/SKILL.md")
        with self.assertRaises(CatalogError):
            SkillCatalog(self.root)
        (self.root / "skills.json").write_text('{"skills":[],"skills":[]}')
        with self.assertRaisesRegex(CatalogError, "duplicate"):
            SkillCatalog(self.root)

    def test_malformed_activation_inputs_refuse(self):
        catalog = SkillCatalog(self.root)
        for roots, retained in (("root", None), ([], None), (["old"], None),
                                (["root"], {"base": "bad"}), (["root"], [])):
            with self.subTest(roots=roots, retained=retained), self.assertRaises(CatalogError):
                catalog.activate(roots, retained)


if __name__ == "__main__":
    unittest.main()
# ratios: loc_comments=103:1 imports_exports=6:1 calls_definitions=59:10
