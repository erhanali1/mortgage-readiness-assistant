import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from readiness import (  # noqa: E402
    applicable_requirements,
    completion_pct,
    evaluate,
    missing_requirements,
    next_action,
    risk_reasons,
    readiness_status,
)


def base_application(**overrides):
    row = {
        "application_id": "APP-TEST",
        "loan_purpose": "Purchase",
        "loan_type": "Conventional",
        "stage": "Processing",
        "income_verified": True,
        "identity_verified": True,
        "credit_authorized": True,
        "purchase_contract": True,
        "appraisal_complete": True,
        "insurance_verified": True,
        "disclosures_signed": True,
        "days_in_stage": 1,
        "last_contact_days": 0,
    }
    row.update(overrides)
    return row


class ApplicableRequirementsTests(unittest.TestCase):
    def test_purchase_includes_contract(self):
        fields = applicable_requirements("Purchase")
        self.assertIn("purchase_contract", fields)
        self.assertEqual(len(fields), 7)

    def test_refinance_excludes_contract(self):
        fields = applicable_requirements("Refinance")
        self.assertNotIn("purchase_contract", fields)
        self.assertEqual(len(fields), 6)


class CompletionTests(unittest.TestCase):
    def test_complete_purchase_is_100(self):
        self.assertEqual(completion_pct(base_application()), 100)

    def test_refinance_ignores_missing_purchase_contract(self):
        app = base_application(loan_purpose="Refinance", purchase_contract=False)
        self.assertEqual(completion_pct(app), 100)
        self.assertEqual(missing_requirements(app), [])

    def test_purchase_missing_two_items(self):
        app = base_application(appraisal_complete=False, insurance_verified=False)
        self.assertEqual(completion_pct(app), 71)
        self.assertEqual(
            missing_requirements(app),
            ["appraisal_complete", "insurance_verified"],
        )


class StatusTests(unittest.TestCase):
    def test_ready_when_complete_and_current(self):
        self.assertEqual(readiness_status(base_application()), "Ready")

    def test_needs_attention_when_incomplete_but_not_stalled(self):
        app = base_application(appraisal_complete=False, insurance_verified=False)
        self.assertEqual(readiness_status(app), "Needs Attention")

    def test_at_risk_when_completion_below_50(self):
        app = base_application(
            identity_verified=False,
            income_verified=False,
            credit_authorized=False,
            disclosures_signed=False,
            purchase_contract=False,
            days_in_stage=1,
            last_contact_days=0,
        )
        self.assertLess(completion_pct(app), 50)
        self.assertEqual(readiness_status(app), "At Risk")

    def test_at_risk_when_days_in_stage_high(self):
        app = base_application(days_in_stage=7)
        self.assertEqual(readiness_status(app), "At Risk")

    def test_at_risk_when_contact_stale(self):
        app = base_application(last_contact_days=5)
        self.assertEqual(readiness_status(app), "At Risk")

    def test_complete_but_aging_stays_at_risk(self):
        app = base_application(days_in_stage=8, last_contact_days=0)
        self.assertEqual(completion_pct(app), 100)
        self.assertEqual(readiness_status(app), "At Risk")

    def test_risk_reasons_explain_all_triggered_thresholds(self):
        app = base_application(
            identity_verified=False,
            income_verified=False,
            credit_authorized=False,
            disclosures_signed=False,
            days_in_stage=8,
            last_contact_days=6,
        )
        reasons = risk_reasons(app)
        self.assertEqual(len(reasons), 3)
        self.assertIn("below 50%", reasons[0])
        self.assertIn("8 days in stage", reasons[1])
        self.assertIn("6 days since contact", reasons[2])

    def test_current_ready_file_has_no_risk_reasons(self):
        self.assertEqual(risk_reasons(base_application()), [])


class NextActionTests(unittest.TestCase):
    def test_priority_order_identity_before_income(self):
        app = base_application(identity_verified=False, income_verified=False)
        self.assertEqual(next_action(app), "Request identity verification")

    def test_skips_complete_items(self):
        app = base_application(disclosures_signed=False, appraisal_complete=False)
        self.assertEqual(next_action(app), "Request disclosures signed")

    def test_purchase_contract_before_appraisal(self):
        app = base_application(purchase_contract=False, appraisal_complete=False)
        self.assertEqual(next_action(app), "Request purchase contract")

    def test_refinance_skips_purchase_contract(self):
        app = base_application(
            loan_purpose="Refinance",
            purchase_contract=False,
            appraisal_complete=False,
        )
        self.assertEqual(next_action(app), "Request appraisal")

    def test_complete_current_file_recommends_human_handoff(self):
        action = next_action(base_application(stage="Processing"))
        self.assertEqual(action, "Review for Underwriting handoff")
        self.assertNotIn("approve", action.lower())
        self.assertNotIn("deny", action.lower())

    def test_complete_stale_contact_recommends_outreach(self):
        app = base_application(last_contact_days=5)
        self.assertEqual(next_action(app), "Contact borrower for a status update")

    def test_complete_aging_stage_recommends_review(self):
        app = base_application(days_in_stage=7, last_contact_days=0)
        self.assertEqual(next_action(app), "Review stage aging with a processor")


class EvaluateTests(unittest.TestCase):
    def test_evaluate_adds_advisory_fields(self):
        result = evaluate(base_application())
        self.assertEqual(result["completion_pct"], 100)
        self.assertEqual(result["status"], "Ready")
        self.assertEqual(result["risk_reasons"], [])
        self.assertEqual(result["missing_requirements"], [])
        self.assertIn("next_action", result)
        self.assertNotIn("Approve", result["next_action"])
        self.assertNotIn("Deny", result["next_action"])


if __name__ == "__main__":
    unittest.main()
