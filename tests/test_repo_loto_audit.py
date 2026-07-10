from __future__ import annotations

import contextlib
import importlib.util
import io
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPO_LOTO_TEST = ROOT / "tests" / "test_repo_loto.py"


def sentinel() -> None:
    pass


def extra() -> None:
    pass


def _load_repo_loto_test_module():
    spec = importlib.util.spec_from_file_location("repo_loto_audit_subject", REPO_LOTO_TEST)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load test_repo_loto.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _write_contracts(path: Path, contract_ids: list[str]) -> None:
    lines = ["# === CONTRACTS ==="]
    for cid in contract_ids:
        lines.extend([
            f"# id: {cid}",
            "#   given: planted audit fixture",
            "#   then: planted audit result",
            "#   class: audit_fixture",
            "#",
        ])
    lines.append("# === END CONTRACTS ===")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_checks(path: Path, checks: list[dict[str, str]]) -> None:
    lines = ["# === CHECKS ==="]
    for check in checks:
        lines.append(f"# id: {check['id']}")
        for key, value in check.items():
            if key == "id":
                continue
            lines.append(f"#   {key}: {value}")
        lines.append("#")
    lines.append("# === END CHECKS ===")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


class RepoLotoAuditNegativeTest(unittest.TestCase):
    def run_planted_audit(
        self,
        *,
        contract_ids: list[str],
        checks: list[dict[str, str]],
        check_fns: list[object],
    ) -> tuple[int, str]:
        module = _load_repo_loto_test_module()
        module.sentinel = sentinel
        module.extra = extra
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "repo_loto.py"
            evidence = root / "test_repo_loto.py"
            _write_contracts(source, contract_ids)
            _write_checks(evidence, checks)

            old_loto = module.LOTO
            old_file = module.__file__
            old_check_fns = module.CHECK_FNS
            try:
                module.LOTO = str(source)
                module.__file__ = str(evidence)
                module.CHECK_FNS = check_fns
                buf = io.StringIO()
                with contextlib.redirect_stdout(buf):
                    code = module.audit()
                return code, buf.getvalue()
            finally:
                module.LOTO = old_loto
                module.__file__ = old_file
                module.CHECK_FNS = old_check_fns

    def test_audit_gaps_orphan_contract(self) -> None:
        code, out = self.run_planted_audit(
            contract_ids=["covered_contract", "orphan_contract"],
            checks=[{"id": "check_covered", "proves": "covered_contract", "call": "self::sentinel"}],
            check_fns=[sentinel],
        )

        self.assertEqual(1, code)
        self.assertIn("GAP  orphan_contract  has no CHECKS entry claiming to prove it", out)

    def test_audit_gaps_phantom_proves_target(self) -> None:
        code, out = self.run_planted_audit(
            contract_ids=["real_contract"],
            checks=[{"id": "check_phantom", "proves": "missing_contract", "call": "self::sentinel"}],
            check_fns=[sentinel],
        )

        self.assertEqual(1, code)
        self.assertIn("GAP  check_phantom claims unknown contract: missing_contract", out)

    def test_audit_splits_multi_target_proves(self) -> None:
        code, out = self.run_planted_audit(
            contract_ids=["first_contract", "second_contract"],
            checks=[{"id": "check_both", "proves": "first_contract, second_contract", "call": "self::sentinel"}],
            check_fns=[sentinel],
        )

        self.assertEqual(0, code)
        self.assertIn("OK   first_contract  <-  check_both", out)
        self.assertIn("OK   second_contract  <-  check_both", out)
        self.assertIn("graph closed", out)

    def test_audit_gaps_unresolvable_call(self) -> None:
        code, out = self.run_planted_audit(
            contract_ids=["real_contract"],
            checks=[{"id": "check_absent", "proves": "real_contract", "call": "self::absent"}],
            check_fns=[sentinel],
        )

        self.assertEqual(1, code)
        self.assertIn("GAP  check_absent call does not resolve: not callable: self::absent", out)

    def test_audit_gaps_executable_check_without_declaration(self) -> None:
        code, out = self.run_planted_audit(
            contract_ids=["real_contract"],
            checks=[{"id": "check_real", "proves": "real_contract", "call": "self::sentinel"}],
            check_fns=[sentinel, extra],
        )

        self.assertEqual(1, code)
        self.assertIn("GAP  executable check extra has no resolving CHECKS declaration", out)

    def test_audit_refuses_dotted_import_resolution(self) -> None:
        code, out = self.run_planted_audit(
            contract_ids=["real_contract"],
            checks=[{"id": "check_import", "proves": "real_contract", "call": "pkg.mod.fn"}],
            check_fns=[sentinel],
        )

        self.assertEqual(1, code)
        self.assertIn("only self::fn resolves without execution: pkg.mod.fn", out)


if __name__ == "__main__":
    unittest.main()
