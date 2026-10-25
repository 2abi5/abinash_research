"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import Nav from "@/components/Nav";
import { KEYS, TrackedApp, loadLS } from "@/lib/storage";

export default function Dashboard() {
  const [stats, setStats] = useState({ hasCv: false, role: "", tracked: 0, applied: 0 });

  useEffect(() => {
    const tracker = loadLS<TrackedApp[]>(KEYS.tracker, []);
    setStats({
      hasCv: Boolean(loadLS(KEYS.cvText, "")),
      role: loadLS(KEYS.targetRole, ""),
      tracked: tracker.length,
      applied: tracker.filter((t) => t.status !== "Saved").length,
    });
  }, []);

  return (
    <>
      <Nav />
      <div className="container">
        <div className="hero">
          <h1>
            Land your next role, <em>on autopilot</em>.
          </h1>
          <p>
            Upload or paste your CV, let Claude optimize it for the role you want, find live
            openings that match your keywords, and generate ready-to-send application kits.
          </p>
        </div>

        <div className="grid grid-3" style={{ margin: "26px 0" }}>
          <Link href="/cv" className="card feature">
            <div className="emoji">📄</div>
            <h3>CV Studio</h3>
            <p>
              {stats.hasCv
                ? `CV on file${stats.role ? ` · targeting “${stats.role}”` : ""} — re-analyze or regenerate anytime.`
                : "Upload a PDF or paste your CV. Get an ATS score, keyword gaps and a rewritten, optimized CV."}
            </p>
          </Link>
          <Link href="/jobs" className="card feature">
            <div className="emoji">🔎</div>
            <h3>Job Finder</h3>
            <p>
              Search live openings on open job boards, scout the web with AI, and jump into
              pre-filled LinkedIn &amp; Indeed searches.
            </p>
          </Link>
          <Link href="/apply" className="card feature">
            <div className="emoji">🚀</div>
            <h3>Apply Kit</h3>
            <p>
              {stats.tracked > 0
                ? `${stats.tracked} tracked application${stats.tracked === 1 ? "" : "s"}, ${stats.applied} in motion.`
                : "Cover letter, tailored pitch, screening answers and interview prep — generated per job."}
            </p>
          </Link>
        </div>

        <div className="grid grid-2">
          <div className="card">
            <h3 className="section">How it works</h3>
            <div className="step"><span className="step-n">1</span><span><b>Feed it your CV</b> — paste text or upload the PDF in CV Studio, and set your target role.</span></div>
            <div className="step"><span className="step-n">2</span><span><b>Optimize</b> — Claude scores it against the role, finds missing keywords, and rewrites it ATS-friendly.</span></div>
            <div className="step"><span className="step-n">3</span><span><b>Hunt</b> — the suggested search queries flow straight into Job Finder's live boards and LinkedIn deep-links.</span></div>
            <div className="step"><span className="step-n">4</span><span><b>Apply</b> — for each opening, generate a tailored cover letter and answers, then track every application's status.</span></div>
          </div>
          <div className="card">
            <h3 className="section">Connect to Claude (MCP)</h3>
            <p style={{ color: "var(--muted)", fontSize: 14 }}>
              This site exposes its job-search tools as an MCP server. In the Claude app, go to{" "}
              <b>Settings → Connectors → Add custom connector</b> and point it at:
            </p>
            <div className="output mono" style={{ maxHeight: "none" }}>
              https://&lt;your-deployment&gt;.vercel.app/api/mcp
            </div>
            <p style={{ color: "var(--muted)", fontSize: 13.5, marginBottom: 0 }}>
              Claude can then run <b>search_jobs</b> and <b>job_board_links</b> for you in any chat.
              A note on LinkedIn: it has no public API and auto-submitting applications with bots
              violates its terms — CareerPilot keeps you safe with deep-links and one-click
              application kits you fire off yourself.
            </p>
          </div>
        </div>
      </div>
    </>
  );
}
