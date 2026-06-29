const express = require("express");

const app = express();
const PORT = 4000;

// In-memory store of received alerts (newest first). Resets on restart.
const alerts = [];

// Parse incoming JSON request bodies into JavaScript objects.
app.use(express.json());

// Health check — confirms the server is alive.
app.get("/", (req, res) => {
  res.json({ status: "ok", alertsStored: alerts.length });
});

// Receive a detection alert from the Python detector.
app.post("/api/alerts", (req, res) => {
  const alert = req.body;

  if (!alert || typeof alert.pid === "undefined") {
    return res.status(400).json({ error: "Invalid alert: 'pid' is required." });
  }

  const stored = {
    pid: alert.pid,
    name: alert.name || "unknown",
    score: alert.score || 0,
    reasons: alert.reasons || [],
    receivedAt: new Date().toISOString(),
  };

  alerts.unshift(stored);
  console.log(`[ALERT] pid=${stored.pid} name=${stored.name} score=${stored.score}`);

  res.status(201).json({ message: "Alert stored.", stored });
});

// Return all stored alerts.
app.get("/api/alerts", (req, res) => {
  res.json(alerts);
});

app.listen(PORT, () => {
  console.log(`Reporting backend listening on http://localhost:${PORT}`);
});
