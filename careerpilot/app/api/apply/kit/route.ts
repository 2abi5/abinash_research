import { NextRequest, NextResponse } from "next/server";
import { MODEL, anthropic, apiErrorMessage, extractJson, responseText } from "@/lib/anthropic";

export const runtime = "nodejs";
export const maxDuration = 60;

export type ApplyKit = {
  coverLetter: string;
  subjectLine: string;
  tailoredPitch: string;
  bulletRewrites: string[];
  answers: { q: string; a: string }[];
  linkedinMessage: string;
  interviewPrep: string[];
};

const SYSTEM = `You are an elite career coach who writes application materials that are specific,
confident and human — never generic AI-sounding fluff. Ground every claim in the candidate's real CV;
never invent experience. Respond with a single JSON object and nothing else.`;

export async function POST(req: NextRequest) {
  let body: {
    cvText?: string;
    jobTitle?: string;
    company?: string;
    jobDescription?: string;
  };
  try {
    body = await req.json();
  } catch {
    return NextResponse.json({ error: "Bad request" }, { status: 400 });
  }

  const cvText = (body.cvText || "").trim();
  const jobTitle = (body.jobTitle || "").trim();
  if (!cvText) return NextResponse.json({ error: "No CV on file — build one in CV Studio first." }, { status: 400 });
  if (!jobTitle) return NextResponse.json({ error: "Job title is required." }, { status: 400 });

  const prompt = `Create a complete application kit for this candidate.

Position: "${jobTitle}"${body.company ? ` at ${body.company}` : ""}
${body.jobDescription ? `Job description:\n"""\n${body.jobDescription.slice(0, 8000)}\n"""` : "No job description provided — infer typical requirements for the role."}

Candidate CV:
"""
${cvText.slice(0, 24000)}
"""

Return JSON with EXACTLY these keys:
{
  "coverLetter": "<complete, ready-to-send cover letter, 250-350 words, specific to this role and the candidate's real experience>",
  "subjectLine": "<email subject line for the application>",
  "tailoredPitch": "<60-90 word 'about me' pitch tailored to this job, usable in application forms>",
  "bulletRewrites": ["<4-6 CV bullets from the candidate's experience, rewritten to target this job's requirements>"],
  "answers": [{"q": "<common application/screening question for this role>", "a": "<strong tailored answer, 50-120 words>"}, ...4 items: include 'Why this company?', 'Why are you a good fit?', one role-specific technical/behavioral question, and salary-expectations guidance],
  "linkedinMessage": "<short, polite LinkedIn message (under 300 characters) to the hiring manager or recruiter about this opening>",
  "interviewPrep": ["<5 likely interview questions for this specific role, with a one-line hint on how this candidate should angle each answer>"]
}`;

  try {
    const msg = await anthropic().messages.create({
      model: MODEL,
      max_tokens: 8000,
      output_config: { effort: "low" },
      system: SYSTEM,
      messages: [{ role: "user", content: prompt }],
    });
    const parsed = extractJson<ApplyKit>(responseText(msg));
    if (!parsed?.coverLetter)
      return NextResponse.json({ error: "Could not parse kit — try again." }, { status: 502 });
    return NextResponse.json(parsed);
  } catch (err) {
    return NextResponse.json({ error: apiErrorMessage(err) }, { status: 502 });
  }
}
