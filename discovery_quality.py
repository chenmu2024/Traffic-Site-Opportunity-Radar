#!/usr/bin/env python3
"""Free GitHub discovery triage: code/project evidence is never organic SEO proof."""
import argparse
import json
import re
from collections import Counter
from datetime import date, datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

from radar import ROOT, clean, domain

CATALOG_TERMS = ('awesome-', 'awesome_', 'directory', 'curated-list', 'tool-list',
                 'list-of-', '1000-tools', 'best-tools', 'websites-list')
EXERCISE_TERMS = ('challenge', 'desafio', 'tutorial', 'assignment', 'bootcamp', 'coding-exercise',
                  'course-project', 'beginner-project', 'udemy', 'codecademy', 'odin-project')
TOOL_TERMS = ('calculator', 'calculadora', 'calculateur', 'calculate', 'calc-', 'converter',
              'conversor', 'convertidor', 'conversion', 'generador', 'gerador', 'generator',
              'simulador', 'simulator', 'formatter', 'formatador', 'validator',
              'validador', 'visualizer', 'visualizador', 'planner', 'planificador',
              'contador', 'counter', 'font', 'fonts', 'geometry', 'geometria', 'diagram')
PLATFORM_SUFFIXES = ('pythonanywhere.com', 'replit.dev', 'surge.sh', 'fly.dev',
                     'herokuapp.com', 'railway.app', 'workers.dev', 'vercel.app',
                     'pages.dev', 'github.io', 'netlify.app', 'streamlit.app')
ROOT_COUNTRY_SUFFIXES = ('.com.br', '.com.mx', '.org.mx', '.com.ar', '.com.pt',
                         '.co.uk', '.com.co', '.com.pe', '.com.cl')


def parts_from_github(url):
    p = urlparse(url or '')
    chunks = [x for x in p.path.split('/') if x]
    if p.hostname != 'github.com' or len(chunks) < 2:
        return '', ''
    return chunks[0].lower(), chunks[1].lower()


def root_domain(host):
    """Simple presentation heuristic, not public-suffix parsing, canonicalization or DR."""
    pieces = (host or '').split('.')
    if not host or len(pieces) < 2:
        return False
    if any(host.endswith(suffix) for suffix in PLATFORM_SUFFIXES):
        return False
    extra = 1 if any(host.endswith(x) for x in ROOT_COUNTRY_SUFFIXES) else 0
    return len(pieces) == 2 + extra


def assess(lead):
    """Use observable GitHub metadata only; this is *not* an SEO opportunity score."""
    name = lead.get('domain') or ''
    descs = []
    reasons = []
    best = -999
    flags = Counter()
    for rep in lead.get('repositories', []):
        owner, slug = parts_from_github(rep.get('url', ''))
        description = (rep.get('description') or '').lower()
        combined = (slug + ' ' + description).lower()
        bad_catalog = any(token in slug for token in CATALOG_TERMS) or (
            'awesome' in slug and ('list' in description or 'websites' in description))
        bad_exercise = any(token in combined for token in EXERCISE_TERMS)
        relevance = any(x in combined for x in TOOL_TERMS)
        if bad_catalog:
            flags['CATALOG_NOT_TOOL'] += 1
            continue
        if bad_exercise:
            flags['TUTORIAL_OR_COURSE'] += 1
            continue
        if rep.get('archived') or rep.get('fork'):
            flags['ARCHIVED_OR_FORK'] += 1
            continue
        score = 0
        if relevance:
            score += 35
        else:
            flags['TOOL_PURPOSE_NOT_CLEAR'] += 1
        if root_domain(name):
            score += 20
        else:
            flags['SHARED_HOST_OR_SUBDOMAIN_REQUIRES_REVIEW'] += 1
        # Project slug and site host signal product-to-website mapping only.
        s_tokens = {s for s in re.split(r'[^a-z0-9]+', slug) if len(s) >= 5}
        h_tokens = {s for s in re.split(r'[^a-z0-9]+', name) if len(s) >= 5}
        if s_tokens & h_tokens:
            score += 15
        if rep.get('stars') is not None:
            score += 5  # Existence of public code only, never usage or SEO
        if description:
            score += 10
        if len(lead.get('matching_queries', [])) >= 2:
            score += 5
        best = max(score, best)
    if best < 0:
        state = 'SKIP_GITHUB_SOURCE'
        reasons = sorted(flags) or ['NO_USABLE_REPO_METADATA']
        score = 0
    else:
        score = best
        state = 'TECH_LEAD_TO_INSPECT' if score >= 55 else 'LOW_PRIORITY_TECH_LEAD'
        reasons = sorted(flags)
        if not reasons:
            reasons = ['GITHUB_CODE_ONLY_NO_SEO_EVIDENCE']
    return {'domain': name, 'homepage': lead.get('homepage'), 'review_stage': state,
            'source': 'PUBLIC_GITHUB_REPOSITORY', 'quality_heuristic_not_seo_score': score,
            'reasons': reasons, 'repositories': lead.get('repositories', [])[:3],
            'query_language_not_market': lead.get('matching_queries', []),
            'seo_status': 'NO_INDEPENDENT_SEO_EVIDENCE',
            'organic_monthly_search': None, 'nonbrand_clicks': None,
            'kd': None, 'cpc': None, 'country_traffic': None,
            'next_action': ('Inspect actual interactive utility page and locate independent '
                            'nonbrand country-specific SEO evidence before requesting Semrush.')}


def build(source, history=None):
    previous = history or {}
    day = (source.get('generated_at_utc') or '')[:10]
    try:
        date.fromisoformat(day)
    except ValueError:
        day = datetime.now(timezone.utc).date().isoformat()
    attempted = source.get('github_queries_attempted', 0)
    failures = source.get('github_failures', [])
    outage = bool(attempted and len(failures) == attempted)
    seen = dict(previous)
    assessed = []
    for lead in source.get('github_leads', []):
        host = domain(lead.get('domain'))
        if not host:
            continue
        item = assess(lead)
        prev = seen.get(host, {})
        first_seen = prev.get('first_seen') or day
        item['first_seen_in_radar'] = first_seen
        item['is_new_radar_observation'] = not bool(prev)
        item['last_seen_in_radar'] = day
        seen[host] = {
            'first_seen': first_seen, 'last_seen': day,
            'observed_run_count': int(prev.get('observed_run_count', 0)) + 1
        }
        assessed.append(item)
    priority = {'TECH_LEAD_TO_INSPECT': 0, 'LOW_PRIORITY_TECH_LEAD': 1,
                'SKIP_GITHUB_SOURCE': 2}
    assessed.sort(key=lambda x: (priority[x['review_stage']],
                                 -x['quality_heuristic_not_seo_score'], x['domain']))
    counts = dict(Counter(x['review_stage'] for x in assessed))
    return {
        'generated_at_utc': source.get('generated_at_utc'),
        'source_outage': outage, 'github_search_partial': bool(failures),
        'github_query_attempts': attempted, 'github_query_errors': len(failures),
        'observations': assessed, 'priority_to_inspect': [
            x for x in assessed if x['review_stage'] == 'TECH_LEAD_TO_INSPECT'][:5]],
        'stage_counts': counts, 'historical_domains_seen': len(seen),
        'no_semrush_requests_from_github_alone': True,
        'organic_traffic_verified_automatically': False,
        'data_quality_statement': 'GitHub homepage and stars do not verify Google clicks or traffic. '
                                  'These observations are for web-product inspection, NOT Semrush queue.',
    }, (previous if outage else seen)


def markdown(report):
    lines = ['# 上游发现质量报告 · GitHub 技术线索（不是流量证据）', '',
             '生成时间：'+str(report['generated_at_utc']), '',
             '**结论：本模块不会把 GitHub 仓库、Stars 或主页自动判为有自然流量的站点。**',
             '**不要直接查本页的 Semrush：必须先核实真实工具页和非品牌排名证据。**', '']
    if report['source_outage']:
        lines += ['**数据源故障**：所有 GitHub 搜索均失败，本次不能据此判断有没有机会。', '']
    lines += ['## 值得先检查实际工具页的技术线索（最多5项）', '']
    if not report['priority_to_inspect']:
        lines.append('暂无足够吻合的独立工具线索；不要用无关仓库填满推荐数。')
    for entry in report['priority_to_inspect']:
        source = entry['repositories'][0].get('url', '') if entry['repositories'] else ''
        lines += ['- ['+clean(entry['domain'])+']('+clean(entry['homepage'],300)+')：'
                  +' [代码出处]('+clean(source,300)+')；'
                  +'阶段：**需检查实际工具页**；流量、KD、CPC均未知。'
                  +' 需要先确认产品与仓库确实对应，然后寻找具体非品牌排名页面。']
    lines += ['', '## 其他低信号线索及过滤', '',
              '| 网站 | 技术线索阶段 | 原因 |',
              '|---|---|---|']
    for entry in report['observations']:
        if entry['review_stage'] != 'TECH_LEAD_TO_INSPECT':
            lines.append('| '+clean(entry['domain'])+' | '+entry['review_stage']+
                         ' | '+clean(', '.join(entry['reasons']),220)+' |')
    if all(x['review_stage']=='TECH_LEAD_TO_INSPECT' for x in report['observations']):
        lines.append('| — | 无其他线索 | — |')
    lines += ['', '## 数据健康与后续动作', '',
              f"- 本次技术线索：{len(report['observations'])}；质量分层：{json.dumps(report['stage_counts'],ensure_ascii=False)}。",
              f"- GitHub 查询失败：{report['github_query_errors']}/{report['github_query_attempts']}；所有请求失败时不会覆写历史计数。",
              f"- 雷达观察过的不同站点累计：{report['historical_domains_seen']}（不是其 SEO 流量，也不是新词量）。",
              '- **何时需要 Semrush**：只有找到了具体国家的非品牌工具排名入口、目标站功能 URL，以及可初步核查的竞品后，才按国家、域名、关键词列出查询清单。',
              '- 不能根据 GitHub 活跃度、仓库 Stars 或技术评分判断月自然流量 1万–10万；缺失保持未知。',
              '- 这条发现通道与 SaaS 收入雷达完全独立。', '']
    return '\n'.join(lines)


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--source', type=Path, default=ROOT/'reports'/'latest.json')
    p.add_argument('--history', type=Path, default=ROOT/'data'/'site-history.json')
    p.add_argument('--output-dir', type=Path, default=ROOT/'reports')
    args = p.parse_args()
    report = json.loads(args.source.read_text(encoding='utf-8'))
    history = json.loads(args.history.read_text(encoding='utf-8')) if args.history.exists() else {}
    summary, updated = build(report, history)
    args.output_dir.mkdir(parents=True,exist_ok=True)
    args.history.parent.mkdir(parents=True,exist_ok=True)
    (args.output_dir/'discovery-quality.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    (args.output_dir/'discovery-quality.md').write_text(markdown(summary),encoding='utf-8')
    if not summary['source_outage']:
        args.history.write_text(json.dumps(updated,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(f"Discovery: {len(summary['observations'])} GH signals; {len(summary['priority_to_inspect'])} site-inspection candidates; 0 automatic verified organic-traffic claims.")


if __name__ == '__main__':
    main()
