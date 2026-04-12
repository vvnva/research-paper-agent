from __future__ import annotations

from datetime import datetime
from xml.etree import ElementTree as ET


ATOM_NS = {"atom": "http://www.w3.org/2005/Atom"}


def compact_query(text: str) -> str:
    return " ".join(text.strip().split())


def parse_iso_date(value: str | None) -> str | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).date().isoformat()
    except ValueError:
        return None


def safe_find_text(parent: ET.Element, path: str, ns: dict[str, str] | None = None) -> str:
    node = parent.find(path, ns or {})
    return node.text.strip() if node is not None and node.text else ""
