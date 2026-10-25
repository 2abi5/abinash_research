# ✈ CareerPilot

An AI job-search copilot powered by Claude. Upload or paste your CV, get an honest
ATS audit with keyword gaps, generate an optimized rewrite, search live job openings,
scout the web with AI, and produce ready-to-send application kits — cover letter,
tailored pitch, screening answers, LinkedIn message and interview prep — for every
job you chase. Includes a built-in application tracker and an MCP server endpoint
so Claude itself can use your job-search tools.

## Features

| Area | What it does |
|---|---|
| **CV Studio** | PDF upload (parsed natively by Claude) or pasted text → ATS score, strengths/gaps, keywords present/missing, section-by-section fixes, suggested job-search queries, and a full ATS-friendly Markdown rewrite (downloadable). |
| **Job Finder** | Live listings from open job boards (Remotive, Arbeitnow), an AI web scout (Claude + web search tool) that finds current openings, and pre-filled deep links into LinkedIn Jobs, Indeed, Glassdoor, Google Jobs, Wellfound and RemoteOK. |
| **Apply Kit** | Per-job cover letter, email subject, 60–90 word pitch, retargeted CV bullets, screening-question answers, LinkedIn outreach message and interview prep — all grounded in your real CV (no invented experience). |
| **Tracker** | Save jobs from any search, track status (Saved → Applied → Interview → Offer/Rejected) with notes. Stored in your browser. |
| **MCP server** | `/api/mcp` exposes `search_jobs` and `job_board_links` tools over Streamable HTTP — add it to Claude as a custom connector. |
| **Login gate** | The whole site (and the Claude API spend behind it) sits behind a username/password you configure via environment variables. |

> **A note on LinkedIn:** LinkedIn has no public API for job search or applications,
> and bots that log in and auto-submit applications violate its User Agreement (and
> get accounts restricted). CareerPilot does the legitimate version: deep-linked
> searches, AI-scouted openings, and one-click application kits that make *you*
> the fastest applicant in the pipeline.

## Stack

Next.js 15 (App Router, TypeScript) · Anthropic SDK (Claude Opus 5.5 by default) ·
`mcp-handler` (MCP SDK v2) · zero database (browser localStorage) · no UI framework,
hand-rolled design system with dark/light support.

## Environment variables

| Variable | Required | Purpose |
|---|---|---|
| `ANTHROPIC_API_KEY` | ✅ | Claude API key (server-side only). |
| `AUTH_USERNAME` | ✅ | Login username. Logins are refused until both are set. |
| `AUTH_PASSWORD` | ✅ | Login password. |
| `AUTH_SECRET` | recommended | Random string for signing session cookies (`openssl rand -hex 32`). |
| `CLAUDE_MODEL` | optional | Defaults to `claude-opus-5-5`. |
| `MCP_TOKEN` | optional | If set, `/api/mcp` requires `Authorization: Bearer <token>`. |

Secrets live **only** in env vars — never commit them. `.env*` is gitignored.

## Run locally

```bash
cd careerpilot
npm install
cp .env.example .env.local   # then fill in real values
npm run dev                  # http://localhost:3000
```

## Deploy to Vercel (permanent, free Hobby tier)

1. Go to **[vercel.com/new](https://vercel.com/new)** and sign in with GitHub.
2. Import this repository (`2abi5/abinash_research`).
3. **Set “Root Directory” to `careerpilot`** (Edit → select the folder). Framework
   auto-detects as Next.js — leave build settings alone.
4. Under **Environment Variables**, add `ANTHROPIC_API_KEY`, `AUTH_USERNAME`,
   `AUTH_PASSWORD` and `AUTH_SECRET` (all for Production, Preview and Development).
5. Click **Deploy**. You get a permanent `https://<project>.vercel.app` URL; every
   push to the connected branch redeploys automatically. Add a custom domain under
   Project → Settings → Domains if you want one.

### Connect it to Claude (MCP)

Once deployed: Claude app → **Settings → Connectors → Add custom connector** → URL
`https://<project>.vercel.app/api/mcp`. If you set `MCP_TOKEN`, configure the same
bearer token on the client. Claude can then search jobs and build board links for
you inside any conversation.

## Security notes

- The Claude API key is used only in server routes; it never reaches the browser.
- All pages and AI routes are behind the login cookie (HMAC-signed, httpOnly, 7-day
  expiry) — so strangers can't burn your API credits.
- Login endpoint has basic per-IP rate limiting.
- If an API key is ever pasted in a chat, screenshot or commit, **rotate it** at
  [console.anthropic.com → API keys](https://console.anthropic.com/settings/keys).
