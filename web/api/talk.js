// Opens the Retell "Uyir Biology Teacher" talk page. The link (with its token) is kept in a Vercel
// environment variable, RETELL_ORB_URL, so it is not stored in GitHub.
module.exports = (req, res) => {
  const url = process.env.RETELL_ORB_URL || "";
  let ok = false;
  try { const u = new URL(url); ok = u.protocol === "https:" && u.hostname.endsWith("retellai.com"); } catch (e) {}
  res.setHeader("Cache-Control", "no-store");
  if (!ok) return res.status(503).setHeader("Content-Type", "text/plain; charset=utf-8").send("The voice teacher is not set up yet.");
  res.statusCode = 302; res.setHeader("Location", url); res.end();
};
