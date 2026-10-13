import csv
import json
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from demand_gate import build, evaluate, load_metrics, markdown

NOW=datetime(2026,10,13,12,0,tzinfo=timezone.utc)
def candidate():
    return {"id":"br_tool","country":"BR","name":"Test tool",
            "core_keyword":"calculadora de resina epóxi",
            "supporting_keywords":["calculadora de resina para molde"]}
def metric(keyword,volume=3200,kd=20,country="BR"):
    return {"country":country,"keyword":keyword,"monthly_volume_user_supplied":volume,
            "kd_user_supplied":kd,"cpc_user_supplied":0.1,
            "source":"manual-Semrush","observed_on":"2026-10-13"}
def run_gate(core=None,support=None):
    data={}
    if core:data[("BR",candidate()["core_keyword"])]=core
    if support:data[("BR",candidate()["supporting_keywords"][0])]=support
    return evaluate([candidate()],data)[0]

class DemandGateTests(unittest.TestCase):
    def test_missing_metrics_not_assumed_zero(self):
        result=run_gate()
        self.assertEqual(result["stage"],"NEEDS_EXACT_CORE_VOLUME")
        self.assertIsNone(result["core_metric"])
        self.assertIsNone(result["organic_monthly_traffic_verified"])
    def test_insufficient_primary_demand_blocks_more_queries(self):
        result=run_gate(core=metric(candidate()["core_keyword"],volume=170))
        self.assertEqual(result["stage"],"REJECT_LOW_CORE_TOOL_DEMAND")
        self.assertIn("Do not request",result["next_action"])
    def test_high_demand_low_kd_requests_support_first(self):
        result=run_gate(core=metric(candidate()["core_keyword"],volume=8000,kd=18))
        self.assertEqual(result["stage"],"NEEDS_SUPPORTING_VOLUME")
    def test_high_core_kd_stops_no_wild_traffic_claim(self):
        result=run_gate(core=metric(candidate()["core_keyword"],volume=8000,kd=52))
        self.assertEqual(result["stage"],"HOLD_HIGH_KD")
    def test_need_support_data_before_domain_research(self):
        result=run_gate(core=metric(candidate()["core_keyword"]),
                        support=metric(candidate()["supporting_keywords"][0],volume=100,kd=20))
        self.assertEqual(result["stage"],"REJECT_INSUFFICIENT_SUPPORTING_DEMAND")
    def test_sufficient_corroborated_tool_demand_still_not_traffic_proof(self):
        result=run_gate(core=metric(candidate()["core_keyword"]),
                        support=metric(candidate()["supporting_keywords"][0],volume=1100,kd=20))
        self.assertEqual(result["stage"],"READY_FOR_COMPETITOR_ORGANIC_REVIEW")
        self.assertIsNone(result["organic_monthly_traffic_verified"])
    def test_future_stale_and_unsupported_country_rejected(self):
        with tempfile.TemporaryDirectory() as root:
            path=Path(root)/"metrics.csv"
            with path.open("w",encoding="utf-8",newline="") as file:
                wr=csv.DictWriter(file,fieldnames=["country","keyword","volume","kd","cpc","observed_on","source"])
                wr.writeheader()
                wr.writerow({"country":"IN","keyword":"x","volume":100,"kd":1,"cpc":1,"observed_on":"2026-10-13","source":"test"})
                wr.writerow({"country":"BR","keyword":"future","volume":100,"kd":1,"cpc":1,"observed_on":"2027-10-13","source":"test"})
                wr.writerow({"country":"BR","keyword":"old","volume":100,"kd":1,"cpc":1,"observed_on":"2025-10-13","source":"test"})
                wr.writerow({"country":"BR","keyword":"verified? no","volume":2400,"kd":"","cpc":"","observed_on":"2026-10-13","source":"test"})
            data,rejected=load_metrics(path,NOW.date())
            self.assertEqual(len(data),1)
            self.assertEqual(len(rejected),3)
    def test_real_empty_files_wait_for_user(self):
        with tempfile.TemporaryDirectory() as tmp:
            base=Path(tmp)
            (base/"candidates.json").write_text(json.dumps({"candidates":[candidate()]}),encoding="utf-8")
            (base/"metrics.csv").write_text("country,keyword,volume,kd,cpc,observed_on,source\n",encoding="utf-8")
            x=build(base/"candidates.json",base/"metrics.csv",now=NOW)
            self.assertEqual(x["metrics_records"],0)
            self.assertEqual(x["candidates"][0]["stage"],"NEEDS_EXACT_CORE_VOLUME")
            self.assertIn("calculadora de resina",markdown(x))
if __name__=="__main__":
    unittest.main()
