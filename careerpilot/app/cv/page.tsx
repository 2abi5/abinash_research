"use client";

import { useEffect, useRef, useState } from "react";
import Link from "next/link";
import Nav from "@/components/Nav";
import Icon from "@/components/Icon";
import { KEYS, loadLS, saveLS } from "@/lib/storage";
import type { CvAnalysis } from "@/app/api/cv/analyze/route";

type Optimized = { markdown: string; changeNotes: string[] };

function mdToHtml(md: string): string {
  const esc = (x: string) => x.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
  const fmt = (x: string) =>
    x.replace(/\*\*(.+?)\*\*/g, "<b>$1</b>").replace(/\*(.+?)\*/g, "<i>$1</i>");
  let html = "";
  let inList = false;
  const closeList = () => { if (inList) { html += "</ul>"; inList = false; } };
  for (const raw of esc(md).split("\n")) {
    const line = raw.trimEnd();
    if (/^###\s/.test(line)) { closeList(); html += `<h3>${fmt(line.slice(4))}</h3>`; }
    else if (/^##\s/.test(line)) { closeList(); html += `<h2>${fmt(line.slice(3))}</h2>`; }
    else if (/^#\s/.test(line)) { closeList(); html += `<h1>${fmt(line.slice(2))}</h1>`; }
    else if (/^[-*]\s/.test(line)) { if (!inList) { html += "<ul>"; inList = true; } html += `<li>${fmt(line.slice(2))}</li>`; }
    else if (line === "") closeList();
    else { closeList(); html += `<p>${fmt(line)}</p>`; }
  }
  closeList();
  return html;
}

function printCv(md: string) {
  const w = window.open("", "_blank", "width=840,height=1060");
  if (!w) return;
  w.document.write(`<!doctype html><html><head><meta charset="utf-8"><title>CV</title><style>
    body{font-family:Georgia,'Times New Roman',serif;color:#141414;max-width:760px;margin:36px auto;line-height:1.5;font-size:14px;padding:0 28px}
    h1{font-size:27px;margin:0 0 2px;letter-spacing:.2px}
    h1+p{margin-top:3px;color:#444}
    h2{font-size:12.5px;text-transform:uppercase;letter-spacing:.13em;border-bottom:1.5px solid #222;padding-bottom:4px;margin:22px 0 8px}
    h3{font-size:14.5px;margin:13px 0 2px}
    ul{margin:4px 0 10px;padding-left:20px}li{margin:3px 0}p{margin:6px 0}
    @media print{body{margin:0 auto}}
  </style></head><body>${mdToHtml(md)}</body></html>`);
  w.document.close();
  w.focus();
  setTimeout(() => w.print(), 400);
}

function ScoreRing({ score }: { score: number }) {
  const r = 40;
  const c = 2 * Math.PI * r;
  const clamped = Math.min(100, Math.max(0, score));
  const color = clamped >= 75 ? "var(--good)" : clamped >= 50 ? "var(--warn)" : "var(--bad)";
  return (
    <svg className="score-svg" width="104" height="104" viewBox="0 0 104 104">
      <circle className="track" cx="52" cy="52" r={r} fill="none" strokeWidth="9" />
      <circle
        className="arc"
        cx="52"
        cy="52"
        r={r}
        fill="none"
        strokeWidth="9"
        stroke={color}
        strokeLinecap="round"
        strokeDasharray={c}
        strokeDashoffset={c * (1 - clamped / 100)}
        transform="rotate(-90 52 52)"
        style={{ color }}
      />
      <text className="score-num" x="52" y="49" textAnchor="middle" dominantBaseline="central">
        {clamped}
      </text>
      <text className="score-of" x="52" y="69" textAnchor="middle">
        / 100
      </text>
    </svg>
  );
}

export default function CvStudio() {
  const [cvText, setCvText] = useState("");
  const [targetRole, setTargetRole] = useState("");
  const [jobDescription, setJobDescription] = useState("");
  const [pdf, setPdf] = useState<{ name: string; base64: string } | null>(null);
  const [analysis, setAnalysis] = useState<CvAnalysis | null>(null);
  const [optimized, setOptimized] = useState<Optimized | null>(null);
  const [busy, setBusy] = useState<"" | "analyze" | "generate" | "build">("");
  const [mode, setMode] = useState<"have" | "build">("have");
  const [b, setB] = useState({
    name: "",
    contact: "",
    education: "",
    experience: "",
    projects: "",
    skills: "",
    extras: "",
  });
  const setBField = (k: keyof typeof b) => (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) =>
    setB((prev) => ({ ...prev, [k]: e.target.value }));
  const [error, setError] = useState("");
  const fileRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    setCvText(loadLS(KEYS.cvText, ""));
    setTargetRole(loadLS(KEYS.targetRole, ""));
    setAnalysis(loadLS<CvAnalysis | null>(KEYS.analysis, null));
    setOptimized(loadLS<Optimized | null>(KEYS.optimized, null));
  }, []);

  function onFile(e: React.ChangeEvent<HTMLInputElement>) {
    setError("");
    const file = e.target.files?.[0];
    if (!file) return;
    if (file.type !== "application/pdf") {
      setError("Only PDF files are supported — or paste your CV as text.");
      return;
    }
    if (file.size > 3 * 1024 * 1024) {
      setError("PDF too large — keep it under 3 MB (export it compressed, or paste the text instead).");
      return;
    }
    const reader = new FileReader();
    reader.onload = () => {
      const url = String(reader.result);
      setPdf({ name: file.name, base64: url.slice(url.indexOf(",") + 1) });
    };
    reader.readAsDataURL(file);
  }

  async function analyze() {
    if (!targetRole.trim()) return setError("Set a target role first.");
    if (!cvText.trim() && !pdf) return setError("Paste your CV or upload a PDF.");
    setBusy("analyze");
    setError("");
    try {
      const res = await fetch("/api/cv/analyze", {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({
          cvText: cvText.trim() || undefined,
          pdfBase64: pdf?.base64,
          targetRole: targetRole.trim(),
          jobDescription: jobDescription.trim() || undefined,
        }),
      });
      const data = await res.json().catch(() => null);
      if (!res.ok)
        return setError(
          data?.error ||
            (res.status === 413
              ? "File too large — keep the PDF under 3 MB."
              : `Request failed (${res.status}) — try again.`) || "Analysis failed.");
      if (!data) return setError("Unexpected response — try again.");
      const a = data as CvAnalysis;
      setAnalysis(a);
      saveLS(KEYS.analysis, a);
      saveLS(KEYS.targetRole, targetRole.trim());
      // If the CV came from a PDF, keep the extracted text for the Apply Kit.
      const text = cvText.trim() || a.cvPlainText || "";
      if (text) {
        setCvText(text);
        saveLS(KEYS.cvText, text);
      }
    } catch {
      setError("Network error — try again.");
    } finally {
      setBusy("");
    }
  }

  async function generate() {
    const source = cvText.trim();
    if (!source) return setError("Analyze first (or paste CV text) so there's a source CV.");
    setBusy("generate");
    setError("");
    try {
      const res = await fetch("/api/cv/generate", {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({
          cvText: source,
          targetRole: targetRole.trim(),
          jobDescription: jobDescription.trim() || undefined,
          keywordsMissing: analysis?.keywordsMissing,
        }),
      });
      const data = await res.json().catch(() => null);
      if (!res.ok)
        return setError(
          data?.error ||
            (res.status === 413
              ? "File too large — keep the PDF under 3 MB."
              : `Request failed (${res.status}) — try again.`) || "Generation failed.");
      setOptimized(data);
      saveLS(KEYS.optimized, data);
    } catch {
      setError("Network error — try again.");
    } finally {
      setBusy("");
    }
  }

  async function buildCv() {
    if (!b.name.trim()) return setError("Add your name.");
    if (!targetRole.trim()) return setError("Set a target role first.");
    if (!b.experience.trim() && !b.education.trim())
      return setError("Add at least some experience or education to build from.");
    setBusy("build");
    setError("");
    try {
      const res = await fetch("/api/cv/build", {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({ ...b, targetRole: targetRole.trim() }),
      });
      const data = await res.json().catch(() => null);
      if (!res.ok)
        return setError(
          data?.error ||
            (res.status === 413
              ? "File too large — keep the PDF under 3 MB."
              : `Request failed (${res.status}) — try again.`) || "Build failed.");
      const built = { markdown: data.markdown as string, changeNotes: (data.tips as string[]) || [] };
      setOptimized(built);
      saveLS(KEYS.optimized, built);
      // The built CV becomes your CV on file, so analysis and Apply Kit use it.
      setCvText(data.markdown);
      saveLS(KEYS.cvText, data.markdown);
      saveLS(KEYS.targetRole, targetRole.trim());
    } catch {
      setError("Network error — try again.");
    } finally {
      setBusy("");
    }
  }

  function download(filename: string, text: string) {
    const a = document.createElement("a");
    a.href = URL.createObjectURL(new Blob([text], { type: "text/markdown" }));
    a.download = filename;
    a.click();
    URL.revokeObjectURL(a.href);
  }

  return (
    <>
      <Nav />
      <div className="container">
        <h1 className="page-title">CV Studio</h1>
        <p className="page-sub">
          Upload or paste your CV, get an honest ATS audit, then generate an optimized rewrite.
        </p>

        <div className="grid grid-2" style={{ alignItems: "start" }}>
          <div className="card anim">
            <h3 className="section"><Icon name="file" size={14} /> Your CV</h3>
            <div className="segment">
              <button type="button" className={mode === "have" ? "on" : ""} onClick={() => setMode("have")}>
                <Icon name="file" size={14} /> I have a CV
              </button>
              <button type="button" className={mode === "build" ? "on" : ""} onClick={() => setMode("build")}>
                <Icon name="wand" size={14} /> Build from scratch
              </button>
            </div>
            <label className="field">Target role *</label>
            <input
              type="text"
              placeholder="e.g. Research Scientist, Data Analyst, ML Engineer…"
              value={targetRole}
              onChange={(e) => {
                setTargetRole(e.target.value);
                saveLS(KEYS.targetRole, e.target.value);
              }}
            />
            {mode === "have" && (<>
            <label className="field">CV text (paste) — or upload a PDF below</label>
            <textarea
              rows={10}
              placeholder="Paste your full CV here…"
              value={cvText}
              onChange={(e) => {
                setCvText(e.target.value);
                saveLS(KEYS.cvText, e.target.value);
              }}
            />
            <label className="field">PDF upload</label>
            <input ref={fileRef} type="file" accept="application/pdf" onChange={onFile} />
            {pdf && (
              <div className="notice">
                <Icon name="file" size={14} style={{ verticalAlign: "-2px", marginRight: 6 }} />
                {pdf.name} attached — it will be parsed during analysis.{" "}
                <button
                  className="btn ghost small"
                  onClick={() => {
                    setPdf(null);
                    if (fileRef.current) fileRef.current.value = "";
                  }}
                >
                  Remove
                </button>
              </div>
            )}
            <label className="field">Job description to match (optional)</label>
            <textarea
              rows={5}
              placeholder="Paste a specific job posting to tailor the analysis…"
              value={jobDescription}
              onChange={(e) => setJobDescription(e.target.value)}
            />
            </>)}

            {mode === "build" && (<>
              <div className="grid grid-2" style={{ gap: 0, columnGap: 14 }}>
                <div>
                  <label className="field">Your name *</label>
                  <input type="text" placeholder="e.g. Abinash Panta" value={b.name} onChange={setBField("name")} />
                </div>
                <div>
                  <label className="field">Contact line</label>
                  <input type="text" placeholder="email · phone · city · linkedin" value={b.contact} onChange={setBField("contact")} />
                </div>
              </div>
              <label className="field">Experience — jobs, internships, research (rough notes are fine)</label>
              <textarea rows={5} placeholder={"e.g. Research Assistant, ABC University lab, 2023–2025 — cleaned survey data, wrote Python scripts, co-authored 2 papers…"} value={b.experience} onChange={setBField("experience")} />
              <label className="field">Education</label>
              <textarea rows={3} placeholder={"e.g. BSc Computer Science, XYZ University, 2024 — GPA 3.7"} value={b.education} onChange={setBField("education")} />
              <label className="field">Skills</label>
              <textarea rows={2} placeholder="e.g. Python, pandas, SQL, Excel, Git…" value={b.skills} onChange={setBField("skills")} />
              <label className="field">Projects (optional)</label>
              <textarea rows={3} placeholder="Personal or academic projects worth showing…" value={b.projects} onChange={setBField("projects")} />
              <label className="field">Extras (optional) — certifications, awards, languages</label>
              <textarea rows={2} placeholder="e.g. Google Data Analytics cert, English + Nepali + Hindi…" value={b.extras} onChange={setBField("extras")} />
            </>)}

            {error && <div className="error"><Icon name="alert" size={16} style={{ marginTop: 2 }} /><span>{error}</span></div>}
            <div style={{ display: "flex", gap: 10, marginTop: 18, flexWrap: "wrap" }}>
              {mode === "have" ? (<>
                <button className="btn" onClick={analyze} disabled={busy !== ""}>
                  {busy === "analyze" ? <span className="spinner" /> : <><Icon name="gauge" size={15} /> Analyze CV</>}
                </button>
                <button className="btn ghost" onClick={generate} disabled={busy !== ""}>
                  {busy === "generate" ? <span className="spinner" /> : <><Icon name="wand" size={15} /> Generate optimized CV</>}
                </button>
              </>) : (
                <button className="btn" onClick={buildCv} disabled={busy !== ""}>
                  {busy === "build" ? <span className="spinner" /> : <><Icon name="wand" size={15} /> Build my CV</>}
                </button>
              )}
            </div>
          </div>

          <div style={{ display: "grid", gap: 16 }}>
            {analysis && (
              <div className="card anim">
                <div className="score-wrap">
                  <ScoreRing score={analysis.atsScore} />
                  <div>
                    <h3 className="section" style={{ marginBottom: 4 }}><Icon name="gauge" size={14} /> ATS score</h3>
                    <div style={{ color: "var(--muted)", fontSize: 14 }}>{analysis.verdict}</div>
                  </div>
                </div>

                <h3 className="section" style={{ marginTop: 22 }}><Icon name="check" size={14} /> Strengths</h3>
                <ul className="clean">{analysis.strengths.map((s, i) => <li key={i}>{s}</li>)}</ul>

                <h3 className="section" style={{ marginTop: 18 }}><Icon name="alert" size={14} /> Gaps</h3>
                <ul className="clean">{analysis.gaps.map((s, i) => <li key={i}>{s}</li>)}</ul>

                <h3 className="section" style={{ marginTop: 18 }}><Icon name="layers" size={14} /> Keywords you have</h3>
                <div>{analysis.keywordsPresent.map((k) => <span key={k} className="chip good">{k}</span>)}</div>

                <h3 className="section" style={{ marginTop: 18 }}><Icon name="layers" size={14} /> Keywords you&apos;re missing</h3>
                <div>{analysis.keywordsMissing.map((k) => <span key={k} className="chip bad">{k}</span>)}</div>

                <h3 className="section" style={{ marginTop: 18 }}><Icon name="wand" size={14} /> Section-by-section fixes</h3>
                <ul className="clean">
                  {analysis.improvements.map((imp, i) => (
                    <li key={i}><b>{imp.section}:</b> {imp.advice}</li>
                  ))}
                </ul>

                <h3 className="section" style={{ marginTop: 18 }}><Icon name="search" size={14} /> Run these job searches</h3>
                <div>
                  {analysis.searchQueries.map((q) => (
                    <Link key={q} href={`/jobs?q=${encodeURIComponent(q)}`} className="chip">
                      <Icon name="search" size={12} /> {q}
                    </Link>
                  ))}
                </div>
              </div>
            )}

            {optimized && (
              <div className="card anim">
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: 8 }}>
                  <h3 className="section" style={{ margin: 0 }}><Icon name="wand" size={14} /> Your CV, polished</h3>
                  <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
                    <button className="btn ghost small" onClick={() => navigator.clipboard.writeText(optimized.markdown)}>
                      <Icon name="copy" size={13} /> Copy
                    </button>
                    <button className="btn ghost small" onClick={() => download("cv.md", optimized.markdown)}>
                      <Icon name="download" size={13} /> Download
                    </button>
                    <button className="btn small" onClick={() => printCv(optimized.markdown)}>
                      <Icon name="file" size={13} /> Print / PDF
                    </button>
                  </div>
                </div>
                <div className="output mono" style={{ marginTop: 12 }}>{optimized.markdown}</div>
                <h3 className="section" style={{ marginTop: 18 }}><Icon name="list" size={14} /> Notes &amp; next steps</h3>
                <ul className="clean">{optimized.changeNotes.map((n, i) => <li key={i}>{n}</li>)}</ul>
              </div>
            )}

            {!analysis && !optimized && (
              <div className="card" style={{ color: "var(--muted)", display: "flex", gap: 10, alignItems: "center" }}>
                <Icon name="sparkles" size={18} />
                Results appear here — the audit takes about 20–40 seconds.
              </div>
            )}
          </div>
        </div>
      </div>
    </>
  );
}
