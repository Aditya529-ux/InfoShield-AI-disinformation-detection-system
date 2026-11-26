// Content script for displaying in-page verification results

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.action === "SHOW_INFOSHIELD_VERDICT") {
    displayVerdictCard(message.data);
  } else if (message.action === "SHOW_INFOSHIELD_ERROR") {
    alert("InfoShield Error: " + message.error);
  }
});

function displayVerdictCard(data) {
  // Remove existing card if present
  const existing = document.getElementById("infoshield-floating-card");
  if (existing) existing.remove();

  const isFake = data.prediction === 1;
  const badgeClass = isFake ? "fake" : "reliable";
  const badgeText = isFake ? "⚠️ Likely Disinformation" : "✅ Likely Credible";
  const confText = (data.confidence * 100).toFixed(1) + "%";

  const card = document.createElement("div");
  card.id = "infoshield-floating-card";

  // Tokens preview
  const tokens = (data.explanation.all_token_attributions || []).slice(0, 6);
  let tokenHtml = "";
  tokens.forEach(tok => {
    const cls = tok.category === "fake_signal" ? "fake" : "reliable";
    tokenHtml += `<span class="infoshield-token ${cls}">${escapeHtml(tok.term)}</span>`;
  });

  card.innerHTML = `
    <div class="infoshield-card-header">
      <span class="infoshield-badge ${badgeClass}">${badgeText} (${confText})</span>
      <button class="infoshield-close-btn" id="infoshield-close">✕</button>
    </div>
    <div class="infoshield-rationale">
      ${escapeHtml(data.explanation.rationale)}
    </div>
    ${tokenHtml ? `<div class="infoshield-tokens">${tokenHtml}</div>` : ""}
    <div style="font-size: 11px; font-weight:600; color:#64748b; margin-bottom: 6px;">Was this prediction accurate?</div>
    <div class="infoshield-fb-actions">
      <button class="infoshield-fb-btn" id="infoshield-agree">👍 Agree</button>
      <button class="infoshield-fb-btn" id="infoshield-dis-real">❌ Actually Real</button>
      <button class="infoshield-fb-btn" id="infoshield-dis-fake">❌ Actually Fake</button>
    </div>
  `;

  document.body.appendChild(card);

  // Close button
  card.querySelector("#infoshield-close").addEventListener("click", () => card.remove());

  // Feedback buttons
  card.querySelector("#infoshield-agree").addEventListener("click", () => {
    sendFeedback(data.text, data.prediction, "agree");
    card.remove();
  });
  card.querySelector("#infoshield-dis-real").addEventListener("click", () => {
    sendFeedback(data.text, 0, "disagree");
    card.remove();
  });
  card.querySelector("#infoshield-dis-fake").addEventListener("click", () => {
    sendFeedback(data.text, 1, "disagree");
    card.remove();
  });
}

function sendFeedback(text, userLabel, userAction) {
  fetch("http://localhost:8000/api/feedback", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      text: text,
      user_label: userLabel,
      user_action: userAction,
      source_note: "Submitted from Chrome Extension"
    })
  }).then(r => r.json()).then(res => {
    alert("✅ Feedback recorded! Model weights updated in memory and disk.");
  }).catch(e => {
    console.error("Failed to send feedback:", e);
  });
}

function escapeHtml(str) {
  if (!str) return "";
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}
