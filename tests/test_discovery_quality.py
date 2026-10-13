import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from discovery_quality import assess, build, root_domain, markdown
from radar import query_plan

def lead(host,slug,description='',stars=4):
    return {'domain':host,'homepage':'https://'+host,'matching_queries':['test'],
            'repositories':[{'url':'https://github.com/owner/'+slug,'description':description,'stars':stars,'fork':False,'archived':False}]}

class DiscoveryQualityTests(unittest.TestCase):
    def test_avoid_catalogue_masquerading_as_product(self):
        obj=assess(lead('flowmusicai.app','Awesome-AI-Websites-2026','A list of AI tools'))
        self.assertEqual(obj['review_stage'],'SKIP_GITHUB_SOURCE')
        self.assertIn('CATALOG_NOT_TOOL',obj['reasons'])
        self.assertIsNone(obj['organic_monthly_search'])

    def test_avoid_tutorial_classification_as_business(self):
        obj=assess(lead('exampletools.com','calculator-challenge','A bootcamp exercise'))
        self.assertEqual(obj['review_stage'],'SKIP_GITHUB_SOURCE')

    def test_good_tool_has_technical_inspection_not_seo_approval(self):
        obj=assess(lead('sine-wave-generator.com','sine-wave-generator',
                        'An in-browser frequency tool'))
        self.assertEqual(obj['review_stage'],'TECH_LEAD_TO_INSPECT')
        self.assertEqual(obj['seo_status'],'NO_INDEPENDENT_SEO_EVIDENCE')
        self.assertIsNone(obj['nonbrand_clicks'])
        self.assertIsNone(obj['country_traffic'])
        self.assertGreater(obj['quality_heuristic_not_seo_score'],55)

    def test_br_root_domain_and_hosted_subdomain(self):
        self.assertTrue(root_domain('tool.com.br'))
        self.assertTrue(root_domain('tool.mx'))
        self.assertFalse(root_domain('demo.pythonanywhere.com'))
        self.assertFalse(root_domain('any.github.io'))
        self.assertFalse(root_domain('config.meshcentraltools.com'))

    def test_history_and_origin_of_signal(self):
        src={'generated_at_utc':'2026-10-13T10:00:00Z','github_queries_attempted':3,
             'github_failures':[],'github_leads':[lead('sine-wave-generator.com','sine-wave-generator')]}
        report,hist=build(src,{})
        self.assertEqual(report['historical_domains_seen'],1)
        self.assertTrue(report['observations'][0]['is_new_radar_observation'])
        self.assertTrue(report['no_semrush_requests_from_github_alone'])
        again,new=build(src,hist)
        self.assertFalse(again['observations'][0]['is_new_radar_observation'])
        self.assertEqual(new['sine-wave-generator.com']['first_seen'],'2026-10-13')
        self.assertEqual(new['sine-wave-generator.com']['observed_run_count'],2)

    def test_failed_all_sources_preserves_history_and_does_not_imply_zero_demand(self):
        h={'prior.example':{'first_seen':'2026-10-01','last_seen':'2026-10-11','observed_run_count':2}}
        source={'generated_at_utc':'2026-10-13T10:00:00Z','github_queries_attempted':3,
                'github_failures':[{}, {}, {}], 'github_leads':[]}
        report,new=build(source,h)
        self.assertTrue(report['source_outage'])
        self.assertEqual(new,h)
        self.assertIn('数据源故障',markdown(report))
        self.assertEqual(report['priority_to_inspect'],[])

    def test_rotating_pt_es_en_queries(self):
        import datetime
        rows=query_plan(datetime.date(2026,10,13))
        after=query_plan(datetime.date(2026,10,14))
        self.assertEqual([x[0] for x in rows],['pt','es','en'])
        self.assertEqual(len(rows),3)
        self.assertNotEqual(rows,after)
        self.assertEqual(rows,query_plan(datetime.date(2026,10,13)))

if __name__=='__main__':
    unittest.main()
