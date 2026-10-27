// Called by the Retell voice agent (custom function "search_textbook").
// Receives the student's question, searches the Uyir textbooks and returns plain text.
const fs = require("fs");
const path = require("path");
const { search, toks } = require("./_search.js");

const DATA = path.join(process.cwd(), "data");
let CATALOG = null;
const BOOKS = new Map();

function catalog() {
  if (!CATALOG) CATALOG = JSON.parse(fs.readFileSync(path.join(DATA, "catalog.json"), "utf8"));
  return CATALOG;
}
function loadBook(id) {
  if (!BOOKS.has(id)) {
    const b = JSON.parse(fs.readFileSync(path.join(DATA, "books", id + ".json"), "utf8"));
    b.idx = null;
    BOOKS.set(id, b);
  }
  return BOOKS.get(id);
}
function quick(b, qt) {
  if (!qt.length) return 0;
  if (!b.flat) b.flat = b.pages.map(p => p.t.toLowerCase());
  let s = 0;
  for (const t of b.flat) { let n = 0; for (const w of qt) if (t.includes(w)) n++; if (n) s += (n / qt.length) ** 2; }
  return s;
}
function isTamil(t) {
  const ta = (t.match(/[஀-௿]/g) || []).length, en = (t.match(/[A-Za-z]/g) || []).length;
  return ta > 0 && ta >= en * 0.5;
}
function pick(body) {
  const a = (body && body.args) || body || {};
  const q = a.query || a.question || "";
  return { q: String(q).trim().slice(0, 400), std: String(a.standard || a.std || "").trim(), lang: String(a.language || "").trim() };
}
function clean(t) {
  return t.replace(/\s+/g, " ").replace(/[•▪◦]/g, " ").trim().slice(0, 1800);
}

module.exports = (req, res) => {
  res.setHeader("Content-Type", "text/plain; charset=utf-8");
  res.setHeader("Cache-Control", "no-store");
  if (req.method !== "POST") return res.status(405).send("POST only");
  try {
    let body = req.body;
    if (typeof body === "string") { try { body = JSON.parse(body); } catch (e) { body = { query: body }; } }
    const { q, std, lang } = pick(body);
    if (!q) return res.status(200).send("NOT_FOUND: no question was received.");
    const medium = lang === "ta" || lang === "en" ? lang : (isTamil(q) ? "ta" : "en");
    let list = catalog().filter(b => b.medium === medium && (!std || b.std === std || b.std.replace(/\D/g, "") === std.replace(/\D/g, "")));
    if (!list.length) list = catalog().filter(b => b.medium === medium);
    // Quick pre-check: rank books by how many pages contain the question's words, then search only the best few.
    const qt = [...new Set(toks(q))];
    const ranked = list.map(m => ({ m, s: quick(loadBook(m.id), qt) })).filter(x => x.s > 0).sort((a, b) => b.s - a.s).slice(0, 3);
    let best = null;
    for (const { m } of ranked) {
      const r = search(loadBook(m.id), q, false);
      if (r && (!best || r.score > best.score)) best = r;
    }
    if (!best) return res.status(200).send("NOT_FOUND: the textbook does not cover this question.");
    const where = `${best.book.label}, Std ${best.book.std}, page ${best.page.pg || best.page.n}`;
    return res.status(200).send(`${clean(best.text)}\n\n(Source: ${where})`);
  } catch (e) {
    return res.status(200).send("NOT_FOUND: the textbook search had a problem. Ask the student to try again.");
  }
};
