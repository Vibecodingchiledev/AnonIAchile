from __future__ import annotations

import re
from typing import List

from meta import Span

EMAIL_RE = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
RUT_RE = re.compile(r"\b\d{1,2}\.?\d{3}\.?\d{3}-?[\dkK]\b")
PHONE_CL_RE = re.compile(r"(?:\+?56\s?)?(?:9|2|32|33|41|42|51|52|55|57|61|63|64|65|67|71|72|73|75)\s?\d{3,4}\s?\d{4}\b")
PLATE_CL_RE = re.compile(r"\b(?:[A-Z]{2}-?\d{4}|[A-Z]{4}-?\d{2})\b")
DATE_RE = re.compile(r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b")
ADDRESS_RE = re.compile(r"\b(?:Calle|Av\.?|Avenida|Pasaje|Camino|Ruta|Carrer)\s+[A-ZÁÉÍÓÚÑ][\wÁÉÍÓÚÑáéíóúñ\s.-]{2,}(?:\d+)?", re.IGNORECASE)
PERSON_RE = re.compile(r"\b([A-ZÁÉÍÓÚÑ][a-záéíóúñ]+(?:\s+[A-ZÁÉÍÓÚÑ][a-záéíóúñ]+)+)\b")


LABEL_PATTERNS = [
    ("EMAIL", EMAIL_RE),
    ("RUT_CL", RUT_RE),
    ("PHONE_CL", PHONE_CL_RE),
    ("LICENSE_PLATE_CL", PLATE_CL_RE),
    ("DATE", DATE_RE),
    ("LOC", ADDRESS_RE),
    ("PER", PERSON_RE),
]


def detect_spans(text: str) -> List[Span]:
    spans: List[Span] = []
    for label, pattern in LABEL_PATTERNS:
        for match in pattern.finditer(text):
            spans.append(Span(start=match.start(), end=match.end(), label=label, rank=_rank_for_label(label)))
    spans.sort(key=lambda s: (s["start"], -(s["end"] - s["start"]), -s["rank"]))
    return _dedupe_and_merge(spans)



def _rank_for_label(label: str) -> int:
    return {
        "RUT_CL": 4,
        "EMAIL": 4,
        "PHONE_CL": 4,
        "LICENSE_PLATE_CL": 4,
        "PER": 3,
        "LOC": 2,
        "DATE": 1,
    }.get(label, 0)



def _dedupe_and_merge(spans: List[Span]) -> List[Span]:
    if not spans:
        return []
    result: List[Span] = []
    for span in spans:
        if not result:
            result.append(span)
            continue
        current = result[-1]
        if span["start"] < current["end"]:
            current_len = current["end"] - current["start"]
            new_len = span["end"] - span["start"]
            if span["rank"] > current["rank"] or (span["rank"] == current["rank"] and new_len > current_len):
                result[-1] = span
        elif span["start"] == current["end"] and span["label"] == current["label"]:
            current["end"] = span["end"]
        else:
            result.append(span)
    return result
