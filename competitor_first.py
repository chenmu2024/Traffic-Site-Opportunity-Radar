#!/usr/bin/env python3
"""Competitor-first SEO evidence gates using attributable, public, dated snapshots.

This does not scrape Semrush and does not equate global organic estimates with
country-specific visits. Only researchers edit the small public evidence file.
"""
import argparse
import json
from datetime import date, datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

from radar import ROOT, COUNTRIES, clean, domain, number

MIN_ORGANIC_GLOBAL = 10000
MAX_ORGANIC_GLOBAL = 100000
MAX_EVIDENCE_AGE_DAYS = 105
TOOL_POSITION_MAX = 10


def gate(snapshot, today):
    host = domain(snapshot.get("domain"))
    country = snapshot.get("primary_country")
    semrush = snapshot.get("source_url") or ""
    url = snapshot.get("tool_homepage") or ""
    month = snapshot.get("month", "")
    organic = number(snapshot.get("organic_global_estimated_monthly"))
    rank = number(snapshot.get("keyword_position"), 1, 100)
    kw_volume = number(snapshot.get("keyword_volume"))
    kw = " ".join((snapshot.get("keyword") or "").split())
    reason = clean(snapshot.get("reason"), 600)
    try:
        day = date.fromisoformat(month + "-01")
    except ValueError:
        day = None
    # Web content is only an attributable example; no provider API calls.
    valid_provenance = (host and country in COUNTRIES and
                        urlparse(semrush).scheme == "https" and
                        urlparse(semrush).hostname in {"www.semrush.com", "semrush.com"} and
                        host in semrush and
                        urlparse(url).scheme == "https" and
                        domain(url) == host and day is not None and day <= today)
    valid_provenance = valid_provenance and snapshot.get("keyword_country") == country
    if not valid_provenance or organic is None:
        state = "REJECT_INVALID_ATTRIBUTION"
    elif (today-day).days > MAX_EVIDENCE_AGE_DAYS:
        state = "STALE_SOURCE_REFRESH_NEEDED"
    elif organic < MIN_ORGANIC_GLOBAL or organic > MAX_ORGANIC_GLOBAL:
        state = "REJECT_OUTSIDE_GLOBAL_ORGANIC_TRAFFIC_TARGET"
    elif snapshot.get("topic_overlap"):
        state = "OVERLAPS_USER_EXISTING_SITE_NOT_NEW_PROJECT"
    elif (not snapshot.get("keyword_is_nonbrand") or
          not kw or not rank or rank > TOOL_POSITION_MAX or kw_volume is None):
        state = "REJECT_NO_STRONG_NONBRAND_TOOL_KEYWORD"
    elif not snapshot.get("tool_page_publicly_checked"):
        state = "REQUIRE_LANDING_PAGE_FUNCTION_REVIEW"
    else:
        state = "PUBLIC_ORGANIC_AND_NONBRAND_TOOL_EVIDENCE_REVIEW_SERP"
    return {
        "domain": host, "primary_country": country,
        "status": state, "source_url": semrush, "source_month": month,
        "global_monthly_organic_provider_estimate": int(organic) if organic is not None else None,
        "country_organic_visits_not_proven": True, "keyword": kw,
        "keyword_country": snapshot.get("keyword_country"),
        "keyword_position_public_snapshot": int(rank) if rank is not None else None,
        "keyword_volume_public_snapshot": kw_volume, "nonbrand_manual": snapshot.get("keyword_is_nonbrand"),
        "example_tool_url": url, "public_function_inspected": bool(snapshot.get("tool_page_publicly_checked")),
        "site_topic_overlap": bool(snapshot.get("topic_overlap")),
        "source_notes": reason,
        "organic_verified_by_first_party_analytics": False,
        "kd_verified": False, "serp_low_authority_verified": False,
    }


def build(payload, now=None):
    now = now or datetime.now(timezone.utc)
    scored = [gate(x, now.date()) for x in payload.get("snapshots", [])]
    recommended = [x for x in scored if x["status"] ==
                   "PUBLIC_ORGANIC_AND_NONBRAND_TOOL_EVIDENCE_REVIEW_SERP"]
    return {
        "generated_at_utc": now.isoformat(),
        "market": "SEO_TRAFFIC_TOOLS_NOT_SAAS",
        "public_evidence_count": len(scored),
        "shortlist_for_serp_check": recommended[:3],
        "others": [x for x in scored if x not in recommended],
        "organic_traffic_numbers_are_public_provider_estimates_not_first_party": True,
        "do_not_sum_keyword_volume_as_traffic": True,
        "note": "Global organic estimate is NOT country organic visits and does not prove a particular landing page's traffic. No build approved without independent SERP, KD and advantage analysis."
    }


def markdown(data):
    lines = ["# Competitor-first · Public SEO evidence report", "",
             "> Public Semrush global organic visits are third-party estimates, not first-party analytics.",
             "> Nonbrand query ranking is country-specific. Ranking keyword DOES NOT prove the exact page receives those visits.",
             "> A site can have 10k+ organic traffic and still be a bad build opportunity. Never mix SaaS income projects.", "",
             "## Functional competitors that qualify for SERP inspection only", ""]
    if not data["shortlist_for_serp_check"]:
        lines.append("No source-backed candidate currently passes domain organic range, nonbrand keyword rank, and actual browser tool inspection.")
    for e in data["shortlist_for_serp_check"]:
        lines.extend([
            "### " + clean(e["domain"]) + " · " + clean(e["primary_country"]),
            "- Public global organic estimate: " + str(e["global_monthly_organic_provider_estimate"]) + " / month (" + clean(e["source_month"]) + ")",
            "- Country keyword: " + clean(e["keyword"]) + " · rank #" + str(e["keyword_position_public_snapshot"]) + " · Volume " + str(e["keyword_volume_public_snapshot"]) + " (public provider snapshot).",
            "- Browser tool URL: " + clean(e["example_tool_url"],300),
            "- Source: " + clean(e["source_url"],300),
            "- Next step: Inspect SAME-COUNTRY current KD and actual top-10 SERP (weak sites?), separate tool page traffic, competitive differentiation and AdSense economics. Do not open a new domain yet.", ""
        ])
    lines += ["## Rejected or held even if a site exists", "",
              "| Domain | Public estimated global organic/month | Status |", "|---|---:|---|"]
    for e in data["others"]:
        lines.append("| " + clean(e["domain"]) + " | " +
                     str(e["global_monthly_organic_provider_estimate"]) + " | " + e["status"] + " |")
    lines += ["", "## Rules",
              "- Site target: global organic estimated 10k–100k, then verify target-country traffic independently.",
              "- Do not promote domains whose ranked term is navigational, whose usable tool URL was not checked, or whose topic overlaps existing sites.",
              "- DR, KD and weak-domain SERP are unknown unless separately sourced; global site organic does not demonstrate the individual tool page's visits.",
              "- Public third-party data is manually researched, dated and explicitly attributed; no unauthorized automated Semrush scraping or paid API.",
              "- Treat this as research priority, NOT a development recommendation.", ""]
    return "\n".join(lines)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--source", type=Path, default=ROOT/"inputs"/"public-organic-competitors.json")
    p.add_argument("--output-dir", type=Path, default=ROOT/"reports")
    args = p.parse_args()
    data = build(json.loads(args.source.read_text(encoding="utf-8")))
    args.output_dir.mkdir(exist_ok=True, parents=True)
    (args.output_dir/"competitor-first.json").write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    (args.output_dir/"competitor-first.md").write_text(markdown(data),encoding="utf-8")
    print(f"Competitor-first: {data['public_evidence_count']} researched domains; {len(data['shortlist_for_serp_check'])} candidates for SERP inspection; 0 approved builds.")


if __name__ == "__main__":
    main()
