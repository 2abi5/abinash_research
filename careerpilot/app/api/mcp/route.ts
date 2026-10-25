// MCP server endpoint — connect this site to Claude (claude.ai → Settings →
// Connectors → Add custom connector) or any MCP client, using the URL
// https://<your-deployment>/api/mcp
// If MCP_TOKEN is set, clients must send "Authorization: Bearer <token>".
import { createMcpHandler } from "mcp-handler";
import { z } from "zod";
import { deepLinks, searchJobs } from "@/lib/jobs";

export const runtime = "nodejs";
export const maxDuration = 60;

const handler = createMcpHandler((server) => {
  server.registerTool(
    "search_jobs",
    {
      title: "Search job openings",
      description:
        "Search live job openings across open job boards (Remotive, Arbeitnow) by keyword. " +
        "Returns title, company, location and application URL for each match. " +
        "Pass location to strictly filter to a country/region.",
      inputSchema: z.object({
        query: z.string().min(2).describe("Keywords, e.g. 'machine learning engineer'"),
        location: z.string().optional().describe("Strict location filter, e.g. 'USA' or 'Germany'"),
      }),
    },
    async ({ query, location }) => {
      const { jobs, errors, note } = await searchJobs(query, location);
      const lines = jobs
        .slice(0, 15)
        .map(
          (j, i) =>
            `${i + 1}. ${j.title} — ${j.company} (${j.location}) [${j.source}]\n   Apply: ${j.url}`,
        );
      const text =
        (lines.length ? lines.join("\n") : "No matches on the open boards right now.") +
        (note ? `\n\n${note}` : "") +
        (errors.length ? `\n\nNote: ${errors.join(", ")}.` : "");
      return { content: [{ type: "text", text }] };
    },
  );

  server.registerTool(
    "job_board_links",
    {
      title: "Job board search links",
      description:
        "Build pre-filled search URLs for LinkedIn Jobs, Indeed, Glassdoor, Google Jobs, " +
        "Wellfound and RemoteOK for a given query and optional location.",
      inputSchema: z.object({
        query: z.string().min(2).describe("Keywords, e.g. 'data analyst'"),
        location: z.string().optional().describe("City/country, e.g. 'Kathmandu' or 'Remote'"),
      }),
    },
    async ({ query, location }) => {
      const text = deepLinks(query, location)
        .map((l) => `- ${l.board}: ${l.url}`)
        .join("\n");
      return { content: [{ type: "text", text }] };
    },
  );
});

function authorized(req: Request): boolean {
  const token = process.env.MCP_TOKEN;
  if (!token) return true; // open endpoint when no token configured
  return req.headers.get("authorization") === `Bearer ${token}`;
}

function guard(req: Request): Promise<Response> {
  if (!authorized(req)) {
    return Promise.resolve(
      new Response(JSON.stringify({ error: "Unauthorized" }), {
        status: 401,
        headers: { "content-type": "application/json" },
      }),
    );
  }
  return handler(req);
}

export { guard as GET, guard as POST, guard as DELETE };
