"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import Nav from "@/components/Nav";
import Icon from "@/components/Icon";
import { KEYS, TrackedApp, loadLS, saveLS } from "@/lib/storage";
import type { ApplyKit } from "@/app/api/apply/kit/route";

const STATUSES: TrackedApp["status"][] = ["Saved", "Applied", "Interview", "Offer", "Rejected"];

function CopyBtn({ text }: { text: string }) {
  const [done, setDone] = useState(false);
  return (
    <button
      className="btn ghost small"
      onClick={() => {
        navigator.clipboard.writeText(text);
        setDone(true);
        setTimeout(() => setDone(false), 1500);
      }}
    >
      <Icon name={done ? "check" : "copy"} size={13} /> {done ? "Copied" : "Copy"}
    </button>
  );
}

export default function ApplyPage() {
  const [hasCv, setHasCv] = useState(true);
  const [jobTitle, setJobTitle] = useState("");
  const [company, setCompany] = useState("");
  const [jobDescription, setJobDescription] = useState("");
  const [kit, setKit] = useState<ApplyKit | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [tracker, setTracker] = useState<TrackedApp[]>([]);

  useEffect(() => {
    setHasCv(Boolean(loadLS(KEYS.cvText, "")));
    setTracker(loadLS<TrackedApp[]>(KEYS.tracker, []));
  }, []);

  function updateTracker(next: TrackedApp[]) {
    setTracker(next);
    saveLS(KEYS.tracker, next);
  }

  async function generate() {
    if (!jobTitle.trim()) return setError("Enter the job title.");
    const cvText = loadLS(KEYS.cvText, "");
    if (!cvText) return setError("No CV on file — add one in CV Studio first.");
    setBusy(true);
    setError("");
    setKit(null);
    try {
      const res = await fetch("/api/apply/kit", {
        method: "POST",
        headers: { "content-type": "application/json" },
        signal: AbortSignal.timeout(290_000),
        body: JSON.stringify({
          cvText,
          jobTitle: jobTitle.trim(),
          company: company.trim() || undefined,
          jobDescription: jobDescription.trim() || undefined,
        }),
      });
      const data = await res.json();
      if (!res.ok) return setError(data.error || "Generation failed.");
      setKit(data);
    } catch {
      setError("Network error — try again.");
    } finally {
      setBusy(false);
    }
  }

  function addManual() {
    if (!jobTitle.trim()) return setError("Enter a job title to track.");
    const t = jobTitle.trim();
    const c = company.trim() || "—";
    if (
      tracker.some(
        (x) => x.title.toLowerCase() === t.toLowerCase() && x.company.toLowerCase() === c.toLowerCase(),
      )
    )
      return setError("You're already tracking that application.");
    setError("");
    const next: TrackedApp[] = [
      {
        id: `manual-${Date.now()}`,
        title: t,
        company: c,
        url: "",
        status: "Applied" as const,
        notes: "",
        addedAt: new Date().toISOString(),
      },
      ...tracker,
    ];
    updateTracker(next);
  }

  return (
    <>
      <Nav />
      <div className="container">
        <h1 className="page-title">Apply Kit</h1>
        <p className="page-sub">
          Generate a tailored cover letter, pitch, screening answers and interview prep for each
          job — then track every application below.
        </p>

        {!hasCv && (
          <div className="notice">
            No CV on file yet — <Link href="/cv">add one in CV Studio</Link> so kits can be
            grounded in your real experience.
          </div>
        )}

        <div className="card anim">
          <div className="grid grid-2">
            <div>
              <label className="field">Job title *</label>
              <input
                type="text"
                placeholder="e.g. Senior Data Analyst"
                value={jobTitle}
                onChange={(e) => setJobTitle(e.target.value)}
              />
            </div>
            <div>
              <label className="field">Company (optional)</label>
              <input
                type="text"
                placeholder="e.g. Acme GmbH"
                value={company}
                onChange={(e) => setCompany(e.target.value)}
              />
            </div>
          </div>
          <label className="field">Job description (paste for best results)</label>
          <textarea
            rows={7}
            placeholder="Paste the full job posting here…"
            value={jobDescription}
            onChange={(e) => setJobDescription(e.target.value)}
          />
          {error && <div className="error">{error}</div>}
          <div style={{ display: "flex", gap: 10, marginTop: 16, flexWrap: "wrap" }}>
            <button className="btn" onClick={generate} disabled={busy}>
              {busy ? <span className="spinner" /> : <><Icon name="rocket" size={15} /> Generate application kit</>}
            </button>
            <button className="btn ghost" onClick={addManual}><Icon name="plus" size={15} /> Track this application</button>
          </div>
        </div>

        {kit && (
          <div style={{ display: "grid", gap: 16, marginTop: 16 }}>
            <div className="card">
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                <h3 className="section" style={{ margin: 0 }}><Icon name="mail" size={14} /> Cover letter</h3>
                <CopyBtn text={kit.coverLetter} />
              </div>
              <div style={{ color: "var(--muted)", fontSize: 13.5, margin: "8px 0" }}>
                Subject: <b style={{ color: "var(--text)" }}>{kit.subjectLine}</b>{" "}
                <CopyBtn text={kit.subjectLine} />
              </div>
              <div className="output">{kit.coverLetter}</div>
            </div>

            <div className="grid grid-2">
              <div className="card">
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                  <h3 className="section" style={{ margin: 0 }}><Icon name="target" size={14} /> Tailored pitch</h3>
                  <CopyBtn text={kit.tailoredPitch} />
                </div>
                <div className="output" style={{ marginTop: 10 }}>{kit.tailoredPitch}</div>
                <h3 className="section" style={{ marginTop: 18 }}><Icon name="message" size={14} /> Outreach message</h3>
                <div className="output">{kit.linkedinMessage}</div>
                <div style={{ marginTop: 8 }}><CopyBtn text={kit.linkedinMessage} /></div>
              </div>
              <div className="card">
                <h3 className="section"><Icon name="layers" size={14} /> CV bullets tuned for this job</h3>
                <ul className="clean">
                  {kit.bulletRewrites.map((b, i) => <li key={i}>{b}</li>)}
                </ul>
                <div style={{ marginTop: 8 }}><CopyBtn text={kit.bulletRewrites.join("\n")} /></div>
              </div>
            </div>

            <div className="grid grid-2">
              <div className="card">
                <h3 className="section"><Icon name="user" size={14} /> Screening answers</h3>
                {kit.answers.map((a, i) => (
                  <div key={i} style={{ marginBottom: 14 }}>
                    <b style={{ fontSize: 14 }}>{a.q}</b>
                    <div className="output" style={{ marginTop: 6 }}>{a.a}</div>
                  </div>
                ))}
              </div>
              <div className="card">
                <h3 className="section"><Icon name="bulb" size={14} /> Interview prep</h3>
                <ul className="clean">
                  {kit.interviewPrep.map((p, i) => <li key={i}>{p}</li>)}
                </ul>
              </div>
            </div>
          </div>
        )}

        <div className="card" style={{ marginTop: 16 }}>
          <h3 className="section">
            <Icon name="list" size={14} /> Application tracker{" "}
            {tracker.length > 0 && <span className="badge">{tracker.length}</span>}
          </h3>
          {tracker.length === 0 ? (
            <p style={{ color: "var(--muted)" }}>
              Nothing tracked yet — add jobs from <Link href="/jobs">Job Finder</Link> or the button above.
            </p>
          ) : (
            <div style={{ overflowX: "auto" }}>
              <table className="tracker">
                <thead>
                  <tr>
                    <th>Role</th><th>Company</th><th>Status</th><th>Added</th><th>Notes</th><th></th>
                  </tr>
                </thead>
                <tbody>
                  {tracker.map((t) => (
                    <tr key={t.id}>
                      <td>
                        {t.url ? (
                          <a href={t.url} target="_blank" rel="noopener noreferrer">{t.title} <Icon name="external" size={12} /></a>
                        ) : (
                          t.title
                        )}
                      </td>
                      <td>{t.company}</td>
                      <td>
                        <select
                          value={t.status}
                          onChange={(e) =>
                            updateTracker(
                              tracker.map((x) =>
                                x.id === t.id ? { ...x, status: e.target.value as TrackedApp["status"] } : x,
                              ),
                            )
                          }
                        >
                          {STATUSES.map((s) => <option key={s}>{s}</option>)}
                        </select>
                      </td>
                      <td style={{ whiteSpace: "nowrap", color: "var(--muted)" }}>
                        {new Date(t.addedAt).toLocaleDateString()}
                      </td>
                      <td style={{ minWidth: 160 }}>
                        <input
                          type="text"
                          placeholder="notes…"
                          value={t.notes}
                          onChange={(e) =>
                            updateTracker(
                              tracker.map((x) => (x.id === t.id ? { ...x, notes: e.target.value } : x)),
                            )
                          }
                        />
                      </td>
                      <td>
                        <button
                          className="btn ghost small"
                          onClick={() => updateTracker(tracker.filter((x) => x.id !== t.id))}
                        >
                          <Icon name="x" size={14} />
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </>
  );
}
