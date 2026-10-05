# AI-Assisted Development Workflow

## 1. Open this folder

In Cursor, choose **File > Open Folder** and select this repository's root folder.

Allow Cursor to finish indexing the folder.

## 2. Open Agent in Plan mode

- On macOS, open Agent with `Cmd+I`.
- Press `Shift+Tab` until **Plan** is selected.
- Paste the prompt below.

## 3. First prompt

```text
Read README.md and inspect data/applications.csv. I am new to Cursor and want to understand the plan before any code is written.

Design a small, dependency-free Mortgage Application Readiness Assistant. It should use Python for the business rules and local server, and HTML/CSS/JavaScript for a clean dashboard. It must calculate completion percentage, identify missing requirements, assign Ready / Needs Attention / At Risk status, recommend the next action, and include automated tests.

First explain:
1. The proposed file structure.
2. The business rules you recommend.
3. How data will move from the CSV to the dashboard.
4. How we will test the application.

Do not edit files yet. Wait for my approval.
```

## 4. Review the plan

Do not approve automatically. Check that Cursor proposes:

- A separate module for business rules
- A small local server
- A dashboard interface
- Automated tests
- No real applicant data
- No automated loan approval or denial

Ask questions if anything is unclear.

## 5. Build only the first milestone

After you understand the plan, switch to **Agent** mode and send:

```text
Implement only milestone 1: create the Python business-rules module and automated tests. Do not build the web interface yet. Explain every file you create, run the tests, and show me the results.
```

## 6. What to record

Keep notes on:

- How you described the business problem to Cursor
- A suggestion from Cursor that you changed or rejected
- How you reviewed the generated code
- What tests found or confirmed
- How you protected privacy and kept a human in control

The goal is not to say “Cursor built it for me.” The goal is to explain how you used Cursor to plan, implement, review, and validate a responsible solution.
