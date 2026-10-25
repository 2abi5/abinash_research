// Session auth shared by the login route and the middleware.
// Works in both Node and Edge runtimes (Web Crypto only).

const encoder = new TextEncoder();

function getSecret(): string {
  return (
    process.env.AUTH_SECRET ||
    // Fallback: derive a signing secret from the credentials themselves so the
    // app still works when AUTH_SECRET is unset. Setting AUTH_SECRET is better.
    `cp::${process.env.AUTH_USERNAME || ""}::${process.env.AUTH_PASSWORD || ""}`
  );
}

async function hmacHex(message: string): Promise<string> {
  const key = await crypto.subtle.importKey(
    "raw",
    encoder.encode(getSecret()),
    { name: "HMAC", hash: "SHA-256" },
    false,
    ["sign"],
  );
  const sig = await crypto.subtle.sign("HMAC", key, encoder.encode(message));
  return Array.from(new Uint8Array(sig))
    .map((b) => b.toString(16).padStart(2, "0"))
    .join("");
}

export const SESSION_COOKIE = "cp_session";
export const SESSION_MAX_AGE = 60 * 60 * 24 * 7; // 7 days

/** Create a signed session token: base64url(user|exp) + "." + hmac */
export async function createSessionToken(username: string): Promise<string> {
  const exp = Date.now() + SESSION_MAX_AGE * 1000;
  const payload = `${username}|${exp}`;
  const b64 = btoa(payload).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
  const sig = await hmacHex(payload);
  return `${b64}.${sig}`;
}

/** Verify a session token; returns the username or null. */
export async function verifySessionToken(token: string | undefined): Promise<string | null> {
  if (!token) return null;
  const [b64, sig] = token.split(".");
  if (!b64 || !sig) return null;
  let payload: string;
  try {
    payload = atob(b64.replace(/-/g, "+").replace(/_/g, "/"));
  } catch {
    return null;
  }
  const expected = await hmacHex(payload);
  if (sig.length !== expected.length) return null;
  // constant-time-ish compare
  let diff = 0;
  for (let i = 0; i < expected.length; i++) diff |= sig.charCodeAt(i) ^ expected.charCodeAt(i);
  if (diff !== 0) return null;
  const [username, expStr] = payload.split("|");
  if (!username || !expStr || Date.now() > Number(expStr)) return null;
  return username;
}

/** Check submitted credentials against the environment configuration. */
export async function checkCredentials(username: string, password: string): Promise<boolean> {
  const envUser = process.env.AUTH_USERNAME;
  const envPass = process.env.AUTH_PASSWORD;
  if (!envUser || !envPass) return false; // refuse logins when not configured
  const a = await hmacHex(`cred|${username}|${password}`);
  const b = await hmacHex(`cred|${envUser}|${envPass}`);
  let diff = 0;
  for (let i = 0; i < b.length; i++) diff |= a.charCodeAt(i) ^ b.charCodeAt(i);
  return a.length === b.length && diff === 0;
}
