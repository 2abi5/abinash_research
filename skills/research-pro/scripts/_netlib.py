"""Shared HTTP helper for the research-pro scripts that talk to bibliographic APIs.

One class, three properties the scripts depend on:

- A clean 404/410 is NOT_FOUND: a reachable database said "no such record". That is
  evidence. A timeout, DNS failure, proxy refusal or 5xx is None: no evidence either
  way. Only the second kind counts toward declaring the network unavailable, so a
  run of fabricated DOIs is reported as UNVERIFIED, never as OFFLINE.
- A JSON cache (``--cache``) so weekly ``make check`` does not re-ask the same
  question, and a replay file (``--replay``) in the same format that answers every
  request from disk and never touches the network. Tests use replay.
- Polite pacing and a single retry on HTTP 429.

Stdlib only.
"""
from __future__ import annotations

import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

TIMEOUT = 20


class NotFound:
    """A reachable database said: no such record. Distinct from a network error."""

    def __repr__(self) -> str:  # pragma: no cover
        return "NOT_FOUND"


NOT_FOUND = NotFound()


def q(s: str) -> str:
    """Quote a query-string value."""
    return urllib.parse.quote(s, safe="")


def qp(s: str) -> str:
    """Quote a path identifier such as a DOI: keep '/' and ':' as the APIs document them."""
    return urllib.parse.quote(s, safe="/:")


def load_replay(path: str | None) -> dict | None:
    """Load a replay file, or raise ValueError with a readable message."""
    if not path:
        return None
    try:
        with open(path, encoding="utf-8") as fh:
            data = json.load(fh)
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot load replay file {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise ValueError(f"replay file {path} must be a JSON object keyed by URL")
    return data


class Net:
    """HTTP with a cache, polite pacing, and a sharp line between 'no record' and 'no network'."""

    def __init__(self, user_agent: str, enabled: bool = True, mailto: str = "",
                 cache_path: str | None = None, replay: dict | None = None,
                 verbose: bool = False, pause: float = 0.12):
        self.user_agent = user_agent
        self.enabled = enabled
        self.mailto = mailto
        self.failures = 0
        self.blocked = False
        self.calls = 0
        self.verbose = verbose
        self.pause = pause
        self.replay = replay          # url -> {"status": "ok"|"notfound", "body": ...}
        self.cache_path = cache_path
        self.cache: dict = {}
        self.dirty = False
        if cache_path and os.path.isfile(cache_path):
            try:
                with open(cache_path, encoding="utf-8") as fh:
                    self.cache = json.load(fh)
            except (OSError, json.JSONDecodeError):
                self.cache = {}

    # ------------------------------------------------------------ bookkeeping
    @property
    def offline(self) -> bool:
        return (not self.enabled or self.blocked) and self.replay is None

    @property
    def state(self) -> str:
        if self.replay is not None:
            return "REPLAY"
        if not self.enabled:
            return "DISABLED"
        if self.blocked:
            return "UNAVAILABLE"
        return f"available ({self.calls} calls)"

    def _log(self, url: str, outcome: str) -> None:
        if self.verbose:
            print(f"    [{outcome}] {url}", file=sys.stderr)

    def _store(self, url: str, status: str, body) -> None:
        if self.cache_path is not None:
            self.cache[url] = {"status": status, "body": body}
            self.dirty = True

    def save(self) -> None:
        if self.cache_path and self.dirty:
            os.makedirs(os.path.dirname(os.path.abspath(self.cache_path)), exist_ok=True)
            with open(self.cache_path, "w", encoding="utf-8") as fh:
                json.dump(self.cache, fh)

    def forgive_one_failure(self) -> None:
        """Undo one failure count when the error was a query-shape problem, not the network."""
        self.failures = max(0, self.failures - 1)
        if self.failures < 4:
            self.blocked = False

    # ------------------------------------------------------------ the request
    def get(self, url: str):
        """Return parsed JSON / raw text, NOT_FOUND for a clean 404/410, or None on error."""
        if self.replay is not None:
            hit = self.replay.get(url)
            if hit is None or hit.get("status") == "notfound":
                self._log(url, "replay:notfound")
                return NOT_FOUND
            self._log(url, "replay:ok")
            return hit.get("body")
        if url in self.cache:
            hit = self.cache[url]
            self._log(url, "cache")
            return NOT_FOUND if hit.get("status") == "notfound" else hit.get("body")
        if not self.enabled or self.blocked:
            return None
        self.calls += 1
        req = urllib.request.Request(url, headers={"User-Agent": self.user_agent,
                                                   "Accept": "application/json"})
        for attempt in (1, 2):
            try:
                with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
                    raw = r.read().decode("utf-8", "replace")
                try:
                    body = json.loads(raw)
                except json.JSONDecodeError:
                    body = raw
                self._store(url, "ok", body)
                self._log(url, "ok")
                time.sleep(self.pause)  # be polite to public APIs
                return body
            except urllib.error.HTTPError as exc:
                if exc.code in (404, 410):
                    self._store(url, "notfound", None)
                    self._log(url, "404")
                    return NOT_FOUND
                if exc.code == 429 and attempt == 1:
                    self._log(url, "429, retrying")
                    time.sleep(2.0)
                    continue
                self._log(url, f"http {exc.code}")
                break
            except Exception as exc:  # timeouts, DNS, proxy refusals
                self._log(url, f"error {type(exc).__name__}")
                break
        self.failures += 1
        if self.failures >= 4:
            self.blocked = True  # network is unavailable; stop hammering it
        return None
