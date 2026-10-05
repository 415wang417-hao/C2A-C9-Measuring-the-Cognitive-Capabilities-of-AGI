"""Answer grading for KnowBound.

Grading is deliberately tolerant of surface form (article / casing / phrasing)
but strict about content:
  * a real item is correct when any accepted token appears as a whole word
    (regular expression word boundary) in the normalised answer;
  * an unanswerable (fictional) item is correct only when the model declares
    that it does not know / the entity does not exist.
"""

from __future__ import annotations

import re
import unicodedata

UNKNOWN_MARKERS = [
    r"\bunknown\b", r"\bunanswerable\b", r"\bnot answerable\b",
    r"\bno such\b", r"\bdoes not exist\b", r"\bdoesn't exist\b",
    r"\bnot a real\b", r"\bfictional\b", r"\bnot exist\b",
    r"\bno information\b", r"\bcannot be determined\b", r"\bcan't be determined\b",
    r"\bi do not know\b", r"\bi don't know\b", r"\bdon't know\b", r"\bdo not know\b",
    r"\bn/?a\b", r"\bnot applicable\b", r"\bunable to answer\b",
    r"\bno reliable\b", r"\binsufficient information\b", r"\bnot verifiable\b",
]

_WS = re.compile(r"\s+")
_PUNCT = re.compile(r"[^\w\s\.\-\^]", flags=re.UNICODE)


def normalize(text) -> str:
    if text is None:
        return ""
    s = str(text)
    s = unicodedata.normalize("NFKD", s)
    s = "".join(ch for ch in s if not unicodedata.combining(ch))
    s = s.lower()
    s = _PUNCT.sub(" ", s)
    s = _WS.sub(" ", s)
    return s.strip()


def declares_unknown(text) -> bool:
    n = normalize(text)
    if not n:
        return False
    return any(re.search(p, n) for p in UNKNOWN_MARKERS)


def grade_item(item: dict, model_answer) -> dict:
    """Return a grading record for one item."""
    norm = normalize(model_answer)
    declared_unknown = declares_unknown(model_answer)
    if item["answerable"]:
        matched = None
        for acc in item.get("accepted") or []:
            acc_n = normalize(acc)
            if not acc_n:
                continue
            if re.search(r"(?<!\w)" + re.escape(acc_n) + r"(?!\w)", norm):
                matched = acc
                break
        return {"correct": matched is not None, "declared_unknown": declared_unknown,
                "matched": matched, "normalized": norm}
    # unanswerable item: only an explicit declaration counts
    return {"correct": bool(declared_unknown), "declared_unknown": declared_unknown,
            "matched": None, "normalized": norm}
