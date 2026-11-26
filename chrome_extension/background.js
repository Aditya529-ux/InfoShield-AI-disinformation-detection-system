// Background service worker for InfoShield Chrome Extension (Manifest V3)

chrome.runtime.onInstalled.addListener(() => {
  chrome.contextMenus.create({
    id: "infoshield_verify_selection",
    title: "🛡️ Verify with InfoShield",
    contexts: ["selection"]
  });
});

chrome.contextMenus.onClicked.addListener(async (info, tab) => {
  if (info.menuItemId === "infoshield_verify_selection" && info.selectionText) {
    const text = info.selectionText.trim();
    if (!text) return;

    try {
      const response = await fetch("http://localhost:8000/api/predict", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text })
      });

      if (!response.ok) {
        throw new Error("InfoShield backend is unreachable. Make sure the server is running on port 8000.");
      }

      const result = await response.json();
      
      // Send result to content script in the active tab to display floating badge
      chrome.tabs.sendMessage(tab.id, {
        action: "SHOW_INFOSHIELD_VERDICT",
        data: result
      });
    } catch (err) {
      chrome.tabs.sendMessage(tab.id, {
        action: "SHOW_INFOSHIELD_ERROR",
        error: err.message
      });
    }
  }
});
