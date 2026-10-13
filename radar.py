#!/usr/bin/env python3
"""Evidence-first traffic-site radar. Standard library; never invents SEO metrics."""
import argparse
import csv
import ipaddress
import json
import os
import re
from collections import defaultdict, deque
from datetime import date, datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlparse
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parent
COUNTRIES = {'BR', 'MX', 'ES', 'PT', 'CL', 'US', 'GB'}
FORBIDDEN = {'facebook.com', 'instagram.com', 'youtube.com', 'linkedin.com',
             'github.com', 'twitter.com', 'x.com', 'tiktok.com', 'play.google.com'}
# Shared hosting/demo and package-index pages are not independent traffic-site competitors.
DISCOVERY_PLATFORM_SUFFIXES = (
    'github.io', 'pages.dev', 'vercel.app', 'netlify.app', 'onrender.com',
    'render.com', 'replit.app', 'repl.co', 'streamlit.app', 'glitch.me',
    'firebaseapp.com', 'web.app', 'appspot.com', 'lovable.app',
)
DISCOVERY_PLATFORM_HOSTS = {'pypi.org', 'npmjs.com', 'huggingface.co', 'codepen.io'}

# Rotate publicly searchable *repo technologies*: language is only a query hint,
# NEVER a claim about country or SEO users. One PT, one ES and one EN query per run.
DISCOVERY_QUERIES = {
    'pt': [
        'calculadora in:name,description stars:3..1500 archived:false',
        'conversor in:name,description stars:3..1500 archived:false',
        'gerador in:name,description stars:3..1500 archived:false',
        'simulador in:name,description stars:3..1500 archived:false',
    ],
    'es': [
        'generador in:name,description stars:3..1500 archived:false',
        'convertidor in:name,description stars:3..1500 archived:false',
        'calculadora in:name,description stars:3..1500 archived:false',
        'herramienta in:name,description stars:3..1500 archived:false',
    ],
    'en': [
        'online generator in:name,description stars:3..1500 archived:false',
        'browser calculator in:name,description stars:3..1500 archived:false',
        'image converter in:name,description stars:3..1500 archived:false',
        'online planner in:name,description stars:3..1500 archived:false',
    ]
}


def query_plan(day=None):
    day = day or datetime.now(timezone.utc).date()
    idx = day.toordinal() % 4
    return [(language, values[idx]) for language, values in DISCOVERY_QUERIES.items()]


QUERIES = [query for _, query in query_plan()]


def domain(value):
    """Canonical *host*, not guessed eTLD+1. No network requests follow these values."""
    raw = (value or '').strip()
    if not raw:
        return None
    try:
        p = urlparse(raw if '://' in raw else 'https://' + raw)
        host = (p.hostname or '').rstrip('.').lower().encode('idna').decode('ascii')
        if p.scheme not in ('http', 'https') or p.username or p.password or p.port not in (None, 80, 443):
            return None
        if not host or host == 'localhost' or not re.fullmatch(r'[a-z0-9.-]+', host):
            return None
        if not '.' in host or '..' in host:
            return None
        try:
            ipaddress.ip_address(host)
            return None
        except ValueError:
            pass
        if host.startswith('www.'):
            host = host[4:]
        if host in FORBIDDEN or host.endswith('.local') or host.endswith('.internal'):
            return None
        return host
    except (ValueError, UnicodeError):
        return None


def number(value, minimum=0, maximum=None):
    if value is None or str(value).strip() == '':
        return None
    try:
        x = float(str(value).strip())
        if x != x or x in (float('inf'), float('-inf')) or x < minimum or (maximum is not None and x > maximum):
            return None
        return x
    except (ValueError, TypeError):
        return None


def read_csv(path):
    if not path.exists():
        return []
    with path.open(encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))


def clean(value, limit=180):
    return str(value or '').replace('|', '/').replace('\n', ' ').replace('\r', ' ')[:limit]


def load_serps(path):
    """Choose the latest snapshot for each country+keyword; reject unverifiable rows."""
    grouped = defaultdict(list)
    for row in read_csv(path):
        country = (row.get('country') or '').strip().upper()
        keyword = ' '.join((row.get('keyword') or '').lower().split())
        host = domain(row.get('url'))
        rank = number(row.get('rank'), 1, 100)
        day = (row.get('observed_on') or '').strip()
        source = (row.get('source') or '').strip()
        if country not in COUNTRIES or not keyword or not host or not rank or not rank.is_integer() or not source:
            continue
        try:
            date.fromisoformat(day)
        except ValueError:
            continue
        grouped[(country, keyword, day)].append({
            'country': country, 'keyword': keyword, 'observed_on': day,
            'url': row['url'].strip(), 'domain': host, 'rank': int(rank),
            'source': clean(source), 'dr': number(row.get('domain_dr'), 0, 100),
            'volume': number(row.get('volume')), 'kd': number(row.get('kd'), 0, 100),
            'cpc': number(row.get('cpc')),
        })
    latest = {}
    for (country, keyword, day), entries in grouped.items():
        key = country, keyword
        if key not in latest or day > latest[key][0]:
            latest[key] = (day, entries)
    result = {}
    for key, (day, entries) in latest.items():
        unique = {}
        for item in sorted(entries, key=lambda x: x['rank']):
            unique.setdefault(item['rank'], item)
        result[key] = list(unique.values())
    return result


def load_sites(path):
    """Optional estimates are always labeled user-supplied, NOT measured by radar."""
    result = {}
    for row in read_csv(path):
        host = domain(row.get('domain'))
        country = (row.get('country') or '').strip().upper()
        traffic = number(row.get('monthly_organic'))
        source = (row.get('source') or '').strip()
        day = (row.get('observed_on') or '').strip()
        try:
            date.fromisoformat(day)
        except ValueError:
            continue
        if host and country in COUNTRIES and traffic is not None and source:
            key = host, country
            if key not in result or day > result[key]['observed_on']:
                result[key] = {'monthly_organic': int(traffic), 'source': clean(source),
                               'observed_on': day, 'status': 'USER_SUPPLIED_UNAUDITED'}
    return result


def union_groups(serps, threshold=0.6):
    """SERP URL Jaccard >= threshold, same country and >=3 observed top-10 URLs."""
    keys = sorted(serps)
    parent = {x: x for x in keys}
    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a
    for i, a in enumerate(keys):
        urls_a = {r['url'].split('#', 1)[0].rstrip('/') for r in serps[a] if r['rank'] <= 10}
        if len(urls_a) < 3:
            continue
        for b in keys[i+1:]:
            if a[0] != b[0]:
                continue
            urls_b = {r['url'].split('#', 1)[0].rstrip('/') for r in serps[b] if r['rank'] <= 10}
            if len(urls_b) < 3:
                continue
            overlap = len(urls_a & urls_b) / len(urls_a | urls_b)
            if overlap >= threshold:
                parent[find(b)] = find(a)
    groups = defaultdict(list)
    for key in keys:
        groups[find(key)].append({'country': key[0], 'keyword': key[1]})
    return sorted(groups.values(), key=lambda g: (-len(g), g[0]['country'], g[0]['keyword']))


def serp_graph(serps, seeds, excluded):
    neighbors = defaultdict(set)
    evidence = defaultdict(list)
    for (country, keyword), rows in serps.items():
        ranked = [r for r in rows if r['rank'] <= 10 and r['domain'] not in excluded]
        hosts = {r['domain'] for r in ranked}
        for row in ranked:
            neighbors[row['domain']].update(hosts - {row['domain']})
            evidence[row['domain']].append(row)
    distance = {}
    queue = deque()
    for seed in sorted(seeds):
        if seed in neighbors and seed not in excluded:
            distance[seed] = 0
            queue.append(seed)
    while queue:
        current = queue.popleft()
        if distance[current] >= 2:
            continue
        for nxt in sorted(neighbors[current]):
            if nxt not in distance:
                distance[nxt] = distance[current] + 1
                queue.append(nxt)
    return evidence, distance


def evaluate(serps, sites, seeds, excluded):
    evidence, distances = serp_graph(serps, seeds, excluded)
    items = []
    for host, rows in evidence.items():
        if host in excluded:
            continue
        top5 = [r for r in rows if r['rank'] <= 5]
        known_dr = {r['dr'] for r in rows if r['dr'] is not None}
        dr = next(iter(known_dr)) if len(known_dr) == 1 else None
        weak = [r for r in top5 if r['dr'] is not None and r['dr'] <= 20]
        weak_valid = bool(weak) and len(known_dr) == 1 and dr <= 20
        sorted_rows = sorted(rows, key=lambda r: (r['rank'], r['country'], r['keyword']))
        regions = sorted(set(r['country'] for r in rows))
        traffic = [{'country': c, **sites[(host, c)]} for c in regions if (host, c) in sites]
        target_range = any(10000 <= t['monthly_organic'] <= 100000 for t in traffic)
        # No score based on unknown volume/KD/revenue. Prioritize only observable SERP evidence.
        score = (35 if weak_valid else 0) + min(len({(r['country'], r['keyword']) for r in top5}) * 5, 25) + (15 if host in distances else 0) + (20 if target_range else 0)
        status = 'SERP_WEAK_SITE_EVIDENCE' if weak_valid else 'SERP_OBSERVED_DR_UNKNOWN_OR_HIGH'
        items.append({'domain': host, 'status': status, 'priority_score_heuristic': score,
                      'related_to_seed_hops': distances.get(host), 'countries': regions,
                      'top5_keyword_count': len({(r['country'], r['keyword']) for r in top5}),
                      'distinct_serp_keywords': len({(r['country'], r['keyword']) for r in rows}),
                      'domain_dr_user_supplied': dr, 'dr_conflict_or_missing': len(known_dr) != 1,
                      'verified_monthly_organic_by_radar': None, 'traffic_user_supplied': traffic,
                      'target_10k_100k_user_supplied': target_range,
                      'ranking_examples': [{'country': r['country'], 'keyword': r['keyword'], 'rank': r['rank'],
                                            'url': r['url'], 'observed_on': r['observed_on'], 'source': r['source'],
                                            'volume_user_supplied': r['volume'], 'kd_user_supplied': r['kd']}
                                           for r in sorted_rows[:5]],
                      'manual_next_step': 'Check Semrush Organic Research Pages + Positions by country; capture screenshot/export and verify non-brand functional URL traffic, DR, CPC, trends.'})
    return sorted(items, key=lambda x: (-x['priority_score_heuristic'], -x['top5_keyword_count'], x['domain']))


def github_discover(token=None, fetch=None):
    """GitHub project homepage hints only: *no* evidence of search traffic, rankings or revenue."""
    fetch = fetch or urlopen
    results, failures = {}, []
    for query in QUERIES:
        # GitHub default Best Match works better than sorting only by recent updates.
        url = 'https://api.github.com/search/repositories?q=' + quote(query) + '&per_page=40'
        headers = {'Accept': 'application/vnd.github+json', 'User-Agent': 'TrafficSiteRadar/1.0'}
        if token:
            headers['Authorization'] = 'Bearer ' + token
        try:
            with fetch(Request(url, headers=headers), timeout=12) as response:
                payload = json.load(response)
            for repo in payload.get('items', []):
                if repo.get('archived') or repo.get('fork'):
                    continue
                host = domain(repo.get('homepage'))
                if not host or host in DISCOVERY_PLATFORM_HOSTS or any(host == s or host.endswith('.' + s) for s in DISCOVERY_PLATFORM_SUFFIXES):
                    continue
                record = results.setdefault(host, {'domain': host, 'homepage': repo['homepage'],
                    'source': 'PUBLIC_GITHUB_REPOSITORY_HOMEPAGE', 'status': 'DISCOVERY_ONLY',
                    'organic_traffic': None, 'domain_dr': None, 'kd': None, 'cpc': None,
                    'repositories': [], 'matching_queries': []})
                record['repositories'].append({'url': repo.get('html_url'), 'stars': repo.get('stargazers_count'),
                                                'updated_at': repo.get('pushed_at'), 'name': repo.get('name'),
                                                'description': (repo.get('description') or '')[:220],
                                                'fork': bool(repo.get('fork')), 'archived': bool(repo.get('archived'))})
                if query not in record['matching_queries']:
                    record['matching_queries'].append(query)
        except (HTTPError, URLError, OSError, ValueError, KeyError, TimeoutError) as err:
            failures.append({'query': query, 'error_type': type(err).__name__})
    return sorted(results.values(), key=lambda v: (-len(v['matching_queries']), v['domain'])), failures


def report_markdown(data):
    lines = ['# SEO 流量站机会雷达 · ' + data['generated_at_utc'][:10], '',
             '> GitHub 主页是网站发现线索，不代表 Google 自然流量。SERP / DR / Volume 数据均来自人工录入，尚未经过系统独立审计。',
             '> 没有证据不得编造 DR、KD、CPC、排名或月流量。只推荐下一步人工验证，不自动建站。', '',
             '## 竞品扩散和弱站 SERP 机会', '',
             '| 域名 | 阶段 | 竞争证据 | 种子距离 | 月自然流量 | 下一步 |', '|---|---|---|---:|---|---|']
    if not data['serp_candidates']:
        lines.append('| 暂无可验证 SERP 导入 | 待人工导入 | — | — | 未知 | 填写 inputs/serp.csv 的国家、关键词、排名 URL、来源、日期 |')
    for r in data['serp_candidates'][:20]:
        ex = r['ranking_examples'][0]
        tr = '; '.join(f"{t['country']} {t['monthly_organic']:,} (用户录入)" for t in r['traffic_user_supplied']) or '未知'
        lines.append('| ' + clean(r['domain']) + ' | ' + clean(r['status']) + ' | ' +
                     clean(f"{ex['country']} {ex['keyword']} #{ex['rank']} / DR={r['domain_dr_user_supplied'] if r['domain_dr_user_supplied'] is not None else '未知'}") +
                     ' | ' + ('—' if r['related_to_seed_hops'] is None else str(r['related_to_seed_hops'])) +
                     ' | ' + tr + ' | 查看排名 URL，核对非品牌工具页及国家 |')
    lines += ['', '## 同意图关键词聚类（SERP 前10 URL Jaccard ≥ 0.6）', '']
    clusters = [c for c in data['clusters'] if len(c) >= 2]
    if not clusters:
        lines.append('没有充足的相同国家 SERP 快照可用于自动聚类（每词至少3个可比 URL）。')
    for c in clusters[:15]:
        lines.append('- ' + clean(c[0]['country']) + '：' + ' / '.join(clean(x['keyword']) for x in c))
    lines += ['', '## 免费 GitHub 发现的工具网站（未经 SEO 验证）', '',
              '| 网站 | 开源实现参考 | 结论 |', '|---|---|---|']
    if not data['github_leads']:
        lines.append('| 暂无合格外部主页或未执行网络抓取 | — | 不代表没有市场机会 |')
    for item in data['github_leads'][:20]:
        ref = item['repositories'][0].get('url') or ''
        lines.append('| ' + clean(item['domain']) + ' | ' + clean(ref) + ' | 仅发现线索：需先核实真实流量和功能 URL |')
    lines += ['', '## 采集质量及验证指引', '',
              '- GitHub 查询失败：' + str(len(data['github_failures'])) + '/' + str(data['github_queries_attempted']) + '；失败不表示候选为零。',
              '- 检查 Semrush：目标国家的 Organic Research → Pages + Positions；保存非品牌关键词、URL、日期、Volume、KD、自然流量估计和来源。',
              '- 查询 DR 请单独注明 Ahrefs/其他服务与测量日期；不同来源 DR 不混用。',
              '- 仅 GitHub 网站主页、Sitemap、Google 收录或弱 DR 均**不能**单独证明有自然搜索流量。',
              '- 不纳入以印度市场为主要依据的候选；仅使用仓库内已指定的目标国家。',
              '- 真实月自然流量目标为10,000–100,000，未核实项保留未知。', '']
    return '\n'.join(lines)


def run(inputs=ROOT / 'inputs', live_github=False, token=None, fetch=None, now=None):
    config_path = inputs / 'seeds.json'
    cfg = json.loads(config_path.read_text(encoding='utf-8')) if config_path.exists() else {}
    seeds = {d for s in cfg.get('seed_domains', []) if (d := domain(s))}
    excluded = {d for s in cfg.get('excluded_domains', []) if (d := domain(s))}
    serps = load_serps(inputs / 'serp.csv')
    sites = load_sites(inputs / 'sites.csv')
    found, failures = github_discover(token=token, fetch=fetch) if live_github else ([], [])
    # Do not send search-provider data or URLs to external endpoints other than GitHub itself.
    seen = {r['domain'] for r in evaluate(serps, sites, seeds, excluded)}
    found = [x for x in found if x['domain'] not in excluded and x['domain'] not in seen]
    now = now or datetime.now(timezone.utc)
    return {'generated_at_utc': now.isoformat(), 'target_countries': sorted(COUNTRIES),
            'seed_domains': sorted(seeds), 'serp_keyword_snapshots': len(serps),
            'serp_candidates': evaluate(serps, sites, seeds, excluded),
            'clusters': union_groups(serps), 'github_leads': found,
            'github_queries_attempted': len(QUERIES) if live_github else 0,
            'github_query_languages': ['pt','es','en'] if live_github else [],
            'github_queries_used': QUERIES if live_github else [],
            'github_failures': failures, 'seo_provider_metrics_verified_automatically': False,
            'note': 'No Google rank, traffic, DR, KD or CPC are derived from GitHub. Manual SERP metrics are user supplied and unaudited.'}


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--github-live', action='store_true', help='3 rotating public GitHub Search requests (PT/ES/EN)')
    p.add_argument('--input-dir', type=Path, default=ROOT / 'inputs')
    p.add_argument('--output-dir', type=Path, default=ROOT / 'reports')
    args = p.parse_args()
    report = run(args.input_dir, live_github=args.github_live, token=os.getenv('GITHUB_TOKEN'))
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / 'latest.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    (args.output_dir / 'latest.md').write_text(report_markdown(report), encoding='utf-8')
    print(f"Traffic radar: {len(report['serp_candidates'])} SERP candidates, {len(report['github_leads'])} unverified GitHub homepages; GitHub query failures {len(report['github_failures'])}")


if __name__ == '__main__':
    main()
