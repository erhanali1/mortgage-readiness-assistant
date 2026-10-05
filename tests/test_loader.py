import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from loader import coerce_row, load_applications, parse_bool  # noqa: E402


class ParseBoolTests(unittest.TestCase):
    def test_true_false_strings(self):
        self.assertTrue(parse_bool("true"))
        self.assertTrue(parse_bool("TRUE"))
        self.assertFalse(parse_bool("false"))
        self.assertFalse(parse_bool(" False "))

    def test_rejects_unknown_values(self):
        with self.assertRaises(ValueError):
            parse_bool("yes")


class CoerceRowTests(unittest.TestCase):
    def test_converts_booleans_and_integers(self):
        row = coerce_row(
            {
                "application_id": "APP-1",
                "income_verified": "true",
                "identity_verified": "false",
                "credit_authorized": "true",
                "purchase_contract": "false",
                "appraisal_complete": "true",
                "insurance_verified": "false",
                "disclosures_signed": "true",
                "days_in_stage": "8",
                "last_contact_days": "6",
            }
        )
        self.assertIs(row["income_verified"], True)
        self.assertIs(row["identity_verified"], False)
        self.assertEqual(row["days_in_stage"], 8)
        self.assertEqual(row["last_contact_days"], 6)


class LoadApplicationsTests(unittest.TestCase):
    def test_reads_csv_file(self):
        csv_text = (
            "application_id,loan_purpose,income_verified,identity_verified,"
            "credit_authorized,purchase_contract,appraisal_complete,"
            "insurance_verified,disclosures_signed,days_in_stage,last_contact_days\n"
            "APP-9,Refinance,true,true,true,false,true,true,true,2,1\n"
        )
        with tempfile.NamedTemporaryFile(
            "w", suffix=".csv", delete=False, encoding="utf-8"
        ) as handle:
            handle.write(csv_text)
            path = handle.name
        rows = load_applications(path)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["application_id"], "APP-9")
        self.assertIs(rows[0]["purchase_contract"], False)
        self.assertEqual(rows[0]["days_in_stage"], 2)


if __name__ == "__main__":
    unittest.main()
