// Client-side persistence helpers (localStorage, guarded for private windows).

export function loadLS<T>(key: string, fallback: T): T {
  if (typeof window === "undefined") return fallback;
  try {
    const raw = window.localStorage.getItem(key);
    return raw === null ? fallback : (JSON.parse(raw) as T);
  } catch {
    return fallback;
  }
}

export function saveLS<T>(key: string, value: T): void {
  if (typeof window === "undefined") return;
  try {
    window.localStorage.setItem(key, JSON.stringify(value));
  } catch {
    /* storage unavailable — non-fatal */
  }
}

export const KEYS = {
  cvText: "cp_cv_text",
  targetRole: "cp_target_role",
  analysis: "cp_analysis",
  optimized: "cp_optimized_cv",
  tracker: "cp_tracker",
} as const;

export type TrackedApp = {
  id: string;
  title: string;
  company: string;
  url: string;
  status: "Saved" | "Applied" | "Interview" | "Offer" | "Rejected";
  notes: string;
  addedAt: string;
};
