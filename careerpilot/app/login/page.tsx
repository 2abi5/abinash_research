"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Icon from "@/components/Icon";

export default function LoginPage() {
  const router = useRouter();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setBusy(true);
    setError("");
    try {
      const res = await fetch("/api/auth/login", {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({ username, password }),
      });
      const data = await res.json().catch(() => ({}));
      if (!res.ok) {
        setError(data.error || "Login failed.");
        return;
      }
      router.push("/");
      router.refresh();
    } catch {
      setError("Network error — try again.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="login-wrap">
      <div className="card login-card anim">
        <div className="login-head">
          <span className="login-mark">
            <Icon name="plane" size={24} strokeWidth={2} />
          </span>
          <div className="login-logo">
            Career<b>Pilot</b>
          </div>
        </div>
        <p className="login-sub">Your AI job-search copilot</p>
        <form onSubmit={submit}>
          <label className="field" htmlFor="u">Username</label>
          <input
            id="u"
            type="text"
            autoComplete="username"
            autoCapitalize="none"
            autoCorrect="off"
            spellCheck={false}
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
          />
          <label className="field" htmlFor="p">Password</label>
          <input
            id="p"
            type="password"
            autoComplete="current-password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
          {error && (
            <div className="error">
              <Icon name="alert" size={16} style={{ marginTop: 2 }} />
              <span>{error}</span>
            </div>
          )}
          <button className="btn" style={{ width: "100%", marginTop: 20 }} disabled={busy}>
            {busy ? <span className="spinner" /> : <>Sign in <Icon name="external" size={14} /></>}
          </button>
        </form>
      </div>
    </div>
  );
}
