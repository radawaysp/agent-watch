from __future__ import annotations

import hashlib
import html
import re
from datetime import datetime
from email.utils import parsedate_to_datetime
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from dateutil import parser as date_parser

TRACKING_PREFIXES = ("utm_",)
TRACKING_KEYS = {"fbclid", "gclid", "mc_cid", "mc_eid", "ref", "source"}
WHITESPACE_RE = re.compile(r"\s+")
TAG_RE = re.compile(r"<[^>]+>")


def canonicalize_url(url: str) -> str:
    """Remove common tracking query parameters and normalize URL shape."""

    parts = urlsplit(url.strip())
    query_pairs = [
        (key, value)
        for key, value in parse_qsl(parts.query, keep_blank_values=True)
        if not key.lower().startswith(TRACKING_PREFIXES) and key.lower() not in TRACKING_KEYS
    ]
    netloc = parts.netloc.lower()
    path = parts.path.rstrip("/") or parts.path
    query = urlencode(query_pairs, doseq=True)
    return urlunsplit((parts.scheme.lower(), netloc, path, query, ""))


def content_hash(title: str, url: str, summary: str = "") -> str:
    normalized = "\n".join(
        [
            collapse_whitespace(title).lower(),
            canonicalize_url(url).lower(),
            collapse_whitespace(summary).lower(),
        ]
    )
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def collapse_whitespace(value: str) -> str:
    return WHITESPACE_RE.sub(" ", value).strip()


def clean_html(value: str | None) -> str:
    if not value:
        return ""
    without_tags = TAG_RE.sub(" ", value)
    return collapse_whitespace(html.unescape(without_tags))


def parse_datetime(value: str | datetime | None) -> datetime | None:
    if value is None or isinstance(value, datetime):
        return value
    try:
        return parsedate_to_datetime(value)
    except (TypeError, ValueError):
        try:
            return date_parser.parse(value)
        except (TypeError, ValueError, OverflowError):
            return None
