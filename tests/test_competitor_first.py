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

    def test_known_high_core_kd_hold_is_not_build_or_duplicate_data_request(self):
        x=row()
        x["manual_keyword_review"]={
            "decision":"HOLD_HIGH_CORE_KD_WITHOUT_WEAK_SERP",
            "reviewed_on":"2026-10-13","source":"User Semrush screenshot",
            "core_keyword":"sens converter","core_volume":33100,
            "core_kd":47,"core_cpc_usd":5.36,
            "reason":"KD above cautious entry threshold; no weak SERP evidence.",
            "do_not_request_same_core_kd_again":True,
            "related":[{"keyword":"valorant sens converter","volume":1900,"kd":28}]
        }
        z=build({"snapshots":[x]},TODAY)
        self.assertEqual(z["shortlist_for_serp_check"],[])
        self.assertEqual(z["others"][0]["status"],"HOLD_HIGH_CORE_KD_WITHOUT_WEAK_SERP")
        self.assertIn("Do NOT re-request this core KD",markdown(z))

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

    def test_dated_competitor_sources_strictly_distinguish_cpc_from_earnings(self):
        payload=json.loads((Path(__file__).resolve().parents[1]/"inputs"/"public-organic-competitors.json").read_text(encoding="utf-8"))
        report=build(payload,TODAY)
        fps=next(x for x in report["others"] if x["domain"]=="aiming.pro")
        self.assertEqual(fps["status"],"HOLD_HIGH_CORE_KD_WITHOUT_WEAK_SERP")
        self.assertEqual(fps["manual_keyword_review"]["core_kd"],47)
        self.assertEqual(fps["manual_keyword_review"]["core_cpc_usd"],5.36)
        self.assertTrue(fps["manual_keyword_review"]["do_not_request_same_core_kd_again"])
        self.assertEqual(fps["keyword_cpc_usd_public_snapshot"],5.31)
        self.assertEqual(fps["keyword_position_public_snapshot"],5)
        self.assertIs(fps["country_organic_visits_not_proven"],True)
        self.assertTrue(any("kovaaks" in u for u in fps["competing_tool_urls"]))
        mx=next(x for x in report["shortlist_for_serp_check"] if x["domain"]=="cps-check.com")
        self.assertEqual(mx["keyword_cpc_usd_public_snapshot"],0)
        self.assertEqual(mx["keyword_country"],"MX")
        self.assertEqual(mx["keyword_volume_public_snapshot"],12100)
        other=next(x for x in report["others"] if x["domain"]=="topster.pt")
        self.assertEqual(other["status"],"OVERLAPS_USER_EXISTING_SITE_NOT_NEW_PROJECT")
        self.assertIn("NOT AdSense earnings", markdown(report))

    def test_brazil_dead_pixel_core_tool_ranking_has_proven_search_not_kd(self):
        payload=json.loads((Path(__file__).resolve().parents[1]/"inputs"/"public-organic-competitors.json").read_text(encoding="utf-8"))
        result=build(payload,TODAY)
        px=next(x for x in result["others"] if x["domain"]=="deadpixeltest.org")
        self.assertEqual(px["primary_country"],"BR")
        self.assertEqual(px["status"],"REJECT_HIGH_KD_WITHOUT_WEAK_SERP")
        self.assertEqual(px["manual_keyword_review"]["core_kd"],62)
        self.assertEqual(px["manual_keyword_review"]["us_same_keyword_reference"]["kd"],26)
        self.assertTrue(px["manual_keyword_review"]["do_not_request_same_core_kd_again"])
        self.assertEqual(px["keyword_position_public_snapshot"],2)
        self.assertEqual(px["keyword_volume_public_snapshot"],9900)
        self.assertEqual(px["global_monthly_organic_provider_estimate"],53460)
        self.assertFalse(px["kd_verified"])
        self.assertFalse(px["organic_verified_by_first_party_analytics"])
        self.assertTrue(px["country_organic_visits_not_proven"])

    def test_over_100k_organic_gamepad_comparison_not_pushed_as_site_idea(self):
        payload=json.loads((Path(__file__).resolve().parents[1]/"inputs"/"public-organic-competitors.json").read_text(encoding="utf-8"))
        result=build(payload,TODAY)
        ex=next(x for x in result["others"] if x["domain"]=="gpadtester.com")
        self.assertEqual(ex["status"],"REJECT_OUTSIDE_GLOBAL_ORGANIC_TRAFFIC_TARGET")
        self.assertEqual(ex["global_monthly_organic_provider_estimate"],108710)
        self.assertEqual(ex["keyword"],"gamepad tester")
        self.assertNotIn(ex["domain"],[x["domain"] for x in result["shortlist_for_serp_check"]])

    def test_gif_background_tool_public_evidence_qualifies_for_kd_check_only(self):
        payload=json.loads((Path(__file__).resolve().parents[1]/"inputs"/"public-organic-competitors.json").read_text(encoding="utf-8"))
        result=build(payload,TODAY)
        gif=next(x for x in result["others"] if x["domain"]=="onlinegiftools.com")
        self.assertEqual(gif["keyword"],"remove background from gif")
        self.assertEqual(gif["status"],"HOLD_MIXED_SERP_NO_DIFFERENTIATED_ENTRY")
        self.assertTrue(gif["serp_review_completed"])
        self.assertTrue(gif["serp_low_link_indie_page_at_position_8_only"])
        self.assertEqual(len(gif["manual_serp_review"]["rankings"]),10)
        self.assertEqual(gif["manual_serp_review"]["rankings"][7]["position"],8)
        self.assertEqual(gif["manual_serp_review"]["rankings"][7]["page_referring_domains"],1)
        self.assertFalse(gif["manual_serp_review"]["analysis"]["approved_to_build"])
        self.assertEqual(gif["current_user_supplied_volume"],33100)
        self.assertEqual(gif["current_user_supplied_kd"],37)
        self.assertEqual(gif["current_user_supplied_cpc_usd"],1.73)
        self.assertEqual(gif["keyword_volume_public_snapshot"],22200)
        self.assertIn("DO NOT ask user for the same results again",markdown(result))
        self.assertEqual(gif["keyword_country"],"US")
        self.assertEqual(gif["keyword_position_public_snapshot"],2)
        self.assertEqual(gif["keyword_volume_public_snapshot"],22200)
        self.assertEqual(gif["global_monthly_organic_provider_estimate"],62260)
        self.assertEqual(gif["keyword_cpc_usd_public_snapshot"],1.37)
        self.assertFalse(gif["serp_low_authority_verified"])
        self.assertFalse(gif["organic_verified_by_first_party_analytics"])

    def test_borderline_kd_only_queues_serp_after_full_evidence_gate(self):
        x=row()
        x["manual_keyword_review"]={
            "decision":"BORDERLINE_KD_37_SERP_ONLY",
            "core_keyword":"remove background from gif",
            "core_volume":33100,"core_kd":37,"core_cpc_usd":1.73,
            "source":"Semrush user screenshot Oct13"
        }
        result=build({"snapshots":[x]},TODAY)
        self.assertEqual(len(result["shortlist_for_serp_check"]),1)
        self.assertEqual(result["shortlist_for_serp_check"][0]["status"],"BORDERLINE_KD_SERP_ONLY")
        self.assertIn("ONLY independent Top10 SERP URLs",markdown(result))
        self.assertFalse(result["shortlist_for_serp_check"][0]["organic_verified_by_first_party_analytics"])
        self.assertFalse(result["shortlist_for_serp_check"][0]["serp_low_authority_verified"])
        x["tool_page_publicly_checked"]=False
        r=gate(x,TODAY.date())
        self.assertEqual(r["status"],"REQUIRE_LANDING_PAGE_FUNCTION_REVIEW")

    def test_completed_serp_review_blocks_repeat_lookup_without_pretending_site_is_weak(self):
        x=row()
        x["manual_keyword_review"]={
            "decision":"BORDERLINE_KD_37_SERP_ONLY",
            "core_keyword":"remove background from gif",
            "core_volume":33100,"core_kd":37,"core_cpc_usd":1.73
        }
        x["manual_serp_review"]={
            "reviewed_on":"2026-10-13",
            "rankings":[
                {"position":1,"page_as":54,"page_referring_domains":366},
                {"position":2,"page_as":43,"page_referring_domains":357},
                {"position":8,"page_as":0,"page_referring_domains":1}
            ],
            "analysis":{
                "decision":"HOLD_MIXED_SERP_NO_DIFFERENTIATED_ENTRY",
                "weak_url_position":8,
                "do_not_request_repeat_semrush":True,
                "approved_to_build":False,
                "conclusion":"One low-link tool page, but incumbents have mature free tools."
            }
        }
        r=build({"snapshots":[x]},TODAY)
        self.assertEqual(r["shortlist_for_serp_check"],[])
        entry=r["others"][0]
        self.assertEqual(entry["status"],"HOLD_MIXED_SERP_NO_DIFFERENTIATED_ENTRY")
        self.assertTrue(entry["serp_review_completed"])
        self.assertTrue(entry["serp_low_link_indie_page_at_position_8_only"])
        self.assertFalse(entry["serp_low_authority_verified"])
        self.assertFalse(entry["organic_verified_by_first_party_analytics"])
        self.assertIn("DO NOT ask user for the same results again",markdown(r))
        x["tool_page_publicly_checked"]=False
        self.assertEqual(gate(x,TODAY.date())["status"],"REQUIRE_LANDING_PAGE_FUNCTION_REVIEW")

    def test_ordinary_pixelator_and_morse_code_are_held_not_auto_pushed(self):
        payload=json.loads((Path(__file__).resolve().parents[1]/"inputs"/"public-organic-competitors.json").read_text(encoding="utf-8"))
        result=build(payload,TODAY)
        hosts={x["domain"]:x for x in result["others"]}
        self.assertEqual(hosts["onlinetools.com"]["status"],"HOLD_SATURATED_COMMODITY_TOOL_NO_MOAT")
        self.assertEqual(hosts["onlinetexttools.com"]["status"],"HOLD_SATURATED_COMMODITY_TOOL_NO_MOAT")
        self.assertNotIn("deadpixeltest.org",[x["domain"] for x in result["shortlist_for_serp_check"]])
        self.assertIn("BR",hosts["deadpixeltest.org"]["manual_keyword_review"]["country"])

    def test_real_evidence_fixture_zero_unsubstantiated_sites(self):
        p=Path(__file__).resolve().parents[1]/"inputs"/"public-organic-competitors.json"
        data=json.loads(p.read_text(encoding="utf-8"))
        report=build(data,TODAY)
        self.assertEqual(report["public_evidence_count"],18)
        self.assertTrue(report["organic_traffic_numbers_are_public_provider_estimates_not_first_party"])
        self.assertEqual({x["domain"] for x in report["shortlist_for_serp_check"]},{"cps-check.com"})
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
