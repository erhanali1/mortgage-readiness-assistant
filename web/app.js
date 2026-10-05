const statusClass = {
  Ready: "ready",
  "Needs Attention": "attention",
  "At Risk": "risk",
};

let applications = [];

function byId(id) {
  return document.getElementById(id);
}

function renderSummary(summary) {
  byId("total-count").textContent = summary.total;
  byId("ready-count").textContent = summary.ready;
  byId("attention-count").textContent = summary.needs_attention;
  byId("risk-count").textContent = summary.at_risk;
}

function fillStageFilter(rows) {
  const select = byId("stage-filter");
  const stages = [...new Set(rows.map((row) => row.stage))].sort();
  stages.forEach((stage) => {
    const option = document.createElement("option");
    option.value = stage;
    option.textContent = stage;
    select.appendChild(option);
  });
}

function filteredRows() {
  const stage = byId("stage-filter").value;
  const status = byId("status-filter").value;
  return applications.filter((row) => {
    const stageOk = stage === "all" || row.stage === stage;
    const statusOk = status === "all" || row.status === status;
    return stageOk && statusOk;
  });
}

function missingHtml(items) {
  if (!items.length) {
    return "<span class='sub'>None</span>";
  }
  return `<ul class="missing">${items.map((item) => `<li>${item}</li>`).join("")}</ul>`;
}

function riskReasonsHtml(items) {
  if (!items || !items.length) {
    return "";
  }
  return `<ul class="risk-reasons">${items
    .map((item) => `<li>${item}</li>`)
    .join("")}</ul>`;
}

function renderTable() {
  const rows = filteredRows();
  const tbody = byId("app-rows");
  const empty = byId("empty-state");
  tbody.innerHTML = "";
  empty.classList.toggle("hidden", rows.length > 0);

  rows.forEach((row) => {
    const tr = document.createElement("tr");
    const klass = statusClass[row.status] || "";
    tr.innerHTML = `
      <td>
        <div class="id">${row.application_id}</div>
        <div class="sub">${row.days_in_stage} days in stage · ${row.last_contact_days} days since contact</div>
      </td>
      <td>${row.loan_purpose}<div class="sub">${row.loan_type}</div></td>
      <td>${row.stage}</td>
      <td>${row.completion_pct}%</td>
      <td>
        <span class="badge ${klass}">${row.status}</span>
        ${riskReasonsHtml(row.risk_reasons)}
      </td>
      <td>${missingHtml(row.missing_requirements)}</td>
      <td>${row.next_action}</td>
    `;
    tbody.appendChild(tr);
  });
}

async function init() {
  const response = await fetch("/api/applications");
  const data = await response.json();
  applications = data.applications;
  byId("advisory").textContent = data.advisory_notice;
  renderSummary(data.summary);
  fillStageFilter(applications);
  renderTable();
  ["stage-filter", "status-filter"].forEach((id) => {
    const el = byId(id);
    el.addEventListener("change", renderTable);
    el.addEventListener("input", renderTable);
  });
}

init();
