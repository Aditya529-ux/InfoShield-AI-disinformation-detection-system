document.getElementById("popup-scan-btn").addEventListener("click", async () => {
  const text = document.getElementById("popup-input").value.trim();
  const resBox = document.getElementById("res-box");

  if (!text) return;

  resBox.style.display = "block";
  resBox.className = "";
  resBox.textContent = "Analyzing claim...";

  try {
    const res = await fetch("http://localhost:8000/api/predict", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text })
    });

    if (!res.ok) throw new Error("Backend server unreachable.");

    const data = await res.json();
    const isFake = data.prediction === 1;
    resBox.className = isFake ? "fake" : "reliable";
    resBox.innerHTML = `
      <strong>${isFake ? "⚠️ Likely Fake" : "✅ Likely Reliable"}</strong> (${(data.confidence * 100).toFixed(1)}%)<br>
      <div style="margin-top:4px;">${data.explanation.rationale}</div>
    `;
  } catch (err) {
    resBox.className = "fake";
    resBox.textContent = "Error: Ensure InfoShield server is running on http://localhost:8000";
  }
});
