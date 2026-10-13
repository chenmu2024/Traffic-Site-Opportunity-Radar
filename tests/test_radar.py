import csv
import json
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from radar import domain, union_groups, evaluate, run, github_discover


class RadarTests(unittest.TestCase):
    def test_domains_safe_and_no_guess_etld(self):
        self.assertEqual(domain('https://www.example.com.br/a'), 'example.com.br')
        for x in ('http://localhost/','http://127.0.0.1','https://user:pw@foo.com','file:///etc/passwd','https://github.com/x'):
            self.assertIsNone(domain(x))

    def test_no_serp_no_fake_evidence(self):
        with tempfile.TemporaryDirectory() as d:
            folder=Path(d)
            (folder/'seeds.json').write_text('{"seed_domains":["example.com"]}',encoding='utf-8')
            result=run(folder,now=datetime(2026,10,13,tzinfo=timezone.utc))
            self.assertEqual(result['serp_candidates'], [])
            self.assertEqual(result['github_leads'], [])
            self.assertFalse(result['seo_provider_metrics_verified_automatically'])

    def test_serp_rank_and_weak_site_evidence(self):
        with tempfile.TemporaryDirectory() as d:
            folder=Path(d)
            with (folder/'serp.csv').open('w',newline='',encoding='utf-8') as f:
                writer=csv.DictWriter(f,fieldnames=['country','keyword','rank','url','observed_on','source','domain_dr','volume','kd','cpc'])
                writer.writeheader()
                writer.writerows([
                    dict(country='BR',keyword='calculadora teste',rank=3,url='https://www.small.example.com.br/tool',observed_on='2026-10-13',source='manual-capture-001',domain_dr=17,volume=1500,kd=20,cpc=0.5),
                    dict(country='BR',keyword='calculadora teste',rank=1,url='https://source.example.br/test',observed_on='2026-10-13',source='manual-capture-001',domain_dr='',volume='',kd='',cpc=''),
                    dict(country='BR',keyword='calculadora teste',rank=4,url='https://bad.example.br',observed_on='2026-10-12',source='old',domain_dr=1,volume=10,kd=10,cpc=0),
                    dict(country='IN',keyword='fake',rank=1,url='https://fake.example',observed_on='2026-10-13',source='bad',domain_dr=1,volume=999,kd=1,cpc=0),
                    dict(country='BR',keyword='missing source',rank=1,url='https://fake.example',observed_on='2026-10-13',source='',domain_dr=1,volume=999,kd=1,cpc=0),
                ])
            (folder/'seeds.json').write_text('{"seed_domains":["source.example.br"]}',encoding='utf-8')
            with (folder/'sites.csv').open('w',newline='',encoding='utf-8') as f:
                writer=csv.DictWriter(f,fieldnames=['domain','country','monthly_organic','source','observed_on'])
                writer.writeheader()
                writer.writerow(dict(domain='small.example.com.br',country='BR',monthly_organic=25000,source='semrush-manual',observed_on='2026-10-13'))
            result=run(folder)
            self.assertEqual(result['serp_keyword_snapshots'],1)
            target=next(x for x in result['serp_candidates'] if x['domain']=='small.example.com.br')
            self.assertEqual(target['status'],'SERP_WEAK_SITE_EVIDENCE')
            self.assertEqual(target['related_to_seed_hops'],1)
            self.assertEqual(target['traffic_user_supplied'][0]['monthly_organic'],25000)
            self.assertIsNone(target['verified_monthly_organic_by_radar'])
            self.assertEqual(target['domain_dr_user_supplied'],17)

    def test_dr_unknown_and_conflict_not_weak(self):
        serp={('MX','tool'): [dict(country='MX',keyword='tool',rank=2,url='https://a.test/x',domain='a.test',dr=14,observed_on='2026-10-13',source='s',volume=None,kd=None),
                               dict(country='MX',keyword='tool',rank=3,url='https://a.test/y',domain='a.test',dr=30,observed_on='2026-10-13',source='s',volume=None,kd=None)]}
        obj=evaluate(serp,{},set(),set())[0]
        self.assertIsNone(obj['domain_dr_user_supplied'])
        self.assertNotEqual(obj['status'],'SERP_WEAK_SITE_EVIDENCE')

    def test_same_country_serp_overlap(self):
        def rows(urls):
            return [dict(url=url,rank=i+1) for i,url in enumerate(urls)]
        x=['https://a.test/one','https://b.test/one','https://c.test/one']
        serps={('BR','calcular'):rows(x),('BR','calculadora'):rows(x),('MX','calcular'):rows(x)}
        groups=union_groups(serps)
        self.assertEqual(sorted(map(len,groups)),[1,2])

    def test_github_signal_not_organic_proof(self):
        class Response:
            def __enter__(self):return self
            def __exit__(self,*args):return False
            def read(self,*a):return self.data
            data=json.dumps({'items':[{'homepage':'https://foo.example/tool','html_url':'https://github.com/a/b','stargazers_count':5,'pushed_at':'2026-10-12'}]}).encode()
        leads,errors=github_discover(fetch=lambda *a,**k: Response())
        self.assertEqual(errors,[])
        self.assertEqual(len(leads),1)
        self.assertEqual(leads[0]['status'],'DISCOVERY_ONLY')
        self.assertIsNone(leads[0]['organic_traffic'])
        self.assertIsNone(leads[0]['kd'])


if __name__=='__main__':unittest.main()
