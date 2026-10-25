"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";

const LINKS = [
  { href: "/", label: "Dashboard" },
  { href: "/cv", label: "CV Studio" },
  { href: "/jobs", label: "Job Finder" },
  { href: "/apply", label: "Apply Kit" },
];

export default function Nav() {
  const pathname = usePathname();
  const router = useRouter();

  async function logout() {
    await fetch("/api/auth/logout", { method: "POST" });
    router.push("/login");
    router.refresh();
  }

  return (
    <nav className="nav">
      <div className="nav-inner">
        <span className="brand">✈ CareerPilot</span>
        <div className="nav-links">
          {LINKS.map((l) => (
            <Link
              key={l.href}
              href={l.href}
              className={`nav-link${pathname === l.href ? " active" : ""}`}
            >
              {l.label}
            </Link>
          ))}
        </div>
        <button className="btn ghost small" onClick={logout}>
          Sign out
        </button>
      </div>
    </nav>
  );
}
