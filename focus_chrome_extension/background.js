// ── Initialize defaults on install ──────────────────────────────────────────
chrome.runtime.onInstalled.addListener(() => {
  chrome.storage.local.get(
    ["allowedDomains", "sessionActive", "note"],
    (data) => {
      const defaults = {};
      if (data.allowedDomains === undefined) defaults.allowedDomains = [];
      if (data.sessionActive === undefined) defaults.sessionActive = false;
      if (data.note === undefined) defaults.note = "";
      if (Object.keys(defaults).length > 0) {
        chrome.storage.local.set(defaults);
      }
    },
  );
});

// ── Message handler ─────────────────────────────────────────────────────────
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  switch (message.action) {
    // ── Notes ────────────────────────────────────────────────────────
    case "saveNote":
      chrome.storage.local.set({ note: message.text }, () => {
        sendResponse({ success: true });
      });
      return true; // keep channel open for async response

    case "getNote":
      chrome.storage.local.get("note", (data) => {
        sendResponse({ note: data.note || "" });
      });
      return true;

    case "clearNote":
      chrome.storage.local.set({ note: "" }, () => {
        sendResponse({ success: true });
      });
      return true;

    // ── Session ──────────────────────────────────────────────────────
    case "startSession":
      chrome.storage.local.set({ sessionActive: true }, () => {
        sendResponse({ success: true });
      });
      return true;

    case "stopSession":
      chrome.storage.local.set({ sessionActive: false }, () => {
        sendResponse({ success: true });
      });
      return true;

    case "getSessionState":
      chrome.storage.local.get(["sessionActive", "allowedDomains"], (data) => {
        sendResponse({
          sessionActive: data.sessionActive || false,
          allowedDomains: data.allowedDomains || [],
        });
      });
      return true;

    // ── Allowed domains ──────────────────────────────────────────────
    case "addAllowedDomain":
      chrome.storage.local.get("allowedDomains", (data) => {
        const domains = data.allowedDomains || [];
        if (!domains.includes(message.domain)) {
          domains.push(message.domain);
          chrome.storage.local.set({ allowedDomains: domains }, () => {
            sendResponse({ success: true, domains });
          });
        } else {
          sendResponse({ success: true, domains });
        }
      });
      return true;

    case "removeAllowedDomain":
      chrome.storage.local.get("allowedDomains", (data) => {
        const domains = (data.allowedDomains || []).filter(
          (d) => d !== message.domain,
        );
        chrome.storage.local.set({ allowedDomains: domains }, () => {
          sendResponse({ success: true, domains });
        });
      });
      return true;

    case "getAllowedDomains":
      chrome.storage.local.get("allowedDomains", (data) => {
        sendResponse({ domains: data.allowedDomains || [] });
      });
      return true;

    default:
      sendResponse({ error: "Unknown action" });
      return false;
  }
});

// ── Navigation blocking ─────────────────────────────────────────────────────
chrome.webNavigation.onCommitted.addListener((details) => {
  if (details.frameId !== 0) return;

  const url = new URL(details.url);
  const domain = url.hostname;

  chrome.storage.local.get(["allowedDomains", "sessionActive"], (data) => {
    if (!data.sessionActive) return;
    if (!data.allowedDomains) return;
    if (data.allowedDomains.includes(domain)) return;

    const blockUrl =
      chrome.runtime.getURL("blocked.html") +
      "?domain=" +
      encodeURIComponent(domain) +
      "&tabId=" +
      details.tabId;

    chrome.tabs.update(details.tabId, { url: blockUrl });
  });
});
