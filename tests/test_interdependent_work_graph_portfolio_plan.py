import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "interdependent-work-graph" / "portfolio_plan.py"
SPEC = importlib.util.spec_from_file_location("portfolio_plan", MODULE_PATH)
portfolio_plan = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(portfolio_plan)


def report(repository: str, commit: str, relation_to: str | None = None):
    relations = []
    if relation_to:
        relations.append({
            "repository": relation_to,
            "relation": "declared test dependency",
            "authority_transfer": False,
        })
    return {
        "schema": "the-interdependency.repository-plan-report",
        "version": "1.0.0",
        "repository": repository,
        "contract": {
            "repository": "The-Interdependency/skill-lib",
            "path": "interdependent-work-graph/repository-plan-report.schema.json",
            "version": "1.0.0",
            "blob_sha": portfolio_plan.CONTRACT_BLOB_SHA,
        },
        "source": {
            "branch": "main",
            "commit": commit,
            "generated_at": "2026-08-07",
            "note": "test fixture",
        },
        "authority": {
            "owns": ["its own test authority"],
            "does_not_own": ["another repository's authority"],
            "non_transfer": ["authority does not transfer"],
        },
        "portfolio_role": {
            "summary": "test portfolio role",
            "reports_to": {
                "repository": "The-Interdependency/skill-lib",
                "skill": "interdependent-work-graph",
                "relation": "repo-owned plan/status input",
            },
        },
        "status": {"state": "test", "current_claim": "bounded test claim"},
        "delivered": [{"surface": "fixture", "status": "delivered", "boundary": "test only"}],
        "active_frontier": ["one frontier"],
        "next_actions": [{"action": "one action", "owner": repository, "dependency": "none"}],
        "blocked": [],
        "cross_repository_relations": relations,
        "machine_entrypoints": {"repo_report": "docs/work-graphs/repository-plan-report.json"},
        "hmmm": ["one unresolved boundary"],
    }


class PortfolioPlanTests(unittest.TestCase):
    def test_projection_is_order_independent_and_hashed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            a = root / "z.json"
            b = root / "a.json"
            a.write_text(json.dumps(report("The-Interdependency/z", "a" * 40)), encoding="utf-8")
            b.write_text(json.dumps(report("The-Interdependency/a", "b" * 40, "The-Interdependency/z")), encoding="utf-8")

            first = portfolio_plan.build_portfolio([(a, portfolio_plan.load_report(a)), (b, portfolio_plan.load_report(b))])
            second = portfolio_plan.build_portfolio([(b, portfolio_plan.load_report(b)), (a, portfolio_plan.load_report(a))])

            self.assertEqual(first, second)
            self.assertEqual(
                [entry["repository"] for entry in first["repositories"]],
                ["The-Interdependency/a", "The-Interdependency/z"],
            )
            digest = first.pop("portfolio_plan_sha256")
            self.assertEqual(digest, portfolio_plan.digest(first))

    def test_authority_transfer_is_rejected(self):
        bad = report("The-Interdependency/a", "c" * 40, "The-Interdependency/z")
        bad["cross_repository_relations"][0]["authority_transfer"] = True
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "bad.json"
            path.write_text(json.dumps(bad), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "authority transfer must be false"):
                portfolio_plan.load_report(path)

    def test_wrong_contract_blob_is_rejected(self):
        bad = report("The-Interdependency/a", "c" * 40)
        bad["contract"]["blob_sha"] = "0" * 40
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "bad-contract.json"
            path.write_text(json.dumps(bad), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "frozen contract blob"):
                portfolio_plan.load_report(path)

    def test_duplicate_repository_reports_are_rejected(self):
        one = report("The-Interdependency/a", "d" * 40)
        two = report("The-Interdependency/a", "e" * 40)
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            p1 = root / "1.json"
            p2 = root / "2.json"
            p1.write_text(json.dumps(one), encoding="utf-8")
            p2.write_text(json.dumps(two), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "duplicate repository reports"):
                portfolio_plan.build_portfolio([(p1, portfolio_plan.load_report(p1)), (p2, portfolio_plan.load_report(p2))])

    def test_next_action_cannot_override_source_repository(self):
        bad = report("The-Interdependency/a", "f" * 40)
        bad["next_actions"][0]["repository"] = "The-Interdependency/spoofed"
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "bad-action.json"
            path.write_text(json.dumps(bad), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "next_actions\[0\] has missing or unknown fields"):
                portfolio_plan.load_report(path)

    def test_relation_extras_cannot_override_derived_endpoints(self):
        value = report("The-Interdependency/a", "1" * 40, "The-Interdependency/z")
        value["cross_repository_relations"][0]["from"] = "The-Interdependency/spoofed-from"
        value["cross_repository_relations"][0]["to"] = "The-Interdependency/spoofed-to"
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "relation.json"
            path.write_text(json.dumps(value), encoding="utf-8")
            loaded = portfolio_plan.load_report(path)
            projection = portfolio_plan.build_portfolio([(path, loaded)])
            relation = projection["cross_repository_dependencies"][0]
            self.assertEqual(relation["from"], "The-Interdependency/a")
            self.assertEqual(relation["to"], "The-Interdependency/z")
            self.assertNotIn("spoofed", json.dumps(relation))


if __name__ == "__main__":
    unittest.main()
