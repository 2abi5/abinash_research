"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import Icon from "@/components/Icon";

const LINKS = [
  { href: "/", label: "Dashboard", icon: "gauge" },
  { href: "/cv", label: "CV Studio", icon: "file" },
  { href: "/jobs", label: "Job Finder", icon: "search" },
  { href: "/apply", label: "Apply Kit", icon: "rocket" },
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
        <Link href="/" className="brand">
          <span className="brand-mark">
            <Icon name="plane" size={16} strokeWidth={2} />
          </span>
          <span className="brand-name">
            Career<b>Pilot</b>
          </span>
        </Link>
        <div className="nav-links">
          {LINKS.map((l) => (
            <Link
              key={l.href}
              href={l.href}
              className={`nav-link${pathname === l.href ? " active" : ""}`}
            >
              <Icon name={l.icon} size={15} />
              {l.label}
            </Link>
          ))}
        </div>
        <button className="btn ghost small" onClick={logout}>
          <Icon name="logout" size={14} />
          Sign out
        </button>
      </div>
    </nav>
  );
}
