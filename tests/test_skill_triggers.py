"""Deterministic trigger and activation evaluation tests for all 48 skills.

Usage: python -m unittest tests/test_skill_triggers.py -v
"""
from __future__ import annotations

import json
import math
import re
import unittest
from collections import Counter
from pathlib import Path

from tools.build_codex_plugin_skills import canonical_frontmatter

ROOT = Path(__file__).resolve().parents[1]
SKILLS_JSON = ROOT / "skills.json"

_STOPWORDS = frozenset({
    "a", "an", "and", "are", "as", "at", "be", "before", "by", "can", "do",
    "for", "from", "has", "have", "how", "if", "in", "into", "is", "it", "its",
    "load", "may", "more", "no", "not", "of", "on", "one", "only", "or",
    "other", "should", "such", "than", "that", "the", "their", "them", "then",
    "these", "this", "to", "use", "using", "was", "were", "what", "when",
    "whenever", "where", "whether", "which", "while", "who", "with", "without",
    "you", "your",
})

_TOKEN_RE = re.compile(r"[a-z0-9][a-z0-9_.-]*")


def _tokenize(text: str) -> list[str]:
    tokens: list[str] = []
    for raw in _TOKEN_RE.findall(text.lower()):
        cleaned = raw.strip("._-")
        if not cleaned or len(cleaned) < 2 or cleaned in _STOPWORDS:
            continue
        tokens.append(cleaned)
        if "-" in cleaned or "_" in cleaned or "." in cleaned:
            for part in re.split(r"[-_.]", cleaned):
                if len(part) >= 2 and part not in _STOPWORDS:
                    tokens.append(part)
    return tokens


def _split_positive_negative(description: str) -> tuple[str, str]:
    match = re.search(r"\bDo not load\b", description)
    if not match:
        return description, ""
    return description[: match.start()].strip(), description[match.start() :].strip()


def _load_catalog() -> list[dict[str, str]]:
    data = json.loads(SKILLS_JSON.read_text(encoding="utf-8"))
    catalog: list[dict[str, str]] = []
    for entry in data["skills"]:
        fm = canonical_frontmatter(ROOT / str(entry["path"]))
        pos, neg = _split_positive_negative(fm["description"])
        catalog.append({
            "name": fm["name"],
            "description": fm["description"],
            "positive": pos,
            "negative": neg,
        })
    return catalog


class SkillMatcher:
    """Pure-stdlib BM25 + bigram + boundary-exclusion skill router."""

    def __init__(self, catalog: list[dict[str, str]]) -> None:
        self.catalog = catalog
        self.docs: list[dict[str, object]] = []
        df: Counter[str] = Counter()
        lengths: list[int] = []

        for item in catalog:
            pos_tokens = _tokenize(f"{item['name']} {item['name']} {item['positive']}")
            neg_tokens = set(_tokenize(item["negative"]))
            bigrams = {
                f"{pos_tokens[i]}_{pos_tokens[i + 1]}"
                for i in range(len(pos_tokens) - 1)
            }
            tf = Counter(pos_tokens)
            lengths.append(len(pos_tokens))
            for term in tf:
                df[term] += 1
            self.docs.append({
                "name": item["name"],
                "tf": tf,
                "len": len(pos_tokens),
                "bigrams": bigrams,
                "neg": neg_tokens,
            })

        n_docs = len(self.docs)
        self.avg_len = sum(lengths) / max(1, n_docs)
        self.idf = {
            term: math.log((n_docs - freq + 0.5) / (freq + 0.5) + 1.0)
            for term, freq in df.items()
        }

    def rank(self, query: str) -> list[tuple[str, float]]:
        q_tokens = _tokenize(query)
        q_bigrams = {
            f"{q_tokens[i]}_{q_tokens[i + 1]}"
            for i in range(len(q_tokens) - 1)
        }
        q_lower = query.lower()
        k1 = 1.4
        b = 0.65
        scored: list[tuple[str, float]] = []

        for doc in self.docs:
            name = str(doc["name"])
            tf: Counter[str] = doc["tf"]  # type: ignore[assignment]
            doc_len = int(doc["len"])  # type: ignore[arg-type]
            bigrams: set[str] = doc["bigrams"]  # type: ignore[assignment]
            neg: set[str] = doc["neg"]  # type: ignore[assignment]

            score = 0.0
            for term in set(q_tokens):
                if term not in tf:
                    continue
                freq = tf[term]
                idf = self.idf.get(term, 0.0)
                denom = freq + k1 * (1.0 - b + b * (doc_len / max(1.0, self.avg_len)))
                score += idf * (freq * (k1 + 1.0)) / denom

            score += 0.8 * len(q_bigrams & bigrams)
            if name in q_lower:
                score += 3.0
            if neg:
                neg_overlap = len(set(q_tokens) & neg)
                pos_overlap = len(set(q_tokens) & set(tf))
                if neg_overlap > pos_overlap:
                    score -= 1.5 * (neg_overlap - pos_overlap)

            scored.append((name, score))

        scored.sort(key=lambda pair: (-pair[1], pair[0]))
        return scored


class SkillTriggerEvalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.catalog = _load_catalog()
        cls.matcher = SkillMatcher(cls.catalog)

    def test_every_skill_has_bounded_trigger_description(self) -> None:
        self.assertEqual(48, len(self.catalog))
        for item in self.catalog:
            with self.subTest(skill=item["name"]):
                desc = item["description"]
                self.assertLessEqual(len(desc), 1024)
                self.assertTrue(
                    "Load this when" in desc or "Use this when" in desc,
                    f"missing trigger phrase in {item['name']}",
                )

    def test_positive_activation_all_48_skills(self) -> None:
        prompts = {
            "msdmd": "Audit metadata coverage and provenance using native conventions and MSDMD blocks",
            "doc-build": "Wire documentation coverage checks into CI tying docstrings to DOCS blocks",
            "cap-build": "Build a capability registry auditing exposed API signatures against CAPABILITIES",
            "deps-build": "Check dependency topology graph cycles and lockfiles for architecture drift",
            "owner-build": "Audit unowned code and route reviews from CODEOWNERS and OWNERS stewardship",
            "test-build": "Refactor CONTRACTS and CHECKS declarations for test owners without executing them",
            "meta-module-build": "Turn a new capability idea into a bounded module manifest and MODULE_BUILD plan",
            "risk-boundary-build": "Declare runtime auth, storage, network, and user-data BOUNDARIES before migration",
            "ratios": "Record loc_comments, imports_exports, and calls_definitions ratios at module boundaries",
            "canon": "Decide whether a repo-local practice should become org canon or stay hmmm",
            "domain-claims": "Disambiguate a contested acronym across domains before attaching provenance to canon",
            "manifest": "Generate the mechanical pyproject.toml layout block inside CLAUDE.md with a CI check",
            "llms-build": "Generate and check root llms.txt from source LLMS blocks for LLM consumption",
            "char-compress": "Compress a long audit handoff thread without dropping negations, values, or unresolved hmmm",
            "visitor-intro": "A newcomer asks what is The Interdependency and how do these repos fit together",
            "adaptive-elicitation": "Interview the user one question at a time after harvesting facts from prior files",
            "agent-instantiation": "Fork and merge PCNAEngine sub-agent instances in a0ucns via sub_agent_spawn",
            "a0p-instancing": "Manage AgentInstance CharacterSheet CRUD with ZFAE weight banks in a0-betatest",
            "plain-lens": "Create a progressive-disclosure multi-lens ELI companion view of dense canonical text",
            "thought-lens": "Translate raw fragmentary coined notes into audience-legible prose preserving the claim kernel",
            "meta": "Consult current METAPAT to decide which distinctions and cross-domain correspondences organize work",
            "gonol-build": "Check closure, atomic participation, and replay for UCNS gonol-language builds in stack",
            "ucns-option-selection": "Compare competing UCNS candidates and issue a scoped decision receipt under eligibility gates",
            "epac-selection-display": "Prepare a receipt-backed EPAC molecule visualization packet for WebMCP display",
            "the-interdependency": "Assemble EDCM transcripts for analysis on interdependentway.org for Harrison Hovel",
            "interdependent-work-graph": "Coordinate producer and evidence commits across multiple repos before picking a workspace",
            "stack-update": "Update stack-manifest.json and BASE.json when adding a participant to The-Interdependency/stack",
            "project-incubation-graduation": "Extract an incubated component into a released PyPI package and reconsumption boundary",
            "distributed-publication": "Publish one ordered textbook from multiple source repos preserving commits and licenses",
            "website-builder-journal": "Edit pages in The-Interdependency.github.io and append a By the builder journal entry",
            "loop-eng": "Design an autonomous Discover Plan Execute Verify Iterate maker-checker agent loop",
            "agent-ops": "Harden a tool-using bot with approval gates, untrusted retrieval rules, and budget preflight",
            "pstack-orchestration": "Run pstack poteto-mode repo orchestration with baseline reproduction and PASS/FAIL evidence",
            "fresh-making": "Compute the minimum rebuild closure to make stale derived projections provably fresh",
            "action-calibration": "Decide between a minimal bounded falsifier and a maximal coherent build under budget constraints",
            "wdll": "Select consequential work and falsifiable completion criteria for a newly scoped spawn",
            "repo-audit-repair": "Audit and repair an existing repository checking if green CI hides placeholder gates",
            "github-tests": "Audit GitHub Actions workflows and test strategy for flaky tests and required gates",
            "skill-build": "Author a new SKILL.md and bring it into skill-lib compliance with tests",
            "skill-usage": "Record material skill usage and report experimental versus daily-use maturity counts",
            "ssh-automation": "Write a non-interactive OpenSSH bash script over Google Cloud IAP with ProxyJump and known_hosts",
            "vm-mcp": "Connect Claude or ChatGPT to a private GCE VM over MCP without an SSH private key",
            "typed-meta-frontend": "Generate TypeScript forms and living specs UI from backend module metadata",
            "sql-queries": "Write a Snowflake and PostgreSQL window-function funnel SQL query",
            "statistical-analysis": "Run hypothesis testing, outlier detection, and correlation significance checks",
            "explore-data": "Profile a new CSV dataset for null rates, column distributions, and data quality issues",
            "validate-data": "QA an analysis for survivorship bias and verify aggregation numbers before stakeholder sharing",
            "data-visualization": "Create publication-quality matplotlib and plotly charts with accessible color palettes",
        }
        self.assertEqual(set(item["name"] for item in self.catalog), set(prompts))

        strict_top1 = {
            "vm-mcp", "char-compress", "ssh-automation", "explore-data",
            "validate-data", "sql-queries", "statistical-analysis",
            "data-visualization", "llms-build", "ratios", "manifest",
            "gonol-build", "ucns-option-selection", "epac-selection-display",
            "website-builder-journal", "pstack-orchestration",
            "agent-instantiation", "a0p-instancing", "adaptive-elicitation",
            "visitor-intro", "thought-lens", "plain-lens", "stack-update",
            "distributed-publication", "github-tests", "repo-audit-repair",
            "skill-usage", "skill-build", "typed-meta-frontend",
        }
        for skill_name, query in prompts.items():
            with self.subTest(skill=skill_name):
                ranked = self.matcher.rank(query)
                top3 = [name for name, _ in ranked[:3]]
                self.assertIn(skill_name, top3, f"{skill_name} not in top 3 for {query!r}: {ranked[:5]}")
                if skill_name in strict_top1:
                    self.assertEqual(skill_name, ranked[0][0], f"expected {skill_name} #1, got {ranked[:3]}")

    def test_boundary_disambiguation_and_non_triggers(self) -> None:
        disambiguation_cases = [
            ("Connect ChatGPT to a GCE VM via MCP personal-console without SSH keys", "vm-mcp", "ssh-automation"),
            ("Write a bash scp/rsync deployment script over Google Cloud IAP SSH with host-key checks", "ssh-automation", "vm-mcp"),
            ("Create AgentInstance CharacterSheet with ZFAE weights in a0-betatest", "a0p-instancing", "agent-instantiation"),
            ("Fork PCNAEngine sub-agents in a0ucns with spawn caps", "agent-instantiation", "a0p-instancing"),
            ("Compress a repo audit handoff keeping negations, operators, and frozen bones", "char-compress", "gonol-build"),
            ("Profile null rates and column distributions in a new CSV file", "explore-data", "validate-data"),
            ("QA a revenue report for survivorship bias and denominator shifting before sharing", "validate-data", "explore-data"),
            ("Give Claude bounded shell and file access to a Google Compute Engine VM over a private tunnel without putting an SSH key in context", "vm-mcp", "ssh-automation"),
            ("Condense a huge conversation transcript for agent handoff without losing negations, dates, or unresolved questions", "char-compress", "gonol-build"),
        ]
        for query, preferred, avoided in disambiguation_cases:
            with self.subTest(preferred=preferred, avoided=avoided):
                scores = dict(self.matcher.rank(query))
                self.assertGreater(scores[preferred], scores[avoided], (preferred, avoided, scores[preferred], scores[avoided]))

        for unrelated in (
            "What is the weather forecast for Seattle tomorrow morning?",
            "Bake a crusty sourdough loaf at 450 degrees Fahrenheit",
        ):
            with self.subTest(unrelated=unrelated):
                top_skill, top_score = self.matcher.rank(unrelated)[0]
                self.assertLess(top_score, 2.5, f"unexpected strong activation {top_skill}={top_score:.2f} for {unrelated!r}")


if __name__ == "__main__":
    unittest.main()
