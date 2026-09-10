const presetList = document.getElementById("preset-list");
const logEditor = document.getElementById("log-editor");
const previewTitle = document.getElementById("preview-title");
const previewMeta = document.getElementById("preview-meta");
const fileInput = document.getElementById("file-input");
const fileName = document.getElementById("file-name");
const analyzeBtn = document.getElementById("analyze-btn");
const statusEl = document.getElementById("status");
const errorEl = document.getElementById("error");
const resultsEl = document.getElementById("results");
const configBanner = document.getElementById("config-banner");
const infoBtn = document.getElementById("info-btn");
const infoModal = document.getElementById("info-modal");
const infoClose = document.getElementById("info-close");

let selectedPreset = "flare-14";
let usingUpload = false;

init();
openInfo();

async function init() {
  const health = await fetch("/health").then((r) => r.json()).catch(() => null);
  if (health && !health.cerebras_configured) {
    configBanner.textContent =
      "This instance has no CEREBRAS_API_KEY. You can browse diaries, but analysis will fail until the key is set on Railway.";
    configBanner.classList.remove("hidden");
  }

  const data = await fetch("/api/presets").then((r) => r.json());
  data.presets.forEach((preset, index) => {
    const btn = document.createElement("button");
    btn.type = "button";
    btn.className = "preset";
    btn.setAttribute("role", "option");
    btn.dataset.id = preset.id;
    btn.innerHTML = `<em>${preset.pattern} · ${preset.days} days</em><strong>${preset.title}</strong><span>${preset.teaser}</span>`;
    btn.addEventListener("click", () => selectPreset(preset.id, btn));
    if (index === 0) btn.setAttribute("aria-selected", "true");
    presetList.appendChild(btn);
  });
  await loadPreset(selectedPreset);
}

async function selectPreset(id, btn) {
  usingUpload = false;
  selectedPreset = id;
  fileInput.value = "";
  fileName.textContent = "";
  presetList.querySelectorAll(".preset").forEach((el) => el.setAttribute("aria-selected", "false"));
  btn.setAttribute("aria-selected", "true");
  await loadPreset(id);
}

async function loadPreset(id) {
  const preset = await fetch(`/api/presets/${id}`).then((r) => r.json());
  previewTitle.textContent = preset.title;
  previewMeta.textContent = preset.raw
    ? `${preset.patient} · ${preset.days} notes`
    : `${preset.patient} · ${preset.days} days`;
  logEditor.value = preset.raw
    ? preset.raw
    : preset.logs.map((note, i) => `Day ${i + 1}: ${note}`).join("\n");
}

fileInput.addEventListener("change", async () => {
  const file = fileInput.files[0];
  if (!file) return;
  usingUpload = true;
  selectedPreset = null;
  presetList.querySelectorAll(".preset").forEach((el) => el.setAttribute("aria-selected", "false"));
  fileName.textContent = file.name;
  previewTitle.textContent = "Uploaded diary";
  previewMeta.textContent = file.name;
  logEditor.value = await file.text();
});

logEditor.addEventListener("input", () => {
  usingUpload = true;
  selectedPreset = null;
  presetList.querySelectorAll(".preset").forEach((el) => el.setAttribute("aria-selected", "false"));
  previewTitle.textContent = "Edited diary";
  previewMeta.textContent = `${countDays(logEditor.value)} day(s)`;
});

analyzeBtn.addEventListener("click", generateBrief);

async function generateBrief() {
  hide(errorEl);
  hide(resultsEl);
  analyzeBtn.disabled = true;
  show(statusEl, "Extracting Harvey-Bradshaw scores, indexing the diary, and writing the trajectory summary…");

  const payload = usingUpload || !selectedPreset
    ? { text: logEditor.value }
    : { preset_id: selectedPreset };

  try {
    const response = await fetch("/api/analyze", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const data = await parseResponse(response);
    if (!response.ok) {
      throw new Error(formatDetail(data.detail) || `Analysis failed (${response.status}).`);
    }
    renderResults(data);
  } catch (err) {
    show(errorEl, err.message);
  } finally {
    hide(statusEl);
    analyzeBtn.disabled = false;
  }
}

function renderResults(data) {
  const stats = data.stats;
  document.getElementById("result-source").textContent = data.source_label;
  const pill = document.getElementById("tier-pill");
  pill.textContent = stats.clinical_tier;
  pill.className = `tier ${tierClass(stats.current_hbi_avg)}`;

  document.getElementById("hbi-from").textContent = stats.baseline_hbi_avg.toFixed(1);
  document.getElementById("hbi-to").textContent = stats.current_hbi_avg.toFixed(1);
  document.getElementById("hbi-windows").textContent =
    `${stats.baseline_window} → ${stats.current_window}`;

  const delta = document.getElementById("hbi-delta");
  const sign = stats.hbi_trend_delta > 0 ? "+" : "";
  delta.textContent = `${sign}${stats.hbi_trend_delta.toFixed(1)}`;
  delta.className = `delta ${stats.hbi_trend_delta > 0 ? "up" : "down"}`;

  document.getElementById("stat-window").textContent = `${stats.monitoring_window_days} days`;
  document.getElementById("stat-adherence").textContent = `${stats.medication_adherence_percent}%`;
  document.getElementById("stat-liquid").textContent = stats.total_liquid_stools_reported;
  document.getElementById("stat-comps").textContent =
    stats.reported_complications.length ? stats.reported_complications.join(", ") : "None reported";
  document.getElementById("stat-missed").textContent = stats.adherence_detail;

  document.getElementById("summary-body").innerHTML = renderSummary(data.summary);
  document.getElementById("chart-img").src = `data:image/png;base64,${data.chart_png_b64}`;

  const pdfBtn = document.getElementById("pdf-btn");
  pdfBtn.href = `/api/reports/${data.report_id}/pdf`;

  const tbody = document.getElementById("history-body");
  tbody.innerHTML = "";
  data.history.forEach((day) => {
    const tr = document.createElement("tr");
    const cls = tierClass(day.hbi);
    tr.innerHTML = `
      <td>${day.day}</td>
      <td>${day.date}</td>
      <td class="hbi-cell ${cls}">${day.hbi}</td>
      <td>${day.wellbeing_label}</td>
      <td>${day.pain_label}</td>
      <td>${day.liquid}</td>
      <td>${day.comps.length ? day.comps.join(", ") : "—"}</td>
      <td>${day.meds ? "Taken" : "Missed"}</td>
    `;
    tbody.appendChild(tr);
  });

  resultsEl.classList.remove("hidden");
  resultsEl.scrollIntoView({ behavior: "smooth", block: "start" });
}

function renderSummary(text) {
  const escaped = String(text)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");
  return escaped
    .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
    .replace(/\n/g, "<br>");
}

function tierClass(score) {
  if (score < 5) return "remission";
  if (score < 8) return "mild";
  return "flare";
}

async function parseResponse(response) {
  const raw = await response.text();
  if (!raw) {
    throw new Error(`Empty response (${response.status}). The server may have run out of memory or timed out.`);
  }
  try {
    return JSON.parse(raw);
  } catch {
    throw new Error(raw.replace(/\s+/g, " ").slice(0, 400));
  }
}

function formatDetail(detail) {
  if (!detail) return "";
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail)) {
    return detail.map((item) => item.msg || JSON.stringify(item)).join("; ");
  }
  return String(detail);
}

function countDays(text) {
  return text.split("\n").filter((line) => line.trim()).length;
}

function show(el, text) {
  el.textContent = text;
  el.classList.remove("hidden");
}

function hide(el) {
  el.classList.add("hidden");
}

function openInfo() {
  infoModal.classList.add("open");
  document.body.classList.add("modal-open");
  infoBtn.setAttribute("aria-expanded", "true");
  infoClose.focus();
}

function closeInfo() {
  infoModal.classList.remove("open");
  document.body.classList.remove("modal-open");
  infoBtn.setAttribute("aria-expanded", "false");
  infoBtn.focus();
}

infoBtn.addEventListener("click", openInfo);
infoClose.addEventListener("click", closeInfo);
infoModal.addEventListener("click", (event) => {
  if (event.target === infoModal) closeInfo();
});
document.addEventListener("keydown", (event) => {
  if (event.key === "Escape" && infoModal.classList.contains("open")) {
    closeInfo();
  }
});
