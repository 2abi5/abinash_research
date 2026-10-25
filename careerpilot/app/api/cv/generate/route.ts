import { NextRequest, NextResponse } from "next/server";
import { MODEL, anthropic, apiErrorMessage, extractJson, responseText } from "@/lib/anthropic";

export const runtime = "nodejs";
export const maxDuration = 300;

const SYSTEM = `You are a professional CV writer who produces clean, ATS-friendly, achievement-driven CVs.
Rules: never invent employers, dates, degrees or certifications; you may only rephrase, reorganize,
quantify where the source gives numbers, and sharpen wording. Strong action verbs, measurable impact,
concise bullets. Respond with a single JSON object and nothing else.`;

export async function POST(req: NextRequest) {
  let body: {
    cvText?: string;
    targetRole?: string;
    jobDescription?: string;
    keywordsMissing?: string[];
  };
  try {
    body = await req.json();
  } catch {
    return NextResponse.json({ error: "Bad request" }, { status: 400 });
  }

  const cvText = (body.cvText || "").trim();
  const targetRole = (body.targetRole || "").trim();
  if (!cvText || !targetRole)
    return NextResponse.json({ error: "CV text and target role are required." }, { status: 400 });

  const prompt = `Rewrite the CV below as an optimized, ATS-friendly CV in clean Markdown, targeting the role: "${targetRole}".
${body.jobDescription ? `Tailor it to this job description:\n"""\n${body.jobDescription.slice(0, 8000)}\n"""` : ""}
${
  body.keywordsMissing?.length
    ? `Where truthfully supported by the candidate's experience, naturally work in these missing keywords: ${body.keywordsMissing
        .slice(0, 15)
        .join(", ")}. Never fabricate experience to force a keyword.`
    : ""
}

Markdown layout: # Name · contact line · ## Professional Summary · ## Core Skills (grouped) ·
## Experience (reverse-chronological, 3-5 impact bullets each) · ## Projects (if any) · ## Education · ## Extras (if any).

Return JSON with EXACTLY these keys:
{
  "markdown": "<the complete optimized CV in Markdown>",
  "changeNotes": ["<5-10 bullets explaining the most important changes you made and why>"]
}

CV source:
"""
${cvText.slice(0, 24000)}
"""`;

  try {
    const msg = await anthropic().messages.create({
      model: MODEL,
      max_tokens: 10000,
      output_config: { effort: "low" },
      system: SYSTEM,
      messages: [{ role: "user", content: prompt }],
    });
    const parsed = extractJson<{ markdown: string; changeNotes: string[] }>(responseText(msg));
    if (!parsed?.markdown)
      return NextResponse.json({ error: "Could not parse generated CV — try again." }, { status: 502 });
    return NextResponse.json(parsed);
  } catch (err) {
    return NextResponse.json({ error: apiErrorMessage(err) }, { status: 502 });
  }
}
