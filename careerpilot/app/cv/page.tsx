"use client";

import { useEffect, useRef, useState } from "react";
import Link from "next/link";
import Nav from "@/components/Nav";
import { KEYS, loadLS, saveLS } from "@/lib/storage";
import type { CvAnalysis } from "@/app/api/cv/analyze/route";

type Optimized = { markdown: string; changeNotes: string[] };

export default function CvStudio() {
  const [cvText, setCvText] = useState("");
  const [targetRole, setTargetRole] = useState("");
  const [jobDescription, setJobDescription] = useState("");
  const [pdf, setPdf] = useState<{ name: string; base64: string } | null>(null);
  const [analysis, setAnalysis] = useState<CvAnalysis | null>(null);
  const [optimized, setOptimized] = useState<Optimized | null>(null);
  const [busy, setBusy] = useState<"" | "analyze" | "generate">("");
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
    if (file.size > 4 * 1024 * 1024) {
      setError("PDF too large — keep it under 4 MB.");
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
      const data = await res.json();
      if (!res.ok) return setError(data.error || "Analysis failed.");
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
      const data = await res.json();
      if (!res.ok) return setError(data.error || "Generation failed.");
      setOptimized(data);
      saveLS(KEYS.optimized, data);
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

  const scoreColor = (s: number) =>
    s >= 75 ? "var(--good)" : s >= 50 ? "var(--warn)" : "var(--bad)";

  return (
    <>
      <Nav />
      <div className="container">
        <h1 className="page-title">CV Studio</h1>
        <p className="page-sub">
          Upload or paste your CV, get an honest ATS audit, then generate an optimized rewrite.
        </p>

        <div className="grid grid-2" style={{ alignItems: "start" }}>
          <div className="card">
            <h3 className="section">Your CV</h3>
            <label className="field">Target role *</label>
            <input
              type="text"
              placeholder="e.g. Research Scientist, Data Analyst, ML Engineer…"
              value={targetRole}
              onChange={(e) => setTargetRole(e.target.value)}
            />
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
                📎 {pdf.name} attached — it will be parsed during analysis.{" "}
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
            {error && <div className="error">{error}</div>}
            <div style={{ display: "flex", gap: 10, marginTop: 18, flexWrap: "wrap" }}>
              <button className="btn" onClick={analyze} disabled={busy !== ""}>
                {busy === "analyze" ? <span className="spinner" /> : "🔬 Analyze CV"}
              </button>
              <button className="btn ghost" onClick={generate} disabled={busy !== ""}>
                {busy === "generate" ? <span className="spinner" /> : "✨ Generate optimized CV"}
              </button>
            </div>
          </div>

          <div style={{ display: "grid", gap: 16 }}>
            {analysis && (
              <div className="card">
                <div className="score-wrap">
                  <div
                    className="score-ring"
                    style={{ "--p": analysis.atsScore, "--ring": scoreColor(analysis.atsScore) } as React.CSSProperties}
                  >
                    <span>{analysis.atsScore}</span>
                  </div>
                  <div>
                    <h3 className="section" style={{ marginBottom: 4 }}>ATS score</h3>
                    <div style={{ color: "var(--muted)", fontSize: 14 }}>{analysis.verdict}</div>
                  </div>
                </div>

                <h3 className="section" style={{ marginTop: 20 }}>✅ Strengths</h3>
                <ul className="clean">{analysis.strengths.map((s, i) => <li key={i}>{s}</li>)}</ul>

                <h3 className="section" style={{ marginTop: 16 }}>⚠️ Gaps</h3>
                <ul className="clean">{analysis.gaps.map((s, i) => <li key={i}>{s}</li>)}</ul>

                <h3 className="section" style={{ marginTop: 16 }}>Keywords you have</h3>
                <div>{analysis.keywordsPresent.map((k) => <span key={k} className="chip good">{k}</span>)}</div>

                <h3 className="section" style={{ marginTop: 16 }}>Keywords you're missing</h3>
                <div>{analysis.keywordsMissing.map((k) => <span key={k} className="chip bad">{k}</span>)}</div>

                <h3 className="section" style={{ marginTop: 16 }}>Section-by-section fixes</h3>
                <ul className="clean">
                  {analysis.improvements.map((imp, i) => (
                    <li key={i}><b>{imp.section}:</b> {imp.advice}</li>
                  ))}
                </ul>

                <h3 className="section" style={{ marginTop: 16 }}>Run these job searches</h3>
                <div>
                  {analysis.searchQueries.map((q) => (
                    <Link key={q} href={`/jobs?q=${encodeURIComponent(q)}`} className="chip" style={{ cursor: "pointer" }}>
                      🔎 {q}
                    </Link>
                  ))}
                </div>
              </div>
            )}

            {optimized && (
              <div className="card">
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: 8 }}>
                  <h3 className="section" style={{ margin: 0 }}>✨ Optimized CV (Markdown)</h3>
                  <div style={{ display: "flex", gap: 8 }}>
                    <button className="btn ghost small" onClick={() => navigator.clipboard.writeText(optimized.markdown)}>
                      Copy
                    </button>
                    <button className="btn small" onClick={() => download("optimized-cv.md", optimized.markdown)}>
                      Download .md
                    </button>
                  </div>
                </div>
                <div className="output mono" style={{ marginTop: 12 }}>{optimized.markdown}</div>
                <h3 className="section" style={{ marginTop: 16 }}>What changed</h3>
                <ul className="clean">{optimized.changeNotes.map((n, i) => <li key={i}>{n}</li>)}</ul>
              </div>
            )}

            {!analysis && !optimized && (
              <div className="card" style={{ color: "var(--muted)" }}>
                Results will appear here — the audit takes ~20–40 seconds.
              </div>
            )}
          </div>
        </div>
      </div>
    </>
  );
}
