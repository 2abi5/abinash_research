"use client";

import { Suspense, useEffect, useRef, useState } from "react";
import { useSearchParams } from "next/navigation";
import Nav from "@/components/Nav";
import Icon from "@/components/Icon";
import { KEYS, TrackedApp, loadLS, saveLS } from "@/lib/storage";
import { deepLinks } from "@/lib/jobs";
import type { Job } from "@/lib/jobs";
import type { ScoutResult } from "@/app/api/jobs/scout/route";
import type { CvAnalysis } from "@/app/api/cv/analyze/route";

function JobFinder() {
  const params = useSearchParams();
  const [query, setQuery] = useState("");
  const [location, setLocation] = useState("");
  const [jobs, setJobs] = useState<Job[]>([]);
  const [scout, setScout] = useState<ScoutResult | null>(null);
  const [boardErrors, setBoardErrors] = useState<string[]>([]);
  const [note, setNote] = useState("");
  const [busySearch, setBusySearch] = useState(false);
  const [busyScout, setBusyScout] = useState(false);
  const [error, setError] = useState("");
  const [searched, setSearched] = useState(false);
  // Which "keywords · location" each result card was produced for, so stale
  // cards are labeled and cleared when a different search runs.
  const [listFor, setListFor] = useState("");
  const [scoutFor, setScoutFor] = useState("");
  const autoRan = useRef(false);
  const [tracked, setTracked] = useState<Set<string>>(new Set());
  const [suggestions, setSuggestions] = useState<string[]>([]);

  useEffect(() => {
    const qp = params.get("q");
    const q = qp || loadLS(KEYS.targetRole, "");
    if (q) setQuery(q);
    // A chip from CV Studio should search immediately, not just prefill.
    if (qp && !autoRan.current) {
      autoRan.current = true;
      search(qp);
    }
    const analysis = loadLS<CvAnalysis | null>(KEYS.analysis, null);
    if (analysis?.searchQueries) setSuggestions(analysis.searchQueries.slice(0, 6));
    setTracked(new Set(loadLS<TrackedApp[]>(KEYS.tracker, []).map((t) => t.id)));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  async function search(q?: string) {
    if (busySearch) return;
    const term = (q ?? query).trim();
    if (!term) return setError("Enter keywords to search.");
    if (q) setQuery(q);
    setBusySearch(true);
    setError("");
    try {
      const res = await fetch("/api/jobs/search", {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({ query: term, location: location.trim() || undefined }),
        signal: AbortSignal.timeout(30_000),
      });
      const data = await res.json();
      if (!res.ok) return setError(data.error || "Search failed.");
      setJobs(data.jobs);
      setBoardErrors(data.errors || []);
      setNote(data.note || "");
      setSearched(true);
      const key = location.trim() ? `${term} · ${location.trim()}` : term;
      setListFor(key);
      if (scout && scoutFor !== key) {
        setScout(null);
        setScoutFor("");
      }
    } catch (e) {
      setError(
        e instanceof DOMException && (e.name === "TimeoutError" || e.name === "AbortError")
          ? "The board search timed out — try again."
          : "Network error — try again.",
      );
    } finally {
      setBusySearch(false);
    }
  }

  async function runScout() {
    if (busyScout) return;
    const term = query.trim();
    if (!term) return setError("Enter a role for the scout.");
    setBusyScout(true);
    setError("");
    try {
      const res = await fetch("/api/jobs/scout", {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({ role: term, location: location.trim() || undefined }),
        signal: AbortSignal.timeout(290_000),
      });
      const data = await res.json();
      if (!res.ok) return setError(data.error || "Scout failed.");
      setScout(data);
      const key = location.trim() ? `${term} · ${location.trim()}` : term;
      setScoutFor(key);
      if (searched && listFor !== key) {
        setJobs([]);
        setBoardErrors([]);
        setNote("");
        setSearched(false);
        setListFor("");
      }
    } catch (e) {
      setError(
        e instanceof DOMException && (e.name === "TimeoutError" || e.name === "AbortError")
          ? "The scout took too long and was stopped — try again or narrow the role."
          : "Network error — try again.",
      );
    } finally {
      setBusyScout(false);
    }
  }

  function track(job: { id: string; title: string; company: string; url: string }) {
    const list = loadLS<TrackedApp[]>(KEYS.tracker, []);
    if (list.some((t) => t.id === job.id)) return;
    list.unshift({
      id: job.id,
      title: job.title,
      company: job.company,
      url: job.url,
      status: "Saved",
      notes: "",
      addedAt: new Date().toISOString(),
    });
    saveLS(KEYS.tracker, list);
    setTracked(new Set(list.map((t) => t.id)));
  }

  return (
    <div className="container">
      <h1 className="page-title">Job Finder</h1>
      <p className="page-sub">
        Live listings from open job boards, AI web scouting, and pre-filled searches on the big boards.
      </p>

      <div className="card anim">
        <div className="grid grid-2">
          <div>
            <label className="field">Keywords</label>
            <input
              type="text"
              placeholder="e.g. machine learning engineer python"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && search()}
            />
          </div>
          <div>
            <label className="field">Location (optional)</label>
            <input
              type="text"
              placeholder="e.g. Kathmandu · Berlin · Remote"
              value={location}
              onChange={(e) => setLocation(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && search()}
            />
          </div>
        </div>
        {suggestions.length > 0 && (
          <div style={{ marginTop: 12 }}>
            <span style={{ color: "var(--muted)", fontSize: 13, marginRight: 8 }}>From your CV analysis:</span>
            {suggestions.map((s) => (
              <button key={s} className="chip" onClick={() => search(s)}>
                <Icon name="search" size={12} /> {s}
              </button>
            ))}
          </div>
        )}
        {error && <div className="error">{error}</div>}
        <div style={{ display: "flex", gap: 10, marginTop: 16, flexWrap: "wrap" }}>
          <button className="btn" onClick={() => search()} disabled={busySearch}>
            {busySearch ? <span className="spinner" /> : <><Icon name="search" size={15} /> Search live boards</>}
          </button>
          <button className="btn ghost" onClick={runScout} disabled={busyScout}>
            {busyScout ? <span className="spinner" /> : <><Icon name="bot" size={15} /> AI web scout</>}
          </button>
        </div>
        {busyScout && (
          <div className="notice">
            The scout is searching the live web — this usually takes a minute or two. You can keep
            using “Search live boards” and the board links meanwhile.
          </div>
        )}
      </div>

      {query.trim().length > 1 && (
        <div className="card" style={{ marginTop: 16 }}>
          <h3 className="section"><Icon name="link" size={14} /> Open this search on the big boards</h3>
          <p style={{ color: "var(--muted)", fontSize: 13, margin: "0 0 10px" }}>
            Always in sync with the keywords and location above.
          </p>
          <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
            {deepLinks(query.trim(), location.trim() || undefined).map((l) => (
              <a key={l.board} href={l.url} target="_blank" rel="noopener noreferrer" className="btn ghost small">
                {l.board} <Icon name="external" size={12} />
              </a>
            ))}
          </div>
        </div>
      )}

      {scout && (
        <div className="card anim" style={{ marginTop: 16 }}>
          <h3 className="section">
            <Icon name="bot" size={14} /> AI scout findings{" "}
            {scoutFor && <span className="badge">{scoutFor}</span>}
          </h3>
          <p style={{ color: "var(--muted)", fontSize: 14 }}>{scout.summary}</p>
          {scout.findings.map((f, i) => (
            <div className="job" key={i}>
              <div>
                <div className="job-title">{f.title} — {f.company}</div>
                <div className="job-meta">{f.location} · {f.note}</div>
              </div>
              <div className="job-actions">
                <a className="btn small" href={f.url} target="_blank" rel="noopener noreferrer">View <Icon name="external" size={13} /></a>
                <button
                  className="btn ghost small"
                  disabled={tracked.has(`scout-${f.url}`)}
                  onClick={() => track({ id: `scout-${f.url}`, title: f.title, company: f.company, url: f.url })}
                >
                  {tracked.has(`scout-${f.url}`) ? "Tracked ✓" : "+ Track"}
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {searched && (
        <div className="card" style={{ marginTop: 16 }}>
          <h3 className="section">
            <Icon name="briefcase" size={14} /> Live listings{" "}
            {listFor && <span className="badge">{listFor}</span>}{" "}
            {jobs.length > 0 && <span className="badge">{jobs.length}</span>}
          </h3>
          {boardErrors.length > 0 && (
            <div className="notice">Some boards were unreachable: {boardErrors.join(", ")}.</div>
          )}
          {note && <div className="notice">{note}</div>}
          {jobs.length === 0 && !note && (
            <p style={{ color: "var(--muted)" }}>
              No matches on the open boards — try the AI scout or the big-board links above.
            </p>
          )}
          {jobs.map((j) => (
            <div className="job" key={j.id}>
              <div>
                <div className="job-title">{j.title} — {j.company}</div>
                <div className="job-meta">
                  {j.location}
                  {j.salary ? ` · ${j.salary}` : ""}
                  {j.publishedAt ? ` · ${new Date(j.publishedAt).toLocaleDateString()}` : ""}
                  {" · "}
                  <span className="badge">{j.source}</span>
                </div>
                {j.tags.length > 0 && (
                  <div style={{ marginTop: 6 }}>
                    {j.tags.map((t) => <span key={t} className="chip">{t}</span>)}
                  </div>
                )}
              </div>
              <div className="job-actions">
                <a className="btn small" href={j.url} target="_blank" rel="noopener noreferrer">Apply <Icon name="external" size={13} /></a>
                <button
                  className="btn ghost small"
                  disabled={tracked.has(j.id)}
                  onClick={() => track(j)}
                >
                  {tracked.has(j.id) ? "Tracked ✓" : "+ Track"}
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default function JobsPage() {
  return (
    <>
      <Nav />
      <Suspense>
        <JobFinder />
      </Suspense>
    </>
  );
}
