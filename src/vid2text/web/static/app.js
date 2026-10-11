const $ = (id) => document.getElementById(id);
let pickTarget = null;
let currentPath = "";
let poller = null;

async function api(url, options) {
  const res = await fetch(url, options);
  const body = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(body.detail || "Something went wrong.");
  return body;
}

function showMessage(text, kind) {
  const box = $("message");
  box.textContent = text;
  box.className = "message " + (kind || "");
  box.hidden = !text;
}

/* ---------- folder browser ---------- */

async function openBrowser(targetId) {
  pickTarget = targetId;
  await loadFolder($(targetId).value.trim());
  $("browser").showModal();
}

async function loadFolder(path) {
  try {
    const data = await api("/api/browse?path=" + encodeURIComponent(path));
    currentPath = data.path;
    $("here").textContent = data.path;
    $("up").disabled = !data.parent;
    $("up").dataset.parent = data.parent || "";
    $("mediaCount").textContent =
      data.media_files ? data.media_files + " video/audio file(s) here" : "";
    const list = $("folders");
    list.innerHTML = "";
    if (!data.dirs.length) {
      const li = document.createElement("li");
      li.className = "empty";
      li.textContent = "No sub-folders";
      list.appendChild(li);
    }
    data.dirs.forEach((d) => {
      const li = document.createElement("li");
      li.textContent = d.name;
      li.onclick = () => loadFolder(d.path);
      list.appendChild(li);
    });
  } catch (err) {
    showMessage(err.message, "error");
    if (path) loadFolder("");
  }
}

document.querySelectorAll("[data-pick]").forEach((btn) =>
  btn.addEventListener("click", () => openBrowser(btn.dataset.pick)));
$("up").onclick = () => loadFolder($("up").dataset.parent);
$("dlgClose").onclick = () => $("browser").close();
$("choose").onclick = () => {
  $(pickTarget).value = currentPath;
  $("browser").close();
  if (pickTarget === "inputDir") checkInput();
  save();
};

async function checkInput() {
  const hint = $("inputHint");
  try {
    const data = await api("/api/browse?path=" + encodeURIComponent($("inputDir").value.trim()));
    hint.textContent = data.media_files
      ? `Found ${data.media_files} video/audio file(s) directly in this folder.`
      : "Every video in the folder (and its sub-folders) will be converted.";
  } catch (_) {
    hint.textContent = "Every video in the folder (and its sub-folders) will be converted.";
  }
}

/* ---------- job control ---------- */

function formats() {
  const out = [];
  if ($("fmtTxt").checked) out.push("txt");
  if ($("fmtJson").checked) out.push("json");
  return out;
}

async function start() {
  showMessage("");
  $("results").innerHTML = "";
  if (!$("inputDir").value.trim() || !$("outputDir").value.trim())
    return showMessage("Please choose both folders first.", "error");
  if (!formats().length)
    return showMessage("Pick at least one format: TXT or JSON.", "error");
  try {
    await api("/api/jobs", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        input_dir: $("inputDir").value.trim(),
        output_dir: $("outputDir").value.trim(),
        formats: formats(),
        model: $("model").value,
        language: $("language").value || null,
        recursive: $("recursive").checked,
        timestamps: $("timestamps").checked,
        overwrite: $("overwrite").checked,
      }),
    });
    save();
    watch();
  } catch (err) {
    showMessage(err.message, "error");
  }
}

function watch() {
  clearInterval(poller);
  poller = setInterval(refresh, 800);
  refresh();
}

async function refresh() {
  const job = await api("/api/jobs/current");
  const running = job.status === "running";
  $("start").hidden = running;
  $("cancel").hidden = !running;
  $("progress").hidden = job.status === "idle";
  const pct = job.total ? Math.round((job.done / job.total) * 100) : 0;
  $("barFill").style.width = (running && !job.total ? 5 : pct) + "%";
  $("progressText").textContent = running
    ? (job.current ? `Working on ${job.current} (${job.done + 1} of ${job.total})` : "Preparing… the first run downloads the speech model.")
    : `${job.done} of ${job.total} file(s) processed`;

  if (!running) {
    clearInterval(poller);
    if (job.status === "error") showMessage(job.error, "error");
    else if (job.status === "cancelled") showMessage("Stopped. Finished files were kept.", "");
    else if (job.status === "finished") {
      if (!job.total) showMessage("No video or audio files were found in that folder.", "error");
      else {
        const failed = job.results.filter((r) => r.status === "failed").length;
        showMessage(failed ? `Done, but ${failed} file(s) failed.` : "All done! Your text files are ready.",
          failed ? "error" : "ok");
      }
    }
    renderResults(job.results);
  }
}

function renderResults(results) {
  const list = $("results");
  list.innerHTML = "";
  const label = { done: "✓", skipped: "↷", failed: "✕" };
  results.forEach((r) => {
    const li = document.createElement("li");
    li.className = r.status;
    li.textContent = `${label[r.status]} ${r.source}` + (r.message ? ` — ${r.message}` : "");
    list.appendChild(li);
  });
}

$("start").onclick = start;
$("cancel").onclick = () => api("/api/jobs/cancel", { method: "POST" });
$("inputDir").addEventListener("change", checkInput);

/* ---------- remember choices ---------- */

const FIELDS = ["inputDir", "outputDir", "model", "language"];
function save() {
  try { FIELDS.forEach((f) => localStorage.setItem("v2t." + f, $(f).value)); } catch (_) {}
}
function restore() {
  try { FIELDS.forEach((f) => { const v = localStorage.getItem("v2t." + f); if (v) $(f).value = v; }); } catch (_) {}
}

(async function init() {
  const cfg = await api("/api/config");
  $("version").textContent = "· v" + cfg.version;
  cfg.models.forEach((m) => {
    const o = document.createElement("option");
    o.value = m;
    o.textContent = m + ({ tiny: " (fastest)", base: " (balanced)", "large-v3": " (best)" }[m] || "");
    $("model").appendChild(o);
  });
  $("model").value = "base";
  restore();
  if (cfg.input_dir) $("inputDir").value = cfg.input_dir;
  if (cfg.output_dir) $("outputDir").value = cfg.output_dir;
  if ($("inputDir").value) checkInput();
  const job = await api("/api/jobs/current");
  if (job.status === "running") watch();
})();
