const API = "http://127.0.0.1:8000";

const SUPPORTED = [
  "reddit.com", "redd.it",
  "youtube.com", "youtu.be",
  "twitter.com", "x.com",
];

const urlBox   = document.getElementById("urlBox");
const btn      = document.getElementById("btn");
const quality  = document.getElementById("quality");
const progressWrap = document.getElementById("progressWrap");
const bar      = document.getElementById("bar");
const status   = document.getElementById("status");
const serverWarning = document.getElementById("serverWarning");

let currentUrl = null;

// ── Init: aktive Tab-URL laden ────────────────────────────────────────────────

async function init() {
  // Server-Erreichbarkeit prüfen
  try {
    await fetch(`${API}/openapi.json`, { signal: AbortSignal.timeout(2000) });
  } catch {
    serverWarning.style.display = "block";
    urlBox.textContent = "Server offline";
    return;
  }

  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  currentUrl = tab?.url || "";

  const supported = SUPPORTED.some(d => currentUrl.includes(d));

  if (supported) {
    urlBox.textContent = currentUrl;
    btn.disabled = false;
    btn.addEventListener("click", startDownload);
  } else {
    urlBox.textContent = "Keine unterstützte Seite (Reddit, YouTube, Twitter/X)";
    urlBox.classList.add("unsupported");
  }
}

// ── Download ──────────────────────────────────────────────────────────────────

async function startDownload() {
  btn.disabled = true;
  progressWrap.style.display = "block";
  setProgress(0, "Startet...");

  try {
    const res = await fetch(`${API}/download`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ url: currentUrl, quality: quality.value }),
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || "Fehler");
    }
    const { job_id } = await res.json();
    await followProgress(job_id);
    triggerDownload(job_id);
  } catch (e) {
    setProgress(0, "Fehler: " + e.message, true);
  } finally {
    btn.disabled = false;
  }
}

function followProgress(jobId) {
  return new Promise((resolve, reject) => {
    const es = new EventSource(`${API}/progress/${jobId}`);
    es.onmessage = (e) => {
      const d = JSON.parse(e.data);
      if (d.status === "done") {
        setProgress(100, "Fertig! Download startet...");
        es.close();
        resolve();
      } else if (d.status === "error") {
        es.close();
        reject(new Error(d.error || "Unbekannter Fehler"));
      } else {
        setProgress(d.progress, d.message);
      }
    };
    es.onerror = () => { es.close(); reject(new Error("Verbindung verloren")); };
  });
}

function triggerDownload(jobId) {
  chrome.tabs.create({ url: `${API}/file/${jobId}`, active: false });
}

function setProgress(pct, msg, isError = false) {
  bar.style.width = pct + "%";
  bar.className = "progress-bar" + (isError ? " error" : "");
  status.textContent = msg;
  status.className = "status" + (isError ? " error" : "");
}

init();
