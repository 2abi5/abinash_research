"""Shared LaTeX/text analysis helpers for the research-pro scripts. Stdlib only."""
from __future__ import annotations

import os
import re

# Environments whose contents are not prose and must not be measured as such.
DROP_ENVS = ("figure", "figure*", "table", "table*", "tabular", "equation", "equation*",
             "align", "align*", "gather", "gather*", "eqnarray", "eqnarray*", "lstlisting",
             "verbatim", "minted", "algorithm", "algorithmic", "tikzpicture", "thebibliography")

SECTION_RE = re.compile(r"\\(?P<lvl>chapter|section|subsection|subsubsection)\*?\s*\{", re.M)


def read_with_inputs(path: str, _seen: set | None = None, depth: int = 0) -> str:
    """Read a .tex file, following \\input and \\include one level of nesting deep."""
    _seen = _seen or set()
    ap = os.path.abspath(path)
    if ap in _seen or depth > 4:
        return ""
    _seen.add(ap)
    try:
        with open(path, encoding="utf-8", errors="replace") as fh:
            text = fh.read()
    except OSError:
        return ""
    base = os.path.dirname(ap)

    def sub(m):
        target = m.group(1).strip()
        for cand in (target, target + ".tex"):
            full = os.path.join(base, cand)
            if os.path.isfile(full):
                return "\n" + read_with_inputs(full, _seen, depth + 1) + "\n"
        return ""

    return re.sub(r"\\(?:input|include)\s*\{([^}]*)\}", sub, text)


def balanced_braces(text: str, start: int) -> tuple[str, int]:
    """Given index of an opening '{', return (contents, index after matching '}')."""
    depth, i, out = 0, start, []
    while i < len(text):
        c = text[i]
        if c == "{":
            depth += 1
            if depth == 1:
                i += 1
                continue
        elif c == "}":
            depth -= 1
            if depth == 0:
                return "".join(out), i + 1
        out.append(c)
        i += 1
    return "".join(out), i


SECTION_CMD_RE = re.compile(r"\\(?:chapter|section|subsection|subsubsection|paragraph|subparagraph)\*?\s*(?=\{)")


def drop_sectioning(text: str) -> str:
    """Remove sectioning commands together with their (brace-balanced) titles.

    Headings are not prose. Leaving them in corrupts paragraph-opener and
    topic-sentence detection, because the heading becomes the first word.
    """
    out, i = [], 0
    while True:
        m = SECTION_CMD_RE.search(text, i)
        if not m:
            out.append(text[i:])
            break
        out.append(text[i:m.start()])
        brace = text.index("{", m.end() - 1)
        _title, after = balanced_braces(text, brace)
        out.append("\n\n")
        i = after
    return "".join(out)


def strip_comments(text: str) -> str:
    return re.sub(r"(?<!\\)%.*?$", "", text, flags=re.M)


def body_only(text: str) -> str:
    """Everything between \\begin{document} and \\end{document}, or the whole text."""
    m = re.search(r"\\begin\{document\}(.*?)(?:\\end\{document\}|$)", text, re.S)
    return m.group(1) if m else text


def to_prose(text: str) -> str:
    """Reduce LaTeX to readable prose: drop math, floats, commands, keep sentence text."""
    t = strip_comments(text)
    for env in DROP_ENVS:
        t = re.sub(rf"\\begin\{{{re.escape(env)}\}}.*?\\end\{{{re.escape(env)}\}}", " ", t, flags=re.S)
    t = re.sub(r"\$\$.*?\$\$", " MATH ", t, flags=re.S)
    t = re.sub(r"(?<!\\)\$.*?(?<!\\)\$", " MATH ", t, flags=re.S)
    t = re.sub(r"\\\[.*?\\\]", " MATH ", t, flags=re.S)
    t = re.sub(r"\\(?:cite|citep|citet|citeauthor|citeyear|autocite|parencite)[a-zA-Z]*\s*(?:\[[^\]]*\])*\s*\{[^}]*\}", " CITE ", t)
    t = re.sub(r"\\(?:ref|eqref|autoref|cref|Cref|pageref|label)\s*\{[^}]*\}", " REF ", t)
    t = re.sub(r"\\(?:includegraphics|usepackage|documentclass|bibliography|bibliographystyle|input|include)\s*(?:\[[^\]]*\])*\s*\{[^}]*\}", " ", t)
    t = drop_sectioning(t)          # headings are not prose
    t = re.sub(r"\\(?:title|author|affiliation|thanks|date)\s*\{[^{}]*\}", " ", t)
    # keep the argument of textual macros, drop the macro
    t = re.sub(r"\\(?:textbf|textit|emph|texttt|textsc|underline|mbox|text)\s*\{([^{}]*)\}", r"\1", t)
    t = re.sub(r"\\(?:begin|end)\s*\{[^}]*\}", " ", t)
    t = re.sub(r"\\[a-zA-Z@]+\*?", " ", t)
    t = t.replace("~", " ").replace("\\&", "and")
    t = re.sub(r"[{}]", " ", t)
    t = re.sub(r"[ \t]+", " ", t)
    return re.sub(r"\n{3,}", "\n\n", t).strip()


_ABBREV = ("e.g", "i.e", "et al", "cf", "vs", "etc", "Fig", "Tab", "Eq", "Sec", "App",
           "Dr", "Prof", "Mr", "Ms", "approx", "resp", "w.r.t", "s.t", "al")


def sentences(prose: str) -> list[str]:
    """Split prose into sentences, protecting common academic abbreviations."""
    t = " " + prose.replace("\n", " ") + " "
    for a in _ABBREV:
        t = t.replace(f" {a}. ", f" {a}<DOT> ")
        t = t.replace(f"({a}. ", f"({a}<DOT> ")
    t = re.sub(r"\b([A-Z])\.\s", r"\1<DOT> ", t)   # initials
    t = re.sub(r"(\d)\.(\d)", r"\1<POINT>\2", t)   # decimals
    parts = re.split(r"(?<=[.!?])\s+", t)
    out = []
    for p in parts:
        s = p.replace("<DOT>", ".").replace("<POINT>", ".").strip()
        if len(s.split()) >= 3:
            out.append(s)
    return out


def words(s: str) -> list[str]:
    return re.findall(r"[A-Za-z][A-Za-z'\-]*", s)


def paragraphs(prose: str) -> list[str]:
    return [p.strip() for p in re.split(r"\n\s*\n", prose) if len(p.split()) >= 12]


def split_sections(text: str) -> list[tuple[str, str, str]]:
    """Return [(level, title, body_text)] from raw LaTeX."""
    marks = []
    for m in SECTION_RE.finditer(text):
        title, after = balanced_braces(text, text.index("{", m.start()))
        marks.append((m.group("lvl"), title.strip(), m.start(), after))
    out = []
    for i, (lvl, title, _start, after) in enumerate(marks):
        end = marks[i + 1][2] if i + 1 < len(marks) else len(text)
        out.append((lvl, title, text[after:end]))
    return out


def count_env(text: str, env: str) -> int:
    return len(re.findall(rf"\\begin\{{{re.escape(env)}\*?\}}", text))


def count_citations(text: str) -> int:
    n = 0
    for m in re.finditer(r"\\(?:[a-zA-Z]*cite[a-zA-Z]*)\s*(?:\[[^\]]*\])*\s*\{([^}]*)\}", text):
        n += len([k for k in m.group(1).split(",") if k.strip()])
    return n


def count_equations(text: str) -> int:
    n = sum(count_env(text, e) for e in ("equation", "align", "gather", "eqnarray"))
    n += len(re.findall(r"\\\[", text))
    return n


def pdf_page_count(pdf_path: str) -> int | None:
    """Page count of a compiled PDF. Tries pdfinfo, then a raw /Type /Page scan."""
    import shutil
    import subprocess
    if not os.path.isfile(pdf_path):
        return None
    if shutil.which("pdfinfo"):
        try:
            out = subprocess.run(["pdfinfo", pdf_path], capture_output=True, text=True, timeout=30)
            m = re.search(r"^Pages:\s+(\d+)", out.stdout, re.M)
            if m:
                return int(m.group(1))
        except Exception:
            pass
    try:
        with open(pdf_path, "rb") as fh:
            data = fh.read()
        n = len(re.findall(rb"/Type\s*/Page[^s]", data))
        return n or None
    except OSError:
        return None


def pdf_text(pdf_path: str) -> str:
    """Extracted PDF text via pdftotext, or '' when unavailable."""
    import shutil
    import subprocess
    if not (os.path.isfile(pdf_path) and shutil.which("pdftotext")):
        return ""
    try:
        out = subprocess.run(["pdftotext", "-layout", pdf_path, "-"],
                             capture_output=True, text=True, timeout=60)
        return out.stdout
    except Exception:
        return ""


def find_registry(start: str = __file__) -> str | None:
    """Locate venues/registry.json relative to this scripts/ directory."""
    here = os.path.dirname(os.path.abspath(start))
    for cand in (os.path.join(here, "..", "venues", "registry.json"),
                 os.path.join(here, "venues", "registry.json")):
        cand = os.path.normpath(cand)
        if os.path.isfile(cand):
            return cand
    return None


GAP_TOKENS = ("[NEEDS SOURCE]", "[TBD]", "[NEEDS EXPERIMENT]", "[AUTHOR DECISION]", "[VERIFY]")


def find_gap_tokens(text: str) -> list[tuple[int, str, str]]:
    out = []
    for i, line in enumerate(text.split("\n"), 1):
        for tok in GAP_TOKENS:
            if tok in line:
                out.append((i, tok, line.strip()[:110]))
    return out
