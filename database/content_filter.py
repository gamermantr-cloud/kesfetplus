"""Objectionable content filter (App Store / Google Play Guideline 1.2 - UGC).

Stdlib-only, fully offline - no external/paid API calls (OpenAI Moderation
etc. were already considered and deferred, see
docs/research/app-store-yayinlama-yol-haritasi.md and the 2026-09-17
research note it references: "hesap gerektiriyor"). This keeps the project's
"KVKK-dostu, dışarıya veri göndermeyen" stance intact - text never leaves
the process.

This is a SEPARATE layer from database/trust_scoring.py, not a replacement
for it: trust-scoring asks "is this likely spam/fake/duplicate" (a
reliability question), this module asks "is this acceptable at all"
(profanity / hate speech / explicit sexual content - an acceptability
question). A comment can score perfectly on trust and still be
objectionable, or vice versa; both checks run independently and either one
can force a comment/status into "hidden".

Word list: a short, deliberately self-authored TR+EN list of unambiguous
profanity / hate-speech slurs / explicit-sexual terms. NOT copied from a
third-party moderation wordlist project (e.g. LDNOOBW) - those don't carry
a clear, checkable license for verbatim reuse. A short, hand-picked list
also keeps false-positive risk manageable for an MVP: this project's own
data-quality lesson (see docs/ - the "bar" false-positive story) is that
large, mechanically-assembled blocklists tend to flag innocuous words that
happen to contain a banned substring (the classic "Scunthorpe problem",
e.g. a town named Scunthorpe getting blocked over "cunt"). Every entry
below is matched as a whole word/phrase (`\\b`-bounded), never as a bare
substring, for exactly this reason.

Matched terms are NEVER logged or persisted anywhere - callers
(comments_store.add_comment, checkins_store.add_status) must only read
`is_objectionable` and discard `matched_terms`, consistent with the
project's privacy stance.
"""

from __future__ import annotations

import re
from typing import Any

# ---------------------------------------------------------------------------
# Word list - deliberately short, self-authored (see module docstring).
# Lowercase, matched after normalization (see _normalize/_collapse_obfuscation
# below), so ASCII-folded variants (pic/piç, got/göt, ...) are listed
# separately rather than relying on locale-aware casefolding.
# ---------------------------------------------------------------------------
_OBJECTIONABLE_TERMS: frozenset[str] = frozenset(
    {
        # Turkish profanity
        "amk",
        "aq",
        "oç",
        "oc",
        "siktir",
        "sikeyim",
        "sik",
        "yarrak",
        "yarak",
        "orospu",
        "kahpe",
        "piç",
        "pic",
        "yavşak",
        "yavsak",
        "amcık",
        "amcik",
        "göt",
        "got",
        "pezevenk",
        "ibne",
        # Turkish explicit sexual content
        "sikiş",
        "sikis",
        "porno",
        # English profanity
        "fuck",
        "shit",
        "bitch",
        "asshole",
        "bastard",
        "cunt",
        "motherfucker",
        "dick",
        "pussy",
        "whore",
        "slut",
        # English hate speech / slurs
        "nigger",
        "nigga",
        "faggot",
        # English explicit sexual content
        "porn",
        "xxx",
    }
)

# Common leetspeak substitutions used to dodge a plain word match.
_LEET_MAP = str.maketrans(
    {
        "4": "a",
        "3": "e",
        "1": "i",
        "!": "i",
        "0": "o",
        "5": "s",
        "$": "s",
        "@": "a",
    }
)

# A run of single-character tokens separated by whitespace or common
# obfuscation punctuation (e.g. "s i k", "s.i.k", "s-i-k") - collapsed down
# to the plain word before matching. Deliberately requires EVERY token in
# the run to be exactly one character, so it never touches real multi-letter
# words (e.g. "klasik müzik" has no internal separators to begin with, and
# "iyi - çok teşekkürler" keeps its spaces since "iyi"/"çok" aren't
# single-character tokens).
_OBFUSCATION_RUN_RE = re.compile(r"\b\w(?:[\s._*-]+\w)+\b")
_OBFUSCATION_SEPARATOR_RE = re.compile(r"[\s._*-]+")

_TERM_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = tuple(
    (term, re.compile(r"\b" + r"\s+".join(re.escape(p) for p in term.split(" ")) + r"\b"))
    for term in sorted(_OBJECTIONABLE_TERMS)
)


def _collapse_obfuscation(text: str) -> str:
    def _squash(match: re.Match[str]) -> str:
        return _OBFUSCATION_SEPARATOR_RE.sub("", match.group(0))

    return _OBFUSCATION_RUN_RE.sub(_squash, text)


def _normalize(text: str) -> str:
    lowered = text.lower().translate(_LEET_MAP)
    return _collapse_obfuscation(lowered)


def check_content(text: str) -> dict[str, Any]:
    """Check free-text user content for objectionable material.

    Returns {"is_objectionable": bool, "matched_terms": list[str] | None}.
    Callers must use only `is_objectionable` when deciding what to store/log
    - `matched_terms` exists for this function's contract but must never be
    persisted or logged by a caller (see module docstring).
    """
    if not text or not text.strip():
        return {"is_objectionable": False, "matched_terms": None}

    normalized = _normalize(text)
    matched = [term for term, pattern in _TERM_PATTERNS if pattern.search(normalized)]

    if matched:
        return {"is_objectionable": True, "matched_terms": matched}
    return {"is_objectionable": False, "matched_terms": None}
