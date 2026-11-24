"""Execute sql-queries example patterns against SQLite fixtures.

Usage: python -m unittest tests.test_sql_queries_examples
SQLite truncates integer / integer like PostgreSQL, so it catches examples that
forget to promote to a fractional type. The funnel example is run verbatim apart
from a one-line shim for the PostgreSQL interval window predicate.
"""

from __future__ import annotations

import re
import sqlite3
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "sql-queries" / "SKILL.md"
WINDOW_PG = "CURRENT_DATE - INTERVAL '30 days'"
WINDOW_SQLITE = "datetime('now', '-30 days')"


def section_sql(text: str, heading: str) -> str:
    section = text.split(heading, 1)[1]
    return section.split("```sql\n", 1)[1].split("```", 1)[0]


class SqlQueriesExamplesTest(unittest.TestCase):
    def setUp(self) -> None:
        self.text = SKILL.read_text(encoding="utf-8")
        self.db = sqlite3.connect(":memory:")
        self.addCleanup(self.db.close)

    def test_percent_of_total_keeps_fractions_for_integer_revenue(self) -> None:
        window_block = section_sql(self.text, "### Window Functions")
        expressions = [
            line.strip()
            for line in window_block.splitlines()
            if re.search(r"\bas pct_of_(total|category)\b", line)
        ]
        self.assertEqual(2, len(expressions))
        self.db.executescript(
            "CREATE TABLE sales(category TEXT, revenue INTEGER);"
            "INSERT INTO sales VALUES ('a', 100), ('a', 200), ('b', 50);"
        )
        rows = self.db.execute(
            f"SELECT category, revenue, {', '.join(expressions)} FROM sales ORDER BY revenue"
        ).fetchall()
        shares = {revenue: (total, category) for _, revenue, total, category in rows}
        self.assertAlmostEqual(100 / 350, shares[100][0])
        self.assertAlmostEqual(200 / 350, shares[200][0])
        self.assertAlmostEqual(1 / 3, shares[100][1])
        self.assertAlmostEqual(2 / 3, shares[200][1])
        self.assertAlmostEqual(1.0, shares[50][1])

    def test_funnel_steps_count_only_users_who_reached_prior_steps_in_order(self) -> None:
        query = section_sql(self.text, "### Funnel Analysis")
        self.assertEqual(1, query.count(WINDOW_PG))
        query = query.replace(WINDOW_PG, WINDOW_SQLITE)
        self.db.executescript(
            """
            CREATE TABLE events(user_id INTEGER, event TEXT, event_time TEXT, event_date TEXT);
            INSERT INTO events(user_id, event, event_time) VALUES
              (1, 'page_view', datetime('now', '-10 days')),
              (1, 'signup_start', datetime('now', '-9 days')),
              (1, 'signup_complete', datetime('now', '-8 days')),
              (1, 'first_purchase', datetime('now', '-7 days')),
              (2, 'signup_start', datetime('now', '-5 days')),
              (3, 'signup_start', datetime('now', '-5 days')),
              (4, 'page_view', datetime('now', '-5 days')),
              (5, 'page_view', datetime('now', '-6 days')),
              (5, 'signup_complete', datetime('now', '-5 days')),
              (6, 'signup_start', datetime('now', '-6 days')),
              (6, 'page_view', datetime('now', '-5 days')),
              (7, 'page_view', datetime('now', '-40 days')),
              (7, 'signup_start', datetime('now', '-5 days'));
            UPDATE events SET event_date = date(event_time);
            """
        )
        cursor = self.db.execute(query)
        row = dict(zip([column[0] for column in cursor.description], cursor.fetchone()))
        # Users 2, 3 and 7 never viewed in the window; user 6 started before viewing;
        # user 5 skipped signup_start. Only user 1 converts past the first step.
        self.assertEqual(4, row["viewed"])
        self.assertEqual(1, row["started_signup"])
        self.assertEqual(1, row["completed_signup"])
        self.assertEqual(1, row["purchased"])
        self.assertEqual(25.0, row["view_to_start_pct"])
        for key in ("view_to_start_pct", "start_to_complete_pct", "complete_to_purchase_pct"):
            self.assertLessEqual(row[key], 100.0)


if __name__ == "__main__":
    unittest.main()
