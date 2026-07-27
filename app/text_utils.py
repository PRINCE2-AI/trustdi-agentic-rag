from __future__ import annotations

import math
import re
from collections import Counter
from datetime import datetime

from app.schemas import ColumnType


STOPWORDS = {
    "a",
    "an",
    "and",
    "at",
    "by",
    "for",
    "from",
    "id",
    "in",
    "is",
    "no",
    "of",
    "on",
    "or",
    "the",
    "to",
    "with",
}


SYNONYMS = {
    "customer": {"client", "buyer", "account"},
    "client": {"customer", "buyer", "account"},
    "amount": {"price", "revenue", "sales", "total", "value"},
    "revenue": {"amount", "sales", "price", "total"},
    "total": {"amount", "price", "revenue", "sales", "value"},
    "sales": {"amount", "revenue", "price", "total", "sale"},
    "price": {"amount", "revenue", "sales", "total", "value"},
    "date": {"day", "dt", "timestamp", "time"},
    "purchase": {"order", "sale", "buy", "transaction"},
    "order": {"purchase", "sale", "transaction"},
    "email": {"mail", "email_address"},
    "phone": {"mobile", "contact", "telephone"},
    "product": {"item", "sku", "goods"},
    "item": {"product", "sku", "goods", "title"},
    "sku": {"product", "item"},
    "name": {"title", "label"},
    "title": {"name", "label", "product", "item"},
    "region": {"area", "state", "country", "location"},
    "area": {"region", "state", "country", "location"},
}


def tokenize(text: str) -> tuple[str, ...]:
    expanded = re.sub(r"([a-z])([A-Z])", r"\1 \2", text)
    tokens = re.findall(r"[a-zA-Z0-9]+", expanded.lower())
    return tuple(token for token in tokens if token not in STOPWORDS)


def expand_tokens(tokens: tuple[str, ...]) -> set[str]:
    expanded = set(tokens)
    for token in tokens:
        expanded.update(SYNONYMS.get(token, set()))
    return expanded


def lexical_similarity(left: str | tuple[str, ...], right: str | tuple[str, ...]) -> float:
    left_tokens = tokenize(left) if isinstance(left, str) else left
    right_tokens = tokenize(right) if isinstance(right, str) else right
    left_set = expand_tokens(left_tokens)
    right_set = expand_tokens(right_tokens)
    if not left_set or not right_set:
        return 0.0
    overlap = len(left_set & right_set)
    union = len(left_set | right_set)
    return overlap / union


def cosine_similarity(left: str, right: str) -> float:
    left_counts = Counter(tokenize(left))
    right_counts = Counter(tokenize(right))
    if not left_counts or not right_counts:
        return 0.0
    common = set(left_counts) & set(right_counts)
    numerator = sum(left_counts[token] * right_counts[token] for token in common)
    left_norm = math.sqrt(sum(value * value for value in left_counts.values()))
    right_norm = math.sqrt(sum(value * value for value in right_counts.values()))
    if left_norm == 0 or right_norm == 0:
        return 0.0
    return numerator / (left_norm * right_norm)


def infer_column_type(values: list[str]) -> ColumnType:
    cleaned = [value.strip() for value in values if value and value.strip()]
    if not cleaned:
        return ColumnType.UNKNOWN
    email_hits = sum(1 for value in cleaned if re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", value))
    bool_hits = sum(1 for value in cleaned if value.lower() in {"true", "false", "yes", "no", "0", "1"})
    int_hits = sum(1 for value in cleaned if re.match(r"^-?\d+$", value))
    float_hits = sum(1 for value in cleaned if re.match(r"^-?\d+(\.\d+)?$", value))
    date_hits = 0
    for value in cleaned:
        for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%m/%d/%Y", "%Y/%m/%d"):
            try:
                datetime.strptime(value[:10], fmt)
                date_hits += 1
                break
            except ValueError:
                continue
    threshold = max(1, int(len(cleaned) * 0.6))
    if email_hits >= threshold:
        return ColumnType.EMAIL
    if bool_hits >= threshold:
        return ColumnType.BOOLEAN
    if int_hits >= threshold:
        return ColumnType.INTEGER
    if float_hits >= threshold:
        return ColumnType.FLOAT
    if date_hits >= threshold:
        return ColumnType.DATE
    return ColumnType.TEXT


def clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, value))
