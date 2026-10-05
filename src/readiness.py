"""Advisory readiness rules for synthetic mortgage applications.

These rules measure document and process completeness for the next
operations step. They do not approve or deny a mortgage.
"""

from __future__ import annotations

ALWAYS_REQUIRED = (
    "identity_verified",
    "income_verified",
    "credit_authorized",
    "disclosures_signed",
    "appraisal_complete",
    "insurance_verified",
)

PURCHASE_ONLY = ("purchase_contract",)

REQUIREMENT_LABELS = {
    "identity_verified": "Identity verification",
    "income_verified": "Income verification",
    "credit_authorized": "Credit authorization",
    "disclosures_signed": "Disclosures signed",
    "purchase_contract": "Purchase contract",
    "appraisal_complete": "Appraisal",
    "insurance_verified": "Insurance verification",
}

# Operations follow-up order: identity → income → credit → disclosures →
# purchase contract (Purchase only) → appraisal → insurance.
NEXT_ACTION_ORDER = (
    "identity_verified",
    "income_verified",
    "credit_authorized",
    "disclosures_signed",
    "purchase_contract",
    "appraisal_complete",
    "insurance_verified",
)

STATUS_AT_RISK = "At Risk"
STATUS_READY = "Ready"
STATUS_NEEDS_ATTENTION = "Needs Attention"

AT_RISK_COMPLETION_BELOW = 50
AT_RISK_DAYS_IN_STAGE = 7
AT_RISK_LAST_CONTACT_DAYS = 5

STAGE_HANDOFF = {
    "Processing": "Review for Underwriting handoff",
    "Underwriting": "Review for Closing handoff",
    "Closing": "Review for closing completion",
}


def applicable_requirements(loan_purpose: str) -> tuple[str, ...]:
    purpose = (loan_purpose or "").strip()
    if purpose.lower() == "purchase":
        # Keep next-action order; purchase_contract sits before appraisal.
        return NEXT_ACTION_ORDER
    return ALWAYS_REQUIRED


def _is_complete(value: object) -> bool:
    return value is True


def missing_requirements(application: dict) -> list[str]:
    missing = []
    for field in applicable_requirements(application.get("loan_purpose", "")):
        if not _is_complete(application.get(field)):
            missing.append(field)
    return missing


def missing_requirement_labels(application: dict) -> list[str]:
    return [REQUIREMENT_LABELS[field] for field in missing_requirements(application)]


def completion_pct(application: dict) -> int:
    fields = applicable_requirements(application.get("loan_purpose", ""))
    if not fields:
        return 0
    done = sum(1 for field in fields if _is_complete(application.get(field)))
    return round(done / len(fields) * 100)


def risk_reasons(application: dict) -> list[str]:
    """Explain every prototype threshold that triggered an At Risk status."""
    reasons = []
    pct = completion_pct(application)
    days_in_stage = int(application.get("days_in_stage") or 0)
    last_contact = int(application.get("last_contact_days") or 0)
    if pct < AT_RISK_COMPLETION_BELOW:
        reasons.append(
            f"Completion is {pct}% (below {AT_RISK_COMPLETION_BELOW}%)"
        )
    if days_in_stage >= AT_RISK_DAYS_IN_STAGE:
        reasons.append(
            f"{days_in_stage} days in stage (threshold: {AT_RISK_DAYS_IN_STAGE})"
        )
    if last_contact >= AT_RISK_LAST_CONTACT_DAYS:
        reasons.append(
            f"{last_contact} days since contact "
            f"(threshold: {AT_RISK_LAST_CONTACT_DAYS})"
        )
    return reasons


def readiness_status(application: dict) -> str:
    if risk_reasons(application):
        return STATUS_AT_RISK
    if not missing_requirements(application):
        return STATUS_READY
    return STATUS_NEEDS_ATTENTION


def next_action(application: dict) -> str:
    missing = missing_requirements(application)
    if missing:
        label = REQUIREMENT_LABELS[missing[0]].lower()
        return f"Request {label}"

    last_contact = int(application.get("last_contact_days") or 0)
    days_in_stage = int(application.get("days_in_stage") or 0)
    if last_contact >= AT_RISK_LAST_CONTACT_DAYS:
        return "Contact borrower for a status update"
    if days_in_stage >= AT_RISK_DAYS_IN_STAGE:
        return "Review stage aging with a processor"
    stage = application.get("stage") or ""
    return STAGE_HANDOFF.get(stage, "Review for next-stage handoff")


def evaluate(application: dict) -> dict:
    """Return the original row plus advisory readiness fields."""
    result = dict(application)
    missing = missing_requirement_labels(application)
    result["completion_pct"] = completion_pct(application)
    result["status"] = readiness_status(application)
    result["risk_reasons"] = risk_reasons(application)
    result["missing_requirements"] = missing
    result["next_action"] = next_action(application)
    return result


def evaluate_all(applications: list[dict]) -> list[dict]:
    return [evaluate(row) for row in applications]


def summarize(evaluated: list[dict]) -> dict:
    counts = {
        "total": len(evaluated),
        "ready": 0,
        "needs_attention": 0,
        "at_risk": 0,
    }
    for row in evaluated:
        if row["status"] == STATUS_READY:
            counts["ready"] += 1
        elif row["status"] == STATUS_NEEDS_ATTENTION:
            counts["needs_attention"] += 1
        elif row["status"] == STATUS_AT_RISK:
            counts["at_risk"] += 1
    return counts
