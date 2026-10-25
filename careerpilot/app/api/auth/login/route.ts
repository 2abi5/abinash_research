import { NextRequest, NextResponse } from "next/server";
import {
  SESSION_COOKIE,
  SESSION_MAX_AGE,
  authConfigured,
  checkCredentials,
  createSessionToken,
} from "@/lib/auth";

export const runtime = "nodejs";

// Tiny in-memory rate limit (per serverless instance) to slow brute force.
const attempts = new Map<string, { n: number; t: number }>();

export async function POST(req: NextRequest) {
  const ip = req.headers.get("x-forwarded-for")?.split(",")[0]?.trim() || "unknown";
  const now = Date.now();
  const a = attempts.get(ip);
  if (a && now - a.t < 60_000 && a.n >= 8) {
    return NextResponse.json({ error: "Too many attempts — wait a minute." }, { status: 429 });
  }

  let body: { username?: string; password?: string };
  try {
    body = await req.json();
  } catch {
    return NextResponse.json({ error: "Bad request" }, { status: 400 });
  }

  const ok = await checkCredentials(String(body.username ?? ""), String(body.password ?? ""));
  if (!ok) {
    attempts.set(ip, { n: (a && now - a.t < 60_000 ? a.n : 0) + 1, t: now });
    return NextResponse.json(
      {
        error: authConfigured()
          ? "Wrong username or password."
          : "Login is not configured — set the AUTH_USERNAME, AUTH_PASSWORD and AUTH_SECRET environment variables, then redeploy.",
      },
      { status: 401 },
    );
  }

  attempts.delete(ip);
  const token = await createSessionToken(String(body.username));
  const res = NextResponse.json({ ok: true });
  res.cookies.set(SESSION_COOKIE, token, {
    httpOnly: true,
    secure: process.env.NODE_ENV === "production",
    sameSite: "lax",
    path: "/",
    maxAge: SESSION_MAX_AGE,
  });
  return res;
}
