import { NextRequest, NextResponse } from "next/server";
import { MODEL, anthropic, apiErrorMessage, extractJson, responseText } from "@/lib/anthropic";

export const runtime = "nodejs";
export const maxDuration = 300;

const SYSTEM = `You are a professional CV writer. You turn rough notes about a person's background
into a polished, ATS-friendly CV. Use ONLY the facts provided — never invent employers, dates,
degrees, metrics or certifications. You may phrase things professionally, organize them well, and
write strong achievement-style bullets from what is given. Respond with a single JSON object and
nothing else.`;

export async function POST(req: NextRequest) {
  let body: {
    name?: string;
    contact?: string;
    targetRole?: string;
    education?: string;
    experience?: string;
    projects?: string;
    skills?: string;
    extras?: string;
  };
  try {
    body = await req.json();
  } catch {
    return NextResponse.json({ error: "Bad request" }, { status: 400 });
  }

  const name = (body.name || "").trim();
  const targetRole = (body.targetRole || "").trim();
  const experience = (body.experience || "").trim();
  const education = (body.education || "").trim();
  if (!name) return NextResponse.json({ error: "Your name is required." }, { status: 400 });
  if (!targetRole) return NextResponse.json({ error: "Target role is required." }, { status: 400 });
  if (!experience && !education)
    return NextResponse.json(
      { error: "Add at least some experience or education to build from." },
      { status: 400 },
    );

  const clip = (s?: string) => (s || "").trim().slice(0, 6000);

  const prompt = `Build a complete, ATS-friendly CV in clean Markdown for this person, targeting the role: "${targetRole}".

Name: ${name}
Contact line: ${clip(body.contact) || "(not provided — omit)"}
Education (rough notes):
${clip(education) || "(none provided)"}
Work / research experience (rough notes):
${clip(experience) || "(none provided)"}
Projects (rough notes):
${clip(body.projects) || "(none provided)"}
Skills (rough notes):
${clip(body.skills) || "(none provided)"}
Extras — certifications, awards, languages, volunteering (rough notes):
${clip(body.extras) || "(none provided)"}

Markdown layout: # Name · contact line · ## Professional Summary (3-4 lines selling them for the
target role, grounded in the facts) · ## Core Skills (grouped) · ## Experience (reverse-chronological,
strong action-verb bullets built from their notes) · ## Projects (if any) · ## Education · ## Extras (if any).
Skip any section with no content. Do not pad with invented details.

Return JSON with EXACTLY these keys:
{
  "markdown": "<the complete CV in Markdown>",
  "tips": ["<4-7 short bullets: what this CV still needs from the candidate to be stronger (e.g. metrics to dig up, certs worth adding), specific to them>"]
}`;

  try {
    const msg = await anthropic().messages.create({
      model: MODEL,
      max_tokens: 10000,
      output_config: { effort: "low" },
      system: SYSTEM,
      messages: [{ role: "user", content: prompt }],
    });
    const parsed = extractJson<{ markdown: string; tips: string[] }>(responseText(msg));
    if (!parsed?.markdown)
      return NextResponse.json({ error: "Could not build the CV — try again." }, { status: 502 });
    return NextResponse.json(parsed);
  } catch (err) {
    return NextResponse.json({ error: apiErrorMessage(err) }, { status: 502 });
  }
}
