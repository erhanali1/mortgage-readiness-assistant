# Mortgage Application Readiness Assistant

A dependency-free operations prototype that helps a mortgage-processing team identify incomplete application files, understand workflow risks, and determine the next follow-up action.

## Why this project

Missing documents and stalled handoffs can delay mortgage processing. This dashboard converts a synthetic application dataset into an explainable work queue so an operations analyst can prioritize follow-up without automating an underwriting decision.

## Features

- Readiness totals for Ready, Needs Attention, and At Risk files
- Document-completion percentage by application
- Plain-language missing requirements and recommended next actions
- Explainable risk reasons based on completion, stage aging, and contact recency
- Stage and readiness filters
- Purchase-specific and refinance-specific requirements
- Automated unit tests for data loading and business rules

## Architecture

```text
Synthetic CSV data
      |
      v
Python loader -> readiness rules -> JSON API
                                      |
                                      v
                         HTML/CSS/JavaScript dashboard
```

The application uses only Python's standard library plus browser-native HTML, CSS, and JavaScript.

## Run locally

```bash
python3 src/server.py
```

Open [http://127.0.0.1:8000](http://127.0.0.1:8000).

## Run the tests

```bash
python3 -m unittest discover -s tests -v
```

The test suite covers CSV parsing, purchase/refinance requirements, completion calculations, readiness classifications, risk explanations, and next-action ordering.

## Prototype business rules

- A purchase file requires a purchase contract; a refinance does not.
- A file is marked At Risk when completion is below 50%, time in stage is at least seven days, or borrower contact is at least five days old.
- An incomplete file that does not meet an At Risk condition is marked Needs Attention.
- A complete, current file is marked Ready.

These thresholds are illustrative prototype assumptions. A production implementation would validate them with mortgage-operations specialists, service-level objectives, historical workflow data, and applicable compliance requirements.

## Responsible-use boundaries

- All included records are synthetic and contain no borrower personal information.
- The tool does not approve, deny, price, or underwrite a mortgage.
- Recommendations are advisory and require human review.
- A production version would require authentication, authorization, encryption, audit logging, data-retention controls, monitoring, and integration testing.

## Possible next steps

- Make thresholds configurable by an authorized administrator
- Add application-level drill-down and audit history
- Integrate with a loan-origination or document-management system
- Measure false-positive risk flags and operational time saved
- Add role-based access controls and observability

## Development approach

This prototype was developed with AI-assisted coding support. The project owner defined the business problem, constraints, rules, human-review boundary, and test expectations, then reviewed and validated the implementation. See [`CURSOR_START_HERE.md`](CURSOR_START_HERE.md) for the planning workflow.
