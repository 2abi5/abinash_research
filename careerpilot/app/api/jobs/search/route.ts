import { NextRequest, NextResponse } from "next/server";
import { deepLinks, searchJobs } from "@/lib/jobs";

export const runtime = "nodejs";
export const maxDuration = 30;

export async function POST(req: NextRequest) {
  let body: { query?: string; location?: string };
  try {
    body = await req.json();
  } catch {
    return NextResponse.json({ error: "Bad request" }, { status: 400 });
  }
  const query = (body.query || "").trim();
  if (!query) return NextResponse.json({ error: "Enter a search query." }, { status: 400 });

  const location = body.location?.trim() || undefined;
  const { jobs, errors, note } = await searchJobs(query, location);
  return NextResponse.json({
    jobs,
    links: deepLinks(query, location),
    errors,
    note,
  });
}
