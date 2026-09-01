// ── DOM references ────────────────────────────────────────────────────────────
const noteInput = document.getElementById("note-input");
const saveBtn = document.getElementById("save-btn");
const clearBtn = document.getElementById("clear-btn");
const statusMsg = document.getElementById("status-msg");

// ── Load saved note on page open ────────────────────────────────────────────
chrome.runtime.sendMessage({ action: "getNote" }, (response) => {
  if (response && response.note) {
    noteInput.value = response.note;
  }
});

// ── Save ────────────────────────────────────────────────────────────────────
saveBtn.addEventListener("click", () => {
  const text = noteInput.value.trim();
  chrome.runtime.sendMessage({ action: "saveNote", text }, (response) => {
    if (response && response.success) {
      showStatus("Note saved!", "green");
    } else {
      showStatus("Failed to save.", "red");
    }
  });
});

// ── Clear ───────────────────────────────────────────────────────────────────
clearBtn.addEventListener("click", () => {
  noteInput.value = "";
  chrome.runtime.sendMessage({ action: "clearNote" }, (response) => {
    if (response && response.success) {
      showStatus("Note cleared.", "#555");
    }
  });
});

// ── Helper ──────────────────────────────────────────────────────────────────
function showStatus(msg, color) {
  statusMsg.textContent = msg;
  statusMsg.style.color = color;
  setTimeout(() => {
    statusMsg.textContent = "";
  }, 2000);
}
