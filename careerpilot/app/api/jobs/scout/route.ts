import { NextRequest, NextResponse } from "next/server";
import type Anthropic from "@anthropic-ai/sdk";
import { MODEL, anthropic, apiErrorMessage, extractJson, responseText, stopReasonError } from "@/lib/anthropic";

export const runtime = "nodejs";
export const maxDuration = 300;

export type ScoutResult = {
  findings: { title: string; company: string; location: string; url: string; note: string }[];
  summary: string;
};

const SYSTEM = `You are a job-market scout. You search the live web for current, real job openings.
Only report openings you actually found in search results, with their real URLs — never invent listings.
Finish with a single JSON object and nothing else after it.`;

export async function POST(req: NextRequest) {
  let body: { role?: string; location?: string; extras?: string };
  try {
    body = await req.json();
  } catch {
    return NextResponse.json({ error: "Bad request" }, { status: 400 });
  }
  const role = (body.role || "").trim();
  if (!role) return NextResponse.json({ error: "Role is required." }, { status: 400 });

  const locationRule = body.location
    ? `STRICT location rule: report ONLY openings located in "${body.location}" or explicitly remote-open to candidates based there. Discard every posting in any other country or region, however good the match.`
    : "Any location is fine; prefer remote-friendly roles.";

  const prompt = `Find current job openings for: "${role}"${body.location ? ` in or near "${body.location}"` : ""}.
${locationRule}
${body.extras ? `Candidate context to prioritize matches: ${body.extras.slice(0, 1500)}` : ""}

Use web search (job boards, company career pages, "hiring" posts). Prefer postings from the last 30 days.

Then output JSON with EXACTLY these keys:
{
  "findings": [{"title": "...", "company": "...", "location": "...", "url": "<the actual URL from search results>", "note": "<one line: why it fits / key requirement>"}, ... up to 10],
  "summary": "<2-3 sentences on the current market for this role: demand, common requirements, salary signals if seen>"
}`;

  try {
    const client = anthropic();
    const tools = [
      { type: "web_search_20260209", name: "web_search", max_uses: 4 } as Anthropic.ToolUnion,
    ];
    const messages: Anthropic.MessageParam[] = [{ role: "user", content: prompt }];
    const params = {
      model: MODEL,
      max_tokens: 8000,
      output_config: { effort: "low" as const },
      system: SYSTEM,
      tools,
    };
    let msg = await client.messages.create({ ...params, messages });
    // A long web-search turn can pause; continue it (bounded) until it finishes.
    for (let i = 0; i < 3 && msg.stop_reason === "pause_turn"; i++) {
      messages.push({ role: "assistant", content: msg.content });
      msg = await client.messages.create({ ...params, messages });
    }
    const stopErr = stopReasonError(msg);
    if (stopErr) return NextResponse.json({ error: stopErr }, { status: 502 });
    const parsed = extractJson<ScoutResult>(responseText(msg));
    if (!parsed?.findings)
      return NextResponse.json({ error: "Scout came back empty — try a broader role." }, { status: 502 });
    return NextResponse.json(parsed);
  } catch (err) {
    return NextResponse.json({ error: apiErrorMessage(err) }, { status: 502 });
  }
}
