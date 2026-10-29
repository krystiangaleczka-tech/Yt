"""Scoring tematu: popyt, konkurencja, wyjątkowość, prognoza wyświetleń, koszt, ROI i werdykt.

Wszystko liczone na żywo z oceny Claude, danych rynkowych i ustawień — zmiana ustawień od razu
przelicza ranking. Prognozy są orientacyjne (±50–100%) i służą do porównywania tematów między sobą.
"""
from __future__ import annotations

import math

from .config import AVAILABILITY

WEIGHTS = {"interest": 0.25, "demand": 0.20, "open_field": 0.15, "exclusivity": 0.15, "roi": 0.15, "ease": 0.10}
VERDICTS = [(70, "Rób to"), (55, "Obiecujące"), (40, "Może"), (0, "Odpuść")]


def clamp(x: float, lo: float = 0, hi: float = 100) -> float:
    return max(lo, min(hi, x))


def log_scale(value: float, full: float) -> float:
    """0 → 0, `full` → 100, logarytmicznie."""
    if not value or value <= 0:
        return 0.0
    return clamp(100 * math.log10(1 + value) / math.log10(1 + full))


def demand_score(wiki: dict | None, yt: dict | None) -> float | None:
    parts = []
    if wiki and wiki.get("article"):
        # artykuł z wyszukiwarki bywa nietrafiony — liczy się słabiej niż wskazany przez Claude
        weight = 0.7 if wiki.get("matched") == "search" else 1.0
        parts.append(log_scale(wiki.get("monthly_avg", 0), 300_000) * weight)
    if yt and yt.get("long_form"):
        parts.append(log_scale(yt.get("median_views", 0), 1_000_000))
    return round(sum(parts) / len(parts), 1) if parts else None


def competition_score(yt: dict | None) -> float | None:
    if not yt:
        return None
    return round(clamp(yt.get("strong_recent", 0) * 8 + yt.get("strong", 0) * 3 + yt.get("relevant", 0) * 1.5), 1)


def channel_factor(user_subs: float, reference_subs: float | None) -> float:
    reference = reference_subs or 100_000
    return clamp(math.sqrt(max(user_subs, 1) / reference), 0.05, 1.5)


def estimate_views(settings: dict, interest: float | None, demand: float | None, competition: float | None,
                   wiki: dict | None, yt: dict | None) -> tuple[int | None, str]:
    """Wyświetlenia w pierwszych 12 miesiącach i opis, skąd wzięła się liczba."""
    subs = float(settings.get("channel_subs") or 0)
    if yt and yt.get("median_first_year"):
        est = yt["median_first_year"] * channel_factor(subs, yt.get("median_subs"))
        basis = "mediana podobnych filmów × wielkość kanału"
        if yt.get("outlier_ratio"):
            est = math.sqrt(est * max(subs * yt["outlier_ratio"], 1))
            basis += " i ratio wyświetlenia/subskrypcje"
    elif wiki and wiki.get("monthly_avg"):
        est = wiki["monthly_avg"] * 12 * 0.01 * clamp(math.sqrt(max(subs, 1) / 10_000), 0.1, 3)
        basis = "odsłony Wikipedii (bez danych YouTube — mała pewność)"
    else:
        return None, "brak danych rynkowych"
    if interest is not None:
        est *= 0.6 + 0.8 * interest / 100
    if demand is not None and competition is not None and competition < 30 and demand > 50:
        est *= 1.3
        basis += ", premia za lukę"
    return int(est), basis


def production_cost(settings: dict, rating: dict, availability: str) -> dict:
    minutes = float(settings.get("video_minutes") or 15)
    visuals = rating.get("visuals") or 5
    access = AVAILABILITY.get(availability, AVAILABILITY["unknown"])["access_hours"]
    hours = {
        "research": float(rating.get("research_hours") or 10),
        "dostęp do źródła": access,
        "scenariusz": minutes * 0.4,
        "montaż i materiały": minutes * 0.8 * (1 + (10 - visuals) / 10),
    }
    total_hours = sum(hours.values())
    usd = total_hours * float(settings.get("hourly_rate_usd") or 0) + float(settings.get("fixed_cost_usd") or 0)
    return {"hours": {k: round(v, 1) for k, v in hours.items()}, "total_hours": round(total_hours, 1),
            "usd": round(usd)}


def compute(book: dict, settings: dict) -> dict:
    rating = book.get("rating") or {}
    market = book.get("market") or {}
    wiki, yt = market.get("wiki"), market.get("youtube")
    availability = book.get("availability") or "unknown"

    interest = rating.get("interest")
    demand = demand_score(wiki, yt)
    competition = competition_score(yt)
    opportunity = round(demand / max(competition, 10), 2) if demand is not None and competition is not None else None

    exclusivity = None
    if interest is not None:
        factor = AVAILABILITY.get(availability, AVAILABILITY["unknown"])["factor"]
        if rating.get("en_translation") is False:
            factor *= 1.15   # brak angielskiego wydania — arbitraż językowy
        exclusivity = round(clamp(interest * factor), 1)

    difficulty = rating.get("difficulty")
    views, views_basis = estimate_views(settings, interest, demand, competition, wiki, yt)
    cost = production_cost(settings, rating, availability) if rating else None
    rpm = float(settings.get("rpm_usd") or 0) if settings.get("monetized") else 0.0
    revenue = round(views / 1000 * rpm) if views is not None else None
    roi = round(revenue / cost["usd"], 2) if revenue is not None and cost and cost["usd"] else None

    parts = {
        "interest": interest,
        "demand": demand,
        "open_field": None if competition is None else 100 - competition,
        "exclusivity": exclusivity,
        "roi": None if roi is None else clamp(100 * math.log2(1 + roi) / math.log2(6)),
        "ease": None if difficulty is None else clamp(100 - (difficulty - 1) * 11.1),
    }
    known = {k: v for k, v in parts.items() if v is not None}
    score = None
    if interest is not None:
        weight = sum(WEIGHTS[k] for k in known)
        score = round(sum(WEIGHTS[k] * v for k, v in known.items()) / weight, 1)
    verdict = next(label for limit, label in VERDICTS if score >= limit) if score is not None else None

    return {
        "score": score,
        "verdict": verdict,
        "completeness": f"{len(known)}/{len(WEIGHTS)}",
        "parts": {k: (round(v, 1) if v is not None else None) for k, v in parts.items()},
        "interest": interest,
        "demand": demand,
        "competition": competition,
        "opportunity_ratio": opportunity,
        "exclusivity": exclusivity,
        "difficulty": difficulty,
        "views": views,
        "views_low": int(views * 0.4) if views is not None else None,
        "views_high": int(views * 2.5) if views is not None else None,
        "views_basis": views_basis,
        "revenue_usd": revenue,
        "cost": cost,
        "roi": roi,
        "value_per_effort": round(views / difficulty) if views is not None and difficulty else None,
        "outlier_ratio": (yt or {}).get("outlier_ratio"),
        "monetized": bool(settings.get("monetized")),
    }
