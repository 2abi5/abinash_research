import { NextRequest, NextResponse } from "next/server";
import type Anthropic from "@anthropic-ai/sdk";
import { MODEL, anthropic, apiErrorMessage, extractJson, responseText, stopReasonError } from "@/lib/anthropic";

export const runtime = "nodejs";
export const maxDuration = 300;

export type CvAnalysis = {
  atsScore: number;
  verdict: string;
  strengths: string[];
  gaps: string[];
  keywordsPresent: string[];
  keywordsMissing: string[];
  improvements: { section: string; advice: string }[];
  searchQueries: string[];
  cvPlainText?: string;
};

const SYSTEM = `You are an expert ATS (applicant tracking system) auditor, technical recruiter and CV coach.
You analyze CVs against target roles and job descriptions with brutal honesty and practical, specific advice.
Always respond with a single JSON object and nothing else — no prose before or after.`;

export async function POST(req: NextRequest) {
  let body: {
    cvText?: string;
    pdfBase64?: string;
    targetRole?: string;
    jobDescription?: string;
  };
  try {
    body = await req.json();
  } catch {
    return NextResponse.json({ error: "Bad request" }, { status: 400 });
  }

  const targetRole = (body.targetRole || "").trim();
  const cvText = (body.cvText || "").trim();
  const pdf = (body.pdfBase64 || "").trim();
  if (!targetRole) return NextResponse.json({ error: "Target role is required." }, { status: 400 });
  if (!cvText && !pdf)
    return NextResponse.json({ error: "Provide CV text or upload a PDF." }, { status: 400 });
  if (pdf.length > 4_300_000)
    return NextResponse.json({ error: "PDF too large — keep it under 3 MB." }, { status: 400 });

  const instruction = `Analyze the CV ${pdf ? "in the attached PDF" : "below"} for the target role: "${targetRole}".
${body.jobDescription ? `Specific job description to match against:\n"""\n${body.jobDescription.slice(0, 8000)}\n"""` : "No specific job description — evaluate against typical postings for that role."}

Return JSON with EXACTLY these keys:
{
  "atsScore": <integer 0-100, how well this CV would rank for the role>,
  "verdict": "<one blunt sentence summarizing the CV's current state>",
  "strengths": ["<3-6 strongest selling points>"],
  "gaps": ["<3-6 most damaging weaknesses or omissions>"],
  "keywordsPresent": ["<8-15 role-relevant keywords already in the CV>"],
  "keywordsMissing": ["<8-15 high-value keywords recruiters/ATS expect but the CV lacks>"],
  "improvements": [{"section": "<CV section>", "advice": "<specific, actionable rewrite advice>"}, ...4-8 items],
  "searchQueries": ["<4-6 short job-board search queries this candidate should run, best first>"]${
    pdf ? `,\n  "cvPlainText": "<the CV's full content extracted as clean plain text>"` : ""
  }
}`;

  const content: Anthropic.ContentBlockParam[] = [];
  if (pdf) {
    content.push({
      type: "document",
      source: { type: "base64", media_type: "application/pdf", data: pdf },
    });
  }
  content.push({
    type: "text",
    text: pdf ? instruction : `${instruction}\n\nCV:\n"""\n${cvText.slice(0, 24000)}\n"""`,
  });

  try {
    const msg = await anthropic().messages.create({
      model: MODEL,
      max_tokens: 8000,
      output_config: { effort: "low" },
      system: SYSTEM,
      messages: [{ role: "user", content }],
    });
    const stopErr = stopReasonError(msg);
    if (stopErr) return NextResponse.json({ error: stopErr }, { status: 502 });
    const parsed = extractJson<CvAnalysis>(responseText(msg));
    if (!parsed) return NextResponse.json({ error: "Could not parse analysis — try again." }, { status: 502 });
    return NextResponse.json(parsed);
  } catch (err) {
    return NextResponse.json({ error: apiErrorMessage(err) }, { status: 502 });
  }
}
