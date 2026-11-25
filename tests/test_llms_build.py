from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import contextlib
import io
import subprocess

from llms.build import collect, generate, main as llms_main, parse_text, resolve_repo_name


class LlmsBuildTest(unittest.TestCase):
    def test_parse_llms_block_allows_hyphenated_key_definitions(self) -> None:
        text = """# === LLMS ===
# id: key_definitions
#   msdmd: Module Self-Declared Metadata in Markdown
#   char-compress: Character-based context compression
#   llms-build: Root llms.txt generation
# === END LLMS ===
"""
        entries = parse_text(text, "#")

        self.assertEqual(1, len(entries))
        self.assertEqual("key_definitions", entries[0].id)
        self.assertEqual("Module Self-Declared Metadata in Markdown", entries[0].fields["msdmd"])
        self.assertEqual("Character-based context compression", entries[0].fields["char-compress"])
        self.assertEqual("Root llms.txt generation", entries[0].fields["llms-build"])

    def test_markdown_fenced_code_examples_are_ignored(self) -> None:
        text = """```markdown
# === LLMS ===
# id: project_overview
#   content: example only
# === END LLMS ===
```

# === LLMS ===
# id: project_overview
#   content: real declaration
# === END LLMS ===
"""
        entries = parse_text(text, "#", source=Path("README.md"))

        self.assertEqual(1, len(entries))
        self.assertEqual("real declaration", entries[0].fields["content"])

    def test_generate_uses_hmmm_for_missing_sections(self) -> None:
        generated = generate([], repo_name="demo")

        self.assertIn("# LLM Instructions for demo", generated)
        self.assertIn("## Project Overview\nhmmm", generated)
        self.assertIn("- **hmmm** = hmmm", generated)
        self.assertIn("## Architecture Summary\nhmmm", generated)
        self.assertIn("## How to Use This Repo with LLMs / Agents\nhmmm", generated)

    def test_native_only_input_retains_uncertainty_and_source_authority(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "AGENTS.md").write_text("Native instructions remain here.\n")
            entries = collect(root)
            generated = generate(entries, repo_name="native-only")

        self.assertEqual([], entries)
        self.assertIn("hmmm", generated)
        self.assertIn("Owning source declarations remain authoritative", generated)
        self.assertIn("omission here does not establish absence", generated)
        self.assertNotIn("single source of truth", generated)
        self.assertNotIn("does not exist in this repository", generated)

    def test_collect_and_generate_from_repo_tree(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "module.py").write_text(
                """# === LLMS ===
# id: project_overview
#   content: Demo repo.
# id: key_definitions
#   demo: exact definition
# id: architecture_summary
#   content: - One module.
# id: usage_rules
#   content: - Read source first.
# === END LLMS ===
""",
                encoding="utf-8",
            )

            generated = generate(collect(root), repo_name="demo")

        self.assertIn("Demo repo.", generated)
        self.assertIn("- **demo** = exact definition", generated)
        self.assertIn("- One module.", generated)
        self.assertIn("- Read source first.", generated)


    def test_resolve_repo_name_from_git_remote_when_dir_renamed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "arbitrary-clone-folder"
            root.mkdir()
            subprocess.run(["git", "init", str(root)], check=True, capture_output=True)
            subprocess.run(
                ["git", "-C", str(root), "remote", "add", "origin", "https://github.com/The-Interdependency/demo-repo.git"],
                check=True,
                capture_output=True,
            )
            (root / "module.py").write_text("# === LLMS ===\n# id: project_overview\n#   content: Demo.\n# === END LLMS ===\n")
            expected = generate(collect(root), repo_name="demo-repo")
            (root / "llms.txt").write_text(expected, encoding="utf-8")

            self.assertEqual("demo-repo", resolve_repo_name(root))
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(0, llms_main(["--root", str(root), "--out", "llms.txt", "--check"]))

    def test_resolve_repo_name_from_ssh_remote_and_skills_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "renamed-dir"
            root.mkdir()
            (root / "skills.json").write_text('{"repo": "The-Interdependency/my-lib"}\n', encoding="utf-8")
            self.assertEqual("my-lib", resolve_repo_name(root))

            ssh_root = Path(tmp) / "ssh-renamed-dir"
            ssh_root.mkdir()
            subprocess.run(["git", "init", str(ssh_root)], check=True, capture_output=True)
            subprocess.run(
                ["git", "-C", str(ssh_root), "remote", "add", "origin", "git@github.com:The-Interdependency/ssh-repo.git"],
                check=True,
                capture_output=True,
            )
            self.assertEqual("ssh-repo", resolve_repo_name(ssh_root))

    def test_subdir_inside_git_repo_does_not_inherit_parent_remote(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            parent = Path(tmp) / "parent-repo"
            parent.mkdir()
            subprocess.run(["git", "init", str(parent)], check=True, capture_output=True)
            subprocess.run(
                ["git", "-C", str(parent), "remote", "add", "origin", "https://github.com/The-Interdependency/parent-repo.git"],
                check=True,
                capture_output=True,
            )
            sub = parent / "nested-dir"
            sub.mkdir()
            self.assertEqual("nested-dir", resolve_repo_name(sub))
            self.assertEqual("override", resolve_repo_name(sub, repo="The-Interdependency/override"))

    def test_repo_llms_txt_matches_named_skill_lib_byte_for_byte(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        committed = (repo_root / "llms.txt").read_text(encoding="utf-8")
        generated = generate(collect(repo_root), repo_name=resolve_repo_name(repo_root))
        named = generate(collect(repo_root), repo_name="skill-lib")
        self.assertEqual(committed, named)
        self.assertEqual(named, generated)


if __name__ == "__main__":
    unittest.main()
