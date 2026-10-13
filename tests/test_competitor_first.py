import json
import sys
import unittest
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from competitor_first import gate, build, markdown

TODAY=datetime(2026,10,13,12,0,tzinfo=timezone.utc)
def row():
    return {
        "domain":"example.com.br", "primary_country":"BR", "month":"2026-08",
        "organic_global_estimated_monthly":45000,
        "source_url":"https://www.semrush.com/website/example.com.br/overview/",
        "tool_homepage":"https://example.com.br/tool/",
        "keyword":"sorteador de numeros", "keyword_country":"BR",
        "keyword_position":4,"keyword_volume":74000,
        "keyword_is_nonbrand":True,
        "tool_page_publicly_checked":True,
        "topic_overlap":False
    }

class CompetitorFirstTests(unittest.TestCase):
    def test_public_organic_and_nonbrand_tool_only_prompts_serp_not_build(self):
        r=gate(row(), TODAY.date())
        self.assertEqual(r["status"],"PUBLIC_ORGANIC_AND_NONBRAND_TOOL_EVIDENCE_REVIEW_SERP")
        self.assertTrue(r["country_organic_visits_not_proven"])
        self.assertFalse(r["organic_verified_by_first_party_analytics"])
        self.assertFalse(r["kd_verified"])
        self.assertFalse(r["serp_low_authority_verified"])
        report=build({"snapshots":[row()]}, TODAY)
        self.assertEqual(len(report["shortlist_for_serp_check"]),1)
        self.assertIn("do not", markdown(report).lower())
    def test_below_or_above_target_rejected(self):
        a=row();a["organic_global_estimated_monthly"]=3200
        self.assertEqual(gate(a,TODAY.date())["status"],"REJECT_OUTSIDE_GLOBAL_ORGANIC_TRAFFIC_TARGET")
        a["organic_global_estimated_monthly"]=311030
        self.assertEqual(gate(a,TODAY.date())["status"],"REJECT_OUTSIDE_GLOBAL_ORGANIC_TRAFFIC_TARGET")
    def test_topic_overlapping_existing_domains_not_new_build(self):
        a=row();a["topic_overlap"]=True
        self.assertEqual(gate(a,TODAY.date())["status"],"OVERLAPS_USER_EXISTING_SITE_NOT_NEW_PROJECT")
    def test_navigational_or_unverified_tool_landing_rejected(self):
        a=row();a["keyword_is_nonbrand"]=False
        self.assertEqual(gate(a,TODAY.date())["status"],"REJECT_NO_STRONG_NONBRAND_TOOL_KEYWORD")
        a=row();a["tool_page_publicly_checked"]=False
        self.assertEqual(gate(a,TODAY.date())["status"],"REQUIRE_LANDING_PAGE_FUNCTION_REVIEW")
    def test_invalid_source_and_stale_date(self):
        a=row();a["source_url"]="https://evil.example/secrets"
        self.assertEqual(gate(a,TODAY.date())["status"],"REJECT_INVALID_ATTRIBUTION")
        a=row();a["month"]="2025-08"
        self.assertEqual(gate(a,TODAY.date())["status"],"STALE_SOURCE_REFRESH_NEEDED")
    def test_explicit_high_kd_user_review_blocks_repeated_serp_request(self):
        a=row()
        a["manual_keyword_review"]={
            "decision":"REJECT_HIGH_KD_WEAK_ADS_NEW_SITE",
            "reviewed_on":"2026-10-13",
            "core_keyword":"sorteador de numeros",
            "core_volume":74000, "core_kd":50,"core_cpc_usd":0,
            "reason":"Brazil KD50; free randomizer alone offers poor new-site advantage.",
            "do_not_request_more_semrush_for_same_niche":True
        }
        result=build({"snapshots":[a]},TODAY)
        self.assertEqual(len(result["shortlist_for_serp_check"]),0)
        self.assertEqual(result["others"][0]["status"],"REJECT_HIGH_KD_WEAK_ADS_NEW_SITE")
        self.assertTrue(result["others"][0]["manual_keyword_review"]["do_not_request_more_semrush_for_same_niche"])

    def test_cross_market_rank_must_match_country(self):
        a=row();a["keyword_country"]="MX"
        self.assertEqual(gate(a,TODAY.date())["status"],"REJECT_INVALID_ATTRIBUTION")
    def test_monthly_organic_collapse_blocks_research(self):
        x=row()
        x["organic_mom_change_pct"]=-76.11
        result=gate(x,TODAY.date())
        self.assertEqual(result["status"],"HOLD_UNSTABLE_ORGANIC_TREND")

    def test_ads_policy_risk_avoids_promising_download_tool(self):
        x=row()
        x["ad_monetization_policy_risk"]=True
        self.assertEqual(gate(x,TODAY.date())["status"],"REJECT_ADS_MONETIZATION_POLICY_RISK")

    def test_tool_keyword_low_volume_is_not_substituted_by_domain_traffic(self):
        x=row()
        x["keyword_volume"]=1900
        self.assertEqual(gate(x,TODAY.date())["status"],"REJECT_LOW_CORE_NONBRAND_TOOL_KEYWORD_DEMAND")
        x["keyword_volume"]=3000
        self.assertEqual(gate(x,TODAY.date())["status"],"PUBLIC_ORGANIC_AND_NONBRAND_TOOL_EVIDENCE_REVIEW_SERP")

    def test_real_evidence_fixture_zero_unsubstantiated_sites(self):
        p=Path(__file__).resolve().parents[1]/"inputs"/"public-organic-competitors.json"
        data=json.loads(p.read_text(encoding="utf-8"))
        report=build(data,TODAY)
        self.assertEqual(report["public_evidence_count"],10)
        self.assertTrue(report["organic_traffic_numbers_are_public_provider_estimates_not_first_party"])
        self.assertEqual([x["domain"] for x in report["shortlist_for_serp_check"]],[])
        reviewed = next(x for x in report["others"] if x["domain"] == "meloja.com.br")
        self.assertEqual(reviewed["status"], "REJECT_HIGH_KD_WEAK_ADS_NEW_SITE")
        self.assertEqual(reviewed["manual_keyword_review"]["core_kd"], 50)
        self.assertIn("do not re-request", markdown(report))
        self.assertIn("OVERLAPS_USER_EXISTING_SITE_NOT_NEW_PROJECT",
                      {x["status"] for x in report["others"]})
        self.assertIn("REJECT_OUTSIDE_GLOBAL_ORGANIC_TRAFFIC_TARGET",
                      {x["status"] for x in report["others"]})
        expected={
            "countdown-timer.app":"HOLD_UNSTABLE_ORGANIC_TREND",
            "loaderr.to":"REJECT_ADS_MONETIZATION_POLICY_RISK",
            "mouser.mx":"REJECT_LOW_CORE_NONBRAND_TOOL_KEYWORD_DEMAND",
            "calculadoras.uno":"REJECT_LOW_CORE_NONBRAND_TOOL_KEYWORD_DEMAND",
        }
        self.assertEqual({x["domain"]:x["status"] for x in report["others"] if x["domain"] in expected},expected)

if __name__=="__main__":
    unittest.main()
