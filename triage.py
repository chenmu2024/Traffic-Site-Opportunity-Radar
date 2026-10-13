#!/usr/bin/env python3
"""Evidence-first SEO traffic site triage: manual provider inputs, never fake clicks."""
import argparse
import json
from collections import defaultdict
from datetime import date, datetime, timezone
from pathlib import Path
from radar import ROOT, COUNTRIES, clean, domain, load_sites, number, read_csv

REVIEW_FLAGS = {'YES', 'NO', 'UNKNOWN'}
MAX_AGE_DAYS = 90


def load_positions(path, as_of=None):
    as_of = as_of or datetime.now(timezone.utc).date()
    rejected = defaultdict(int)
    dedup = {}
    for row in read_csv(path):
        country = (row.get('country') or '').strip().upper()
        site = domain(row.get('domain'))
        landing = domain(row.get('url'))
        keyword = ' '.join((row.get('keyword') or '').strip().lower().split())
        position = number(row.get('position'), 1, 100)
        source = (row.get('source') or '').strip()
        try:
            observed = date.fromisoformat((row.get('observed_on') or '').strip())
        except ValueError:
            rejected['INVALID_DATE'] += 1
            continue
        if observed > as_of:
            rejected['FUTURE_DATE'] += 1
            continue
        if country not in COUNTRIES or not site or site != landing or not keyword:
            rejected['INVALID_COUNTRY_DOMAIN_OR_KEYWORD'] += 1
            continue
        if position is None or not position.is_integer() or not source:
            rejected['INVALID_POSITION_OR_SOURCE'] += 1
            continue
        brand = (row.get('nonbrand_review') or 'UNKNOWN').strip().upper()
        tool = (row.get('tool_intent_review') or 'UNKNOWN').strip().upper()
        if brand not in REVIEW_FLAGS or tool not in REVIEW_FLAGS:
            rejected['INVALID_REVIEW_FLAG'] += 1
            continue
        record = {
            'country': country, 'domain': site, 'keyword': keyword,
            'url': row['url'].strip(), 'position_user_supplied': int(position),
            'volume_user_supplied': number(row.get('volume')),
            'kd_user_supplied': number(row.get('kd'), 0, 100),
            'cpc_user_supplied': number(row.get('cpc')),
            'observed_on': observed.isoformat(), 'source': clean(source),
            'nonbrand_review': brand, 'tool_intent_review': tool,
            'age_days': (as_of-observed).days, 'evidence_status': 'USER_SUPPLIED_UNAUDITED'
        }
        key = (country, site, keyword)
        old = dedup.get(key)
        if old is None or (record['observed_on'], -record['position_user_supplied']) > (
                old['observed_on'], -old['position_user_supplied']):
            dedup[key] = record
    return sorted(dedup.values(), key=lambda r: (r['country'],r['domain'],r['position_user_supplied'],r['keyword'])), dict(rejected)


def shortlist(rankings, site_traffic, as_of=None):
    as_of = as_of or datetime.now(timezone.utc).date()
    groups = defaultdict(list)
    for row in rankings:
        groups[row['domain'], row['country']].append(row)
    candidates = []
    for (host, country), rows in groups.items():
        fresh = [r for r in rows if r['age_days'] <= MAX_AGE_DAYS]
        qualifying = [r for r in fresh if (
            r['nonbrand_review'] == 'YES' and r['tool_intent_review'] == 'YES'
            and r['position_user_supplied'] <= 20
            and r['volume_user_supplied'] is not None and r['volume_user_supplied'] >= 500
            and r['kd_user_supplied'] is not None and r['kd_user_supplied'] <= 30)]
        traffic = site_traffic.get((host, country))
        traffic_current = bool(traffic and 0 <= (
            as_of-date.fromisoformat(traffic['observed_on'])).days <= MAX_AGE_DAYS)
        in_range = bool(traffic_current and 10000 <= traffic['monthly_organic'] <= 100000)
        if not fresh:
            status = 'STALE_DATA_RECHECK'
        elif any(r['nonbrand_review'] == 'UNKNOWN' or r['tool_intent_review'] == 'UNKNOWN' for r in fresh):
            status = 'MANUAL_INTENT_REVIEW'
        elif not traffic_current:
            status = 'CHECK_DOMAIN_TRAFFIC_BY_COUNTRY'
        elif not in_range:
            status = 'OUTSIDE_TARGET_TRAFFIC_RANGE'
        elif len(qualifying) < 2:
            status = 'CHECK_KEYWORD_DEMAND_AND_SERP'
        else:
            status = 'READY_FOR_FINAL_SERP_REVIEW'
        score = (min(len(qualifying)*20, 40) + (30 if in_range else 0)
                 + (20 if qualifying and min(r['position_user_supplied'] for r in qualifying)<=10 else 0)
                 + (10 if len({r['url'] for r in qualifying})>=2 else 0))
        ordered = sorted(fresh, key=lambda r: (0 if r in qualifying else 1,
                         r['position_user_supplied'], -(r['volume_user_supplied'] or 0), r['keyword']))
        candidates.append({
            'domain': host, 'country': country, 'status': status,
            'priority_heuristic_not_forecast': score,
            'fresh_ranked_keywords': len(fresh),
            'manually_confirmed_qualifying_keywords': len(qualifying),
            'qualifying_distinct_urls': len({r['url'] for r in qualifying}),
            'organic_traffic_user_supplied': traffic if traffic_current else None,
            'organic_traffic_verified_by_radar': None,
            'keyword_evidence_user_supplied': ordered[:8]
        })
    return sorted(candidates,key=lambda r:(r['status']!='READY_FOR_FINAL_SERP_REVIEW',
                    -r['priority_heuristic_not_forecast'], r['country'],r['domain']))


def generate(positions_path=None, sites_path=None, now=None):
    now = now or datetime.now(timezone.utc)
    rankings, rejected = load_positions(positions_path or ROOT/'inputs'/'positions.csv', now.date())
    traffic = load_sites(sites_path or ROOT/'inputs'/'sites.csv')
    candidates = shortlist(rankings, traffic, now.date())
    return {
        'generated_at_utc':now.isoformat(), 'imported_rankings':len(rankings),
        'rejections':rejected, 'reviewed_sites':candidates,
        'ready_for_final_serp_review_count':sum(
            r['status']=='READY_FOR_FINAL_SERP_REVIEW' for r in candidates),
        'organic_traffic_verified_automatically':False,
        'github_leads_promoted_to_seo_evidence':0,
        'note':'All rankings, metrics and review flags are user supplied and unaudited. Final SERP review is mandatory.'
    }


def markdown(data):
    out = ['# SEO 流量站 | 国家级关键词核验工作单','',
           '生成时间：'+data['generated_at_utc'],'',
           '> 所有排名和 SEO 指标均来自人工导入，不由系统独立验证。没有数据不等于流量为零。','',
           '## 最多三个进入最终 SERP 审核的候选','']
    ready = [x for x in data['reviewed_sites'] if x['status']=='READY_FOR_FINAL_SERP_REVIEW']
    if not ready:
        out.append('目前无满足证据门槛的候选；不要盲查 Semrush，也不要依据 GitHub Stars 立项。')
    for n, site in enumerate(ready[:3],1):
        organic=site['organic_traffic_user_supplied']
        out += ['',f"### {n}. {clean(site['domain'])} ({site['country']})",
                f"- 人工记录月自然流量估计：{organic['monthly_organic']:,}；来源：{clean(organic['source'])}；日期：{organic['observed_on']}",
                f"- 满足初筛的非品牌工具关键词：{site['manually_confirmed_qualifying_keywords']}；不同排名 URL：{site['qualifying_distinct_urls']}",
                '- 需要按国家复查的具体关键词与 URL：']
        for k in site['keyword_evidence_user_supplied'][:5]:
            out.append(f"  - {clean(k['keyword'])} | 排名 {k['position_user_supplied']} | Volume {k['volume_user_supplied'] if k['volume_user_supplied'] is not None else '未知'} | KD {k['kd_user_supplied'] if k['kd_user_supplied'] is not None else '未知'} | {clean(k['url'],250)}")
        out.append('- 最终核对：真实 SERP 前十、低权重竞争页、流量来源、广告收益和维护成本。')
    out += ['', '## 尚未通过的数据核验项目', '',
            '| 国家 | 域名 | 核验阶段 | 具体查询词 |','|---|---|---|---|']
    pending = [x for x in data['reviewed_sites'] if x['status']!='READY_FOR_FINAL_SERP_REVIEW']
    if not pending:
        out.append('| — | 暂无 | — | — |')
    for site in pending[:15]:
        terms=', '.join(clean(r['keyword']) for r in site['keyword_evidence_user_supplied'][:3])
        out.append('| '+site['country']+' | '+clean(site['domain'])+' | '+site['status']+' | '+terms+' |')
    out += ['', '## 数据可信度与边界', '',
            '- 国家采用 BR/MX/ES/PT/CL/US/GB；不以印度流量立项。',
            '- 收集：国家 + 精确功能 URL + 非品牌工具关键词 + Volume/KD/CPC + 来源和观察日期。',
            '- 人工复核 YES 才被视为非品牌且有工具使用需求；缺失不自动推断。',
            '- 相近词的搜索量不能简单累加；低 DR 和排名并不能保证我方获得流量。',
            f"- 有效导入关键词数：{data['imported_rankings']}；有候选数据的网站数：{len(data['reviewed_sites'])}。",
            f"- 已通过初筛：{len(ready)}；无效记录计数：{json.dumps(data['rejections'],ensure_ascii=False)}。",
            '- SaaS 相关数据、MRR、收入证据不在本仓库参与计算。','']
    return '\n'.join(out)


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--positions',type=Path,default=ROOT/'inputs'/'positions.csv')
    p.add_argument('--sites',type=Path,default=ROOT/'inputs'/'sites.csv')
    p.add_argument('--output-dir',type=Path,default=ROOT/'reports')
    args=p.parse_args()
    data=generate(args.positions,args.sites)
    args.output_dir.mkdir(parents=True,exist_ok=True)
    (args.output_dir/'triage.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    (args.output_dir/'triage.md').write_text(markdown(data),encoding='utf-8')
    print(f"Traffic triage: {data['imported_rankings']} rankings, {len(data['reviewed_sites'])} sites, {data['ready_for_final_serp_review_count']} final reviews, {sum(data['rejections'].values())} invalid inputs")


if __name__=='__main__':
    main()
