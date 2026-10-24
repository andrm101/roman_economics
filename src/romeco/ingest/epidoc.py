"""Minimal EpiDoc (TEI) reader for DDbDP documentary texts.

Produces one record per line (textpart / column / line) with:

* a Leiden-style rendering (supplied text in [ ], unclear letters marked
  with a combining dot, gaps as [---], abbreviations expanded in ( ));
* every encoded numeral with its ``@value`` and whether it is unclear or
  supplied, so numeric claims can be anchored to a line without retyping.

It deliberately does not resolve editorial choices: ``<choice>`` keeps the
regularised form, and the raw XML stays the authority.
"""

from __future__ import annotations

import hashlib
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from fractions import Fraction
from pathlib import Path

TEI = "{http://www.tei-c.org/ns/1.0}"
DOT = "̣"


@dataclass
class Numeral:
    value: str | None
    glyphs: str
    unclear: bool
    supplied: bool

    @property
    def fraction(self) -> Fraction | None:
        if self.value is None:
            return None
        try:
            return Fraction(self.value)
        except ValueError:
            return None


@dataclass
class Line:
    textpart: str
    column: str
    n: str
    text: str = ""
    numerals: list[Numeral] = field(default_factory=list)

    @property
    def locus(self) -> str:
        return f"{self.textpart} col. {self.column} l. {self.n}"


def _local(tag: str) -> str:
    return tag.split("}", 1)[-1]


class _Walker:
    def __init__(self, textpart: str, column: str):
        self.textpart, self.column = textpart, column
        self.lines: list[Line] = []
        self.cur: Line | None = None

    def _emit(self, s: str):
        if self.cur is not None and s:
            self.cur.text += s

    def walk(self, el, unclear=False, supplied=False):
        tag = _local(el.tag)
        if tag == "lb":
            self.cur = Line(self.textpart, self.column, el.get("n", "?"))
            self.lines.append(self.cur)
            if el.get("break") == "no" and len(self.lines) > 1:
                self.cur.text = "-"
            self._tail(el, unclear, supplied)
            return
        if tag == "gap":
            self._emit("[---]" if el.get("reason") == "lost" else "...")
            self._tail(el, unclear, supplied)
            return
        if tag == "g":
            self._emit("'")
            self._tail(el, unclear, supplied)
            return
        if tag in ("del",) or tag == "orig" and self._in_choice(el):
            self._tail(el, unclear, supplied)
            return
        if tag == "num":
            start = len(self.cur.text) if self.cur else 0
            sub_unclear = unclear or any(_local(d.tag) == "unclear" for d in el.iter())
            sub_supplied = supplied or any(_local(d.tag) == "supplied" for d in el.iter())
            self._inner(el, unclear, supplied)
            if self.cur is not None:
                glyphs = self.cur.text[start:]
                self.cur.numerals.append(Numeral(el.get("value"), glyphs, sub_unclear, sub_supplied))
            self._tail(el, unclear, supplied)
            return
        open_, close = {"supplied": ("[", "]"), "ex": ("(", ")")}.get(tag, ("", ""))
        if tag == "supplied" and el.get("reason") == "omitted":
            open_, close = "<", ">"
        self._emit(open_)
        self._inner(el, unclear or tag == "unclear", supplied or tag == "supplied")
        self._emit(close)
        self._tail(el, unclear, supplied)

    def _in_choice(self, el) -> bool:  # ElementTree has no parent pointers; orig skipped always
        return True

    def _inner(self, el, unclear, supplied):
        if el.text:
            self._emit(self._mark(el.text, unclear))
        for ch in el:
            self.walk(ch, unclear, supplied)

    def _tail(self, el, unclear, supplied):
        if el.tail:
            self._emit(self._mark(el.tail, unclear))

    @staticmethod
    def _mark(s: str, unclear: bool) -> str:
        if not s:
            return ""
        core = " ".join(s.split())
        if not core:
            return " "
        s = (" " if s[0].isspace() else "") + core + (" " if s[-1].isspace() else "")
        if unclear:
            return "".join(c + DOT if c.isalpha() else c for c in s)
        return s


def read_lines(path: str | Path) -> list[Line]:
    root = ET.parse(path).getroot()
    edition = next(d for d in root.iter(f"{TEI}div") if d.get("type") == "edition")
    lines: list[Line] = []
    for part in edition.findall(f"{TEI}div"):
        tp = part.get("n", "")
        cols = part.findall(f"{TEI}div") or [part]
        for col in cols:
            w = _Walker(tp, col.get("n", "") if col is not part else "")
            for ab in col.iter(f"{TEI}ab"):
                for ch in ab:
                    w.walk(ch)
            for ln in w.lines:
                ln.text = " ".join(ln.text.split())
            lines.extend(w.lines)
    return lines


def sha256(path: str | Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def line(lines: list[Line], textpart: str, column: str, n: str) -> Line:
    for ln in lines:
        if (ln.textpart, ln.column, ln.n) == (textpart, column, n):
            return ln
    raise KeyError((textpart, column, n))
