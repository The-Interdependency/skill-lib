# ratios: loc_comments=57:1 imports_exports=8:1 calls_definitions=34:4
"""Check source-to-package support inventory, access scope and immutable retrieval."""

from hashlib import sha256
import json
from pathlib import Path
from shutil import copyfile
from tempfile import TemporaryDirectory
import unittest

from skill_lib.mcp_assets import MANIFEST, SkillAssets, source_assets
from skill_lib.mcp_catalog import CatalogError, SkillCatalog

ROOT = Path(__file__).resolve().parents[1]
NAME = "msdmd"
DOC = "references/metadata-conventions.md"


class SkillSupportTests(unittest.TestCase):
    def test_catalog_and_every_packaged_resource_replay_exactly(self):
        data = json.loads((ROOT / "skills.json").read_bytes())
        names = {row["name"] for row in data["skills"]}
        manifest = json.loads(MANIFEST.read_bytes())
        self.assertEqual(source_assets(ROOT, names), manifest)
        store = SkillAssets(ROOT, SkillCatalog(ROOT))
        for name in manifest["skills"]:
            for item in store.list_files(name):
                with self.subTest(name=name, path=item["path"]):
                    raw = (ROOT / name / item["path"]).read_bytes()
                    self.assertEqual(sha256(raw).hexdigest(), item["sha256"])
                    self.assertEqual(store.read_file(name, item["path"])["text"].encode(), raw)
                    self.assertEqual(store.read_digest(name, item["sha256"]).encode(), raw)

    def test_unknown_assets_and_hidden_skills_are_unavailable(self):
        store = SkillAssets(ROOT, SkillCatalog(ROOT, allowed=[NAME]))
        for path in ("SKILL.md", "../skills.json", r"..\skills.json", "/tmp/test",
                     "code.py", "references/NewAmbientFile.md", "./" + DOC, "C:/file.md"):
            with self.subTest(path=path), self.assertRaises(CatalogError):
                store.read_file(NAME, path)
        for name in ("agent-ops", "../" + NAME, "fictional"):
            with self.assertRaises(CatalogError):
                store.list_files(name)
        with self.assertRaises(CatalogError):
            store.read_digest(NAME, "0" * 64)

    def test_worktree_drift_and_symlink_substitution_do_not_return_text(self):
        with TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            skill = root / NAME
            skill.mkdir()
            copyfile(ROOT / NAME / "SKILL.md", skill / "SKILL.md")
            data = json.loads((ROOT / "skills.json").read_bytes())
            data["skills"] = [row for row in data["skills"] if row["name"] == NAME]
            (root / "skills.json").write_text(json.dumps(data))
            file = skill / DOC
            file.parent.mkdir()
            file.write_text("unpublished local content")
            store = SkillAssets(root, SkillCatalog(root))
            with self.assertRaisesRegex(CatalogError, "revision"):
                store.read_file(NAME, DOC)
            file.unlink()
            file.symlink_to(ROOT / NAME / DOC)
            with self.assertRaisesRegex(CatalogError, "unavailable"):
                store.read_file(NAME, DOC)


if __name__ == "__main__":
    unittest.main()
# ratios: loc_comments=57:1 imports_exports=8:1 calls_definitions=34:4
