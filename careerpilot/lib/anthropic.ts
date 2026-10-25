import Anthropic from "@anthropic-ai/sdk";

export const MODEL = process.env.CLAUDE_MODEL || "claude-opus-5-5";

let _client: Anthropic | null = null;

export function anthropic(): Anthropic {
  const key = process.env.ANTHROPIC_API_KEY?.trim();
  if (!key) {
    throw new Error(
      "ANTHROPIC_API_KEY is not set. Add it in Vercel → Project → Settings → Environment Variables.",
    );
  }
  // Catch masked copies ("sk-ant-usr-1bQA•••") pasted from UIs that hide keys.
  if (!/^[\x21-\x7e]+$/.test(key)) {
    throw new Error(
      "ANTHROPIC_API_KEY contains invalid characters (looks like a masked '•••' copy). " +
        "Re-paste the FULL key in Vercel → Settings → Environment Variables, then redeploy.",
    );
  }
  if (!_client) _client = new Anthropic({ apiKey: key });
  return _client;
}

/** Extract the concatenated text blocks from a Messages API response. */
export function responseText(response: Anthropic.Message): string {
  return response.content
    .filter((b): b is Anthropic.TextBlock => b.type === "text")
    .map((b) => b.text)
    .join("\n");
}

/**
 * Parse JSON out of a model reply that may wrap it in prose or ```json fences.
 * Returns null when nothing parseable is found.
 */
export function extractJson<T>(text: string): T | null {
  const fenced = text.match(/```(?:json)?\s*([\s\S]*?)```/);
  const candidates = [fenced?.[1], text];
  for (const c of candidates) {
    if (!c) continue;
    // Prose before the JSON may contain stray brackets, so try several start
    // positions, earliest first, trimming trailing junk at each.
    const starts: number[] = [];
    for (let i = 0; i < c.length && starts.length < 12; i++) {
      if (c[i] === "{" || c[i] === "[") starts.push(i);
    }
    for (const start of starts) {
      const slice = c.slice(start);
      for (let end = slice.length; end > 0; end--) {
        const ch = slice[end - 1];
        if (ch !== "}" && ch !== "]") continue;
        try {
          const v = JSON.parse(slice.slice(0, end));
          if (v && typeof v === "object") return v as T;
        } catch {
          /* keep trimming */
        }
      }
    }
  }
  return null;
}

/** Specific message when the model stopped abnormally, else null. */
export function stopReasonError(msg: Anthropic.Message): string | null {
  if (msg.stop_reason === "max_tokens")
    return "The AI response was cut off — the input is too long. Shorten the CV or job description and retry.";
  if (msg.stop_reason === "refusal")
    return "The AI declined this request — rephrase the input and try again.";
  return null;
}

/** Friendly error message for API failures, without leaking internals. */
export function apiErrorMessage(err: unknown): string {
  if (err instanceof Anthropic.APIError) {
    if (err.status === 401) return "The AI service key is invalid or expired — check ANTHROPIC_API_KEY.";
    if (err.status === 429) return "The AI service is rate-limited — wait a moment and retry.";
    if (err.status === 529) return "The AI service is overloaded — retry shortly.";
    return `AI service error (${err.status ?? "network"}).`;
  }
  return err instanceof Error ? err.message : "Unexpected error.";
}
