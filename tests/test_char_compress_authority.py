"""Guard the local-notation boundary separately from preservation fixtures."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class CharCompressAuthorityTests(unittest.TestCase):
    def test_local_notation_does_not_claim_current_geometry(self):
        text = (ROOT / "char-compress/SKILL.md").read_text()
        compact = " ".join(text.split())
        self.assertIn("Optional local text-stack notation", text)
        self.assertIn("not a UCNS construction law or a mandatory EDCM scale ladder", compact)
        self.assertIn("EDCM owns text-domain gonol construction", text)
        self.assertIn("no current UCNS mathematical derivation is claimed", compact)
        for false_claim in ("Punctuation is a stronger typed twist", "Its mathematics is the source of the compression algorithm"):
            self.assertNotIn(false_claim, compact)

    def test_preservation_guards_survive_authority_correction(self):
        text = (ROOT / "char-compress/SKILL.md").read_text()
        for guard in ("Freeze dangerous bones", "Reconstruct and compare", "Carry hmmm",
                      "lost recurrence order", "dropped negation", "changed proof/status label"):
            self.assertIn(guard, text)
