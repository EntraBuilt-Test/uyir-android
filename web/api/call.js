// Starts a Retell web call for the "Talk to teacher" button. The API key stays on the server.
module.exports = async (req, res) => {
  res.setHeader("Cache-Control", "no-store");
  if (req.method !== "POST") return res.status(405).json({ error: "POST only" });
  const key = process.env.RETELL_API_KEY, agent = process.env.RETELL_AGENT_ID;
  if (!key || !agent) return res.status(500).json({ error: "Voice teacher is not set up yet." });
  try {
    const r = await fetch("https://api.retellai.com/v3/create-web-call", {
      method: "POST",
      headers: { Authorization: "Bearer " + key, "Content-Type": "application/json" },
      body: JSON.stringify({ agent_id: agent })
    });
    const j = await r.json().catch(() => ({}));
    if (!r.ok || !j.access_token) return res.status(502).json({ error: "Could not start the call.", status: r.status, detail: String(j.message || j.error_message || j.error || "").slice(0, 200) });
    return res.status(200).json({ access_token: j.access_token, call_id: j.call_id, transport: j.transport, ice_servers: j.ice_servers });
  } catch (e) {
    return res.status(502).json({ error: "Could not reach the voice service." });
  }
};
