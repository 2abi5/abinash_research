"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import Nav from "@/components/Nav";
import Icon from "@/components/Icon";
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
        <div className="hero anim">
          <span className="eyebrow">
            <Icon name="sparkles" size={13} /> Your AI job-search copilot
          </span>
          <h1>
            Land your next role, <em>on autopilot</em>.
          </h1>
          <p>
            Perfect your CV, find openings that actually match it, and walk into every
            application with tailored materials already written.
          </p>
          <div className="stat-row">
            <span className="stat">
              <Icon name="file" size={15} />
              {stats.hasCv ? <>CV <b>on file</b></> : <>CV <b>not added yet</b></>}
            </span>
            {stats.role && (
              <span className="stat">
                <Icon name="target" size={15} />
                Targeting <b>{stats.role}</b>
              </span>
            )}
            <span className="stat">
              <Icon name="list" size={15} />
              <b>{stats.tracked}</b>&nbsp;tracked
            </span>
            <span className="stat">
              <Icon name="rocket" size={15} />
              <b>{stats.applied}</b>&nbsp;in motion
            </span>
          </div>
        </div>

        <div className="grid grid-3 anim" style={{ margin: "30px 0 18px" }}>
          <Link href="/cv" className="card feature">
            <div className="feature-icon"><Icon name="file" size={20} /></div>
            <h3>CV Studio</h3>
            <p>
              Upload or paste your CV, get a brutal ATS audit with the exact keywords
              you&apos;re missing, then generate a polished rewrite.
            </p>
            <span className="go">Open <Icon name="external" size={13} /></span>
          </Link>
          <Link href="/jobs" className="card feature">
            <div className="feature-icon"><Icon name="search" size={20} /></div>
            <h3>Job Finder</h3>
            <p>
              Live openings from job boards, an AI scout that searches the web for you,
              and one-click searches on LinkedIn, Indeed and more.
            </p>
            <span className="go">Open <Icon name="external" size={13} /></span>
          </Link>
          <Link href="/apply" className="card feature">
            <div className="feature-icon"><Icon name="rocket" size={20} /></div>
            <h3>Apply Kit</h3>
            <p>
              Cover letter, pitch, screening answers and interview prep — written for each
              specific job. Track every application in one place.
            </p>
            <span className="go">Open <Icon name="external" size={13} /></span>
          </Link>
        </div>

        <div className="grid grid-2 anim">
          <div className="card">
            <h3 className="section"><Icon name="gauge" size={14} /> How it works</h3>
            <div className="step"><span className="step-n">1</span><span><b>Add your CV</b> in CV Studio — upload the PDF or paste the text, and set the role you want.</span></div>
            <div className="step"><span className="step-n">2</span><span><b>Optimize it</b> — you get a score, the keywords recruiters filter for, and a clean rewritten CV.</span></div>
            <div className="step"><span className="step-n">3</span><span><b>Find openings</b> — your suggested searches flow straight into Job Finder&apos;s live boards and the big job sites.</span></div>
            <div className="step"><span className="step-n">4</span><span><b>Apply fast</b> — generate a tailored kit per job, send it, and track where every application stands.</span></div>
          </div>
          <div className="card">
            <h3 className="section"><Icon name="bulb" size={14} /> Pro tips</h3>
            <div className="step"><span className="step-n"><Icon name="check" size={13} /></span><span><b>Apply early.</b> Applications in the first 48 hours of a posting get seen far more often — the AI scout favors fresh listings.</span></div>
            <div className="step"><span className="step-n"><Icon name="check" size={13} /></span><span><b>Tailor every time.</b> Paste the job description into CV Studio and Apply Kit — generic applications lose to tailored ones.</span></div>
            <div className="step"><span className="step-n"><Icon name="check" size={13} /></span><span><b>Message a human.</b> Each kit includes a short outreach note — send it to the recruiter or hiring manager after you apply.</span></div>
            <div className="step"><span className="step-n"><Icon name="check" size={13} /></span><span><b>Track and follow up.</b> No reply in a week? A polite follow-up doubles your response odds.</span></div>
          </div>
        </div>
      </div>
    </>
  );
}
