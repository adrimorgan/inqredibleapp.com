import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("check_content", ROOT / "scripts" / "check_content.py")
CHECK = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(CHECK)


class ContentChecksTests(unittest.TestCase):
    def setUp(self):
        self.manifest = json.loads((ROOT / "content" / "release-content.json").read_text(encoding="utf-8"))

    def test_manifest_contract_is_valid(self):
        self.assertEqual([], CHECK.validate_manifest(self.manifest))

    def test_generated_matrix_is_deterministic(self):
        first = CHECK.render_matrix(self.manifest)
        second = CHECK.render_matrix(json.loads(json.dumps(self.manifest)))
        self.assertEqual(first, second)
        self.assertIn("legal-2.5.0-v1", first)
        self.assertIn("Firebase Crashlytics", first)

    def test_unconditional_trial_is_rejected(self):
        errors = CHECK.prohibited_claim_errors("Start PRO with 3 days free", "fixture.html")
        self.assertTrue(any("unconditional trial" in error for error in errors))

    def test_static_commercial_value_is_rejected(self):
        errors = CHECK.prohibited_claim_errors('{"price": "4.99", "priceCurrency": "EUR"}', "fixture.html")
        self.assertTrue(any("static JSON-LD price" in error for error in errors))

    def test_unsupported_public_claims_are_rejected(self):
        samples = ("Guaranteed safe scanner", "Press-ready PDF", "Includes cloud sync", "Lifetime plan")
        for sample in samples:
            with self.subTest(sample=sample):
                self.assertTrue(CHECK.prohibited_claim_errors(sample, "fixture.html"))

    def test_negative_boundaries_are_allowed(self):
        safe = "No cloud sync. Scanner warnings do not certify safety. RGB/sRGB is not press-ready."
        self.assertEqual([], CHECK.prohibited_claim_errors(safe, "fixture.html"))


if __name__ == "__main__":
    unittest.main()
