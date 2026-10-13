import csv
import json
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from triage import load_positions, shortlist, generate, markdown

TODAY = datetime(2026,10,13,tzinfo=timezone.utc)
COLUMNS = ['country','domain','keyword','position','url','volume','kd','cpc',
           'observed_on','source','nonbrand_review','tool_intent_review']

def write_csv(path,fields,rows):
    with path.open('w',encoding='utf-8',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)

def item(country='BR',domain='calculadora.example',keyword='calcular lucro',
         position=3,url='https://calculadora.example/lucro',volume=2400,kd=16,cpc=0.2,
         observed_on='2026-10-12',source='manual-semrush-2026-10-12',
         nonbrand_review='YES',tool_intent_review='YES'):
    return dict(country=country,domain=domain,keyword=keyword,position=position,
                url=url,volume=volume,kd=kd,cpc=cpc,observed_on=observed_on,
                source=source,nonbrand_review=nonbrand_review,
                tool_intent_review=tool_intent_review)

class TriageTests(unittest.TestCase):
    def test_empty_is_not_zero_traffic_claim(self):
        with tempfile.TemporaryDirectory() as tmp:
            data=generate(Path(tmp)/'not-found.csv',Path(tmp)/'missing.csv',now=TODAY)
        self.assertEqual(data['ready_for_final_serp_review_count'],0)
        self.assertEqual(data['imported_rankings'],0)
        self.assertFalse(data['organic_traffic_verified_automatically'])
        self.assertEqual(data['github_leads_promoted_to_seo_evidence'],0)
        self.assertIn('不要盲查 Semrush',markdown(data))

    def test_passes_only_with_country_traffic_and_two_reviewed_nonbrand_tools(self):
        with tempfile.TemporaryDirectory() as tmp:
            d=Path(tmp)
            write_csv(d/'positions.csv',COLUMNS,[
                item(),item(keyword='calculadora de margem',position=9,
                            url='https://calculadora.example/margem',volume=1900,kd=21)])
            write_csv(d/'sites.csv',['domain','country','monthly_organic','source','observed_on'],[
                dict(domain='calculadora.example',country='BR',monthly_organic=24000,
                     source='manual-semrush-domain-2026-10-12',observed_on='2026-10-12')])
            data=generate(d/'positions.csv',d/'sites.csv',now=TODAY)
            r=data['reviewed_sites'][0]
            self.assertEqual(r['status'],'READY_FOR_FINAL_SERP_REVIEW')
            self.assertEqual(r['manually_confirmed_qualifying_keywords'],2)
            self.assertEqual(r['qualifying_distinct_urls'],2)
            self.assertEqual(r['organic_traffic_user_supplied']['monthly_organic'],24000)
            self.assertIsNone(r['organic_traffic_verified_by_radar'])
            self.assertIn('calcular lucro',markdown(data))
            self.assertIn('calculadora de margem',markdown(data))

    def test_brand_and_tool_flags_never_inferred(self):
        with tempfile.TemporaryDirectory() as tmp:
            d=Path(tmp)
            write_csv(d/'positions.csv',COLUMNS,[item(nonbrand_review=''),
                       item(keyword='outra ferramenta',tool_intent_review='UNKNOWN')])
            rows,err=load_positions(d/'positions.csv',TODAY.date())
            self.assertEqual(len(rows),2)
            self.assertTrue(all(r['nonbrand_review']!='YES' or r['tool_intent_review']!='YES' for r in rows))
            data=generate(d/'positions.csv',d/'sites.csv',now=TODAY)
            self.assertEqual(data['reviewed_sites'][0]['status'],'MANUAL_INTENT_REVIEW')
            self.assertEqual(data['ready_for_final_serp_review_count'],0)

    def test_no_india_cross_domain_future_or_unattributed(self):
        with tempfile.TemporaryDirectory() as tmp:
            d=Path(tmp)
            write_csv(d/'positions.csv',COLUMNS,[
                item(country='IN'),item(domain='different.example'),
                item(observed_on='2035-01-01'),item(source=''),
                item(keyword='valid one')])
            records,err=load_positions(d/'positions.csv',TODAY.date())
            self.assertEqual(len(records),1)
            self.assertEqual(records[0]['keyword'],'valid one')
            self.assertEqual(sum(err.values()),4)

    def test_new_snapshot_de_duped_and_outdated_never_promoted(self):
        with tempfile.TemporaryDirectory() as tmp:
            d=Path(tmp)
            write_csv(d/'positions.csv',COLUMNS,[
                item(position=1,observed_on='2026-06-01'),
                item(position=8,observed_on='2026-10-12'),
                item(position=4,observed_on='2026-10-12')])
            records,_=load_positions(d/'positions.csv',TODAY.date())
            self.assertEqual(len(records),1)
            self.assertEqual(records[0]['position_user_supplied'],4)
            write_csv(d/'positions.csv',COLUMNS,[
                item(observed_on='2026-01-01'),
                item(keyword='second',observed_on='2026-01-01')])
            write_csv(d/'sites.csv',['domain','country','monthly_organic','source','observed_on'],[
                dict(domain='calculadora.example',country='BR',monthly_organic=24000,
                     source='semrush',observed_on='2026-10-12')])
            r=generate(d/'positions.csv',d/'sites.csv',now=TODAY)['reviewed_sites'][0]
            self.assertEqual(r['status'],'STALE_DATA_RECHECK')

    def test_missing_kd_cannot_qualify_even_with_high_volume(self):
        with tempfile.TemporaryDirectory() as tmp:
            d=Path(tmp)
            write_csv(d/'positions.csv',COLUMNS,[
                item(kd=''),item(keyword='segundo',volume=12000,kd=20)])
            write_csv(d/'sites.csv',['domain','country','monthly_organic','source','observed_on'],[
                dict(domain='calculadora.example',country='BR',monthly_organic=30000,
                     source='manual',observed_on='2026-10-12')])
            data=generate(d/'positions.csv',d/'sites.csv',now=TODAY)
            self.assertEqual(data['reviewed_sites'][0]['manually_confirmed_qualifying_keywords'],1)
            self.assertEqual(data['reviewed_sites'][0]['status'],'CHECK_KEYWORD_DEMAND_AND_SERP')

if __name__=='__main__':
    unittest.main()
