// Live job listings from open, no-key job boards + deep links to the big boards.
// Remotive and Arbeitnow are free public APIs. LinkedIn/Indeed/etc. have no
// public search API, so we generate pre-filled search deep links instead.

export type Job = {
  id: string;
  title: string;
  company: string;
  location: string;
  url: string;
  source: "Remotive" | "Arbeitnow";
  tags: string[];
  publishedAt: string | null;
  salary: string | null;
};

export type DeepLink = { board: string; url: string };

const FETCH_TIMEOUT_MS = 9000;

async function fetchJson(url: string): Promise<unknown> {
  const res = await fetch(url, {
    signal: AbortSignal.timeout(FETCH_TIMEOUT_MS),
    headers: { accept: "application/json", "user-agent": "CareerPilot/1.0" },
    // job listings change constantly; don't let Next cache them
    cache: "no-store",
  });
  if (!res.ok) throw new Error(`${url} → HTTP ${res.status}`);
  return res.json();
}

function stripHtml(s: string): string {
  return s.replace(/<[^>]+>/g, " ").replace(/\s+/g, " ").trim();
}

async function searchRemotive(query: string): Promise<Job[]> {
  type R = {
    jobs?: Array<{
      id: number;
      title: string;
      company_name: string;
      candidate_required_location: string;
      url: string;
      tags?: string[];
      publication_date?: string;
      salary?: string;
    }>;
  };
  const data = (await fetchJson(
    `https://remotive.com/api/remote-jobs?search=${encodeURIComponent(query)}&limit=40`,
  )) as R;
  return (data.jobs ?? []).map((j) => ({
    id: `remotive-${j.id}`,
    title: j.title,
    company: j.company_name,
    location: j.candidate_required_location || "Remote",
    url: j.url,
    source: "Remotive" as const,
    tags: (j.tags ?? []).slice(0, 6),
    publishedAt: j.publication_date ?? null,
    salary: j.salary || null,
  }));
}

async function searchArbeitnow(query: string): Promise<Job[]> {
  type A = {
    data?: Array<{
      slug: string;
      title: string;
      company_name: string;
      location: string;
      url: string;
      tags?: string[];
      created_at?: number;
      remote?: boolean;
      description?: string;
    }>;
  };
  const q = query.toLowerCase();
  const terms = q.split(/[\s,/]+/).filter((t) => t.length > 1);
  const pages = await Promise.allSettled(
    [1, 2].map((p) => fetchJson(`https://www.arbeitnow.com/api/job-board-api?page=${p}`) as Promise<A>),
  );
  if (pages.every((p) => p.status === "rejected")) throw new Error("Arbeitnow unreachable");
  const rows = pages.flatMap((p) => (p.status === "fulfilled" ? (p.value.data ?? []) : []));
  return rows
    .filter((j) => {
      const hay = `${j.title} ${j.company_name} ${(j.tags ?? []).join(" ")} ${stripHtml(
        j.description ?? "",
      ).slice(0, 400)}`.toLowerCase();
      return terms.length === 0 || terms.some((t) => hay.includes(t));
    })
    .map((j) => ({
      id: `arbeitnow-${j.slug}`,
      title: j.title,
      company: j.company_name,
      location: j.remote ? `${j.location || "—"} (Remote)` : j.location || "—",
      url: j.url,
      source: "Arbeitnow" as const,
      tags: (j.tags ?? []).slice(0, 6),
      publishedAt: j.created_at ? new Date(j.created_at * 1000).toISOString() : null,
      salary: null,
    }));
}

/** Rank jobs by keyword overlap with the query, newest first as tiebreaker. */
function rank(jobs: Job[], query: string): Job[] {
  const terms = query.toLowerCase().split(/[\s,/]+/).filter((t) => t.length > 1);
  const score = (j: Job) => {
    const title = j.title.toLowerCase();
    const hay = `${title} ${j.tags.join(" ").toLowerCase()}`;
    let s = 0;
    for (const t of terms) {
      if (title.includes(t)) s += 3;
      else if (hay.includes(t)) s += 1;
    }
    return s;
  };
  return jobs
    .map((j) => ({ j, s: score(j), d: j.publishedAt ? Date.parse(j.publishedAt) : 0 }))
    .sort((a, b) => b.s - a.s || b.d - a.d)
    .map((x) => x.j);
}

export async function searchJobs(
  query: string,
): Promise<{ jobs: Job[]; errors: string[] }> {
  const results = await Promise.allSettled([searchRemotive(query), searchArbeitnow(query)]);
  const jobs: Job[] = [];
  const errors: string[] = [];
  const names = ["Remotive", "Arbeitnow"];
  results.forEach((r, i) => {
    if (r.status === "fulfilled") jobs.push(...r.value);
    else errors.push(`${names[i]} unavailable`);
  });
  return { jobs: rank(jobs, query).slice(0, 50), errors };
}

/** Pre-filled search links for boards without a public API. */
export function deepLinks(query: string, location?: string): DeepLink[] {
  const q = encodeURIComponent(query);
  const loc = encodeURIComponent(location || "");
  return [
    {
      board: "LinkedIn Jobs",
      url: `https://www.linkedin.com/jobs/search/?keywords=${q}${loc ? `&location=${loc}` : ""}&f_TPR=r604800`,
    },
    { board: "Indeed", url: `https://www.indeed.com/jobs?q=${q}${loc ? `&l=${loc}` : ""}` },
    { board: "Glassdoor", url: `https://www.glassdoor.com/Job/jobs.htm?sc.keyword=${q}` },
    { board: "Google Jobs", url: `https://www.google.com/search?q=${q}+jobs${loc ? `+in+${loc}` : ""}&ibp=htl;jobs` },
    { board: "Wellfound (startups)", url: `https://wellfound.com/jobs?keywords=${q}` },
    { board: "RemoteOK", url: `https://remoteok.com/remote-${query.trim().toLowerCase().replace(/\s+/g, "-")}-jobs` },
  ];
}
