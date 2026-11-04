import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from normalize import normalize
def sample():
    return {"races": [{"state": "TX", "office": "US Senate", "candidates": [{"name": "Example D", "party": "D", "votes": 100}, {"name": "Example R", "party": "R", "votes": 90}], "reporting_pct": 20.0, "called_party": None, "updated_at": "2026-11-03T23:00:00Z"}]}
class NormalizeTests(unittest.TestCase):
    def test_valid(self):
        result = normalize(sample())
        self.assertTrue(result["source_validated"])
        self.assertEqual(result["races"][0]["state"], "TX")
    def test_missing(self):
        with self.assertRaises(ValueError):
            normalize({})
    def test_bad_votes(self):
        data = sample()
        data["races"][0]["candidates"][0]["votes"] = -1
        with self.assertRaises(ValueError):
            normalize(data)
    def test_duplicate_state(self):
        data = sample()
        data["races"].append(data["races"][0].copy())
        with self.assertRaises(ValueError):
            normalize(data)
    def test_empty(self):
        with self.assertRaises(ValueError):
            normalize({"races": []})
if __name__ == "__main__":
    unittest.main()
