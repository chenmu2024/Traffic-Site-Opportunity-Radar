#!/usr/bin/env python3
"""Core tool-intent keyword demand gate BEFORE competitor traffic verification.
Human-supplied Semrush keyword metrics only; never infer from Google results.
"""
import argparse
import csv
import json
from datetime import date, datetime, timezone
from pathlib import Path
from radar import ROOT, COUNTRIES, clean, number

CORE_MIN_VOLUME = 3000
SUPPORT_MIN_VOLUME = 1000
KD_LIMIT = 35
MAX_AGE_DAYS = 90

def keyword_id(text):
    return " ".join((text or "").casefold().split())

def load_metrics(path, as_of):
    indexed = {}
    rejected = {}
    if not path.exists():
        return indexed, rejected
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader=csv.DictReader(handle)
        for line,row in enumerate(reader,2):
            country=(row.get("country") or "").strip().upper()
            keyword=keyword_id(row.get("keyword"))
            volume=number(row.get("volume"),0)
            kd=number(row.get("kd"),0,100)
            cpc=number(row.get("cpc"),0)
            source=(row.get("source") or "").strip()
            try:
                day=date.fromisoformat((row.get("observed_on") or "").strip())
            except ValueError:
                rejected[str(line)]="INVALID_DATE"
                continue
            if country not in COUNTRIES or not keyword or not source or volume is None or volume != int(volume):
                rejected[str(line)]="MISSING_COUNTRY_KEYWORD_VOLUME_OR_SOURCE"
                continue
            if day>as_of:
                rejected[str(line)]="FUTURE_DATED"
                continue
            if (as_of-day).days>MAX_AGE_DAYS:
                rejected[str(line)]="STALE_DATA"
                continue
            key=(country,keyword)
            value={"country":country,"keyword":keyword,"monthly_volume_user_supplied":int(volume),
                   "kd_user_supplied":kd,"cpc_user_supplied":cpc,
                   "source":clean(source,240),"observed_on":day.isoformat(),
                   "evidence_status":"USER_SUPPLIED_UNAUDITED"}
            if key not in indexed or day.isoformat()>indexed[key]["observed_on"]:
                indexed[key]=value
    return indexed,rejected

def evaluate(candidates,metrics):
    """Do not estimate combined/synonymous volume or link keyword evidence to organic visits."""
    reports=[]
    for item in candidates:
        country=item["country"]
        if country not in COUNTRIES:
            continue
        core_key=(country,keyword_id(item["core_keyword"]))
        core=metrics.get(core_key)
        supports=[metrics.get((country,keyword_id(x))) for x in item.get("supporting_keywords",[])]
        supports=[x for x in supports if x is not None]
        support_pass=[r for r in supports if r["monthly_volume_user_supplied"]>=SUPPORT_MIN_VOLUME
                      and r["kd_user_supplied"] is not None and r["kd_user_supplied"]<=KD_LIMIT]
        if core is None:
            state="NEEDS_EXACT_CORE_VOLUME"
            action="Check ONLY the core keyword Volume and KD in the specified country."
        elif core["monthly_volume_user_supplied"]<CORE_MIN_VOLUME:
            state="REJECT_LOW_CORE_TOOL_DEMAND"
            action="Do not request competitor traffic or supporting keywords for this hypothesis."
        elif core["kd_user_supplied"] is None:
            state="NEEDS_CORE_KD"
            action="Core demand is nontrivial; request exact KD in same country and date."
        elif core["kd_user_supplied"]>KD_LIMIT:
            state="HOLD_HIGH_KD"
            action="Do not allocate a build; review tool-specific long tails only if independent evidence justifies it."
        elif not supports:
            state="NEEDS_SUPPORTING_VOLUME"
            action="Core passed: now check 1-2 exact supporting tool-use keywords in the same country."
        elif support_pass:
            state="READY_FOR_COMPETITOR_ORGANIC_REVIEW"
            action="Check 1-2 actual functional competitors: Organic Research Pages/Positions by country; nonbrand functional URL traffic must be verified."
        elif any(x["kd_user_supplied"] is None for x in supports):
            state="NEEDS_SUPPORTING_KD"
            action="Check supporting-keyword KD; never infer missing difficulty."
        else:
            state="REJECT_INSUFFICIENT_SUPPORTING_DEMAND"
            action="Do not request competitor traffic under current narrow tool-intent terms."
        reports.append({"id":item["id"],"name":item["name"],"country":country,
                       "stage":state,"core_keyword":item["core_keyword"],
                       "core_metric":core,"supporting_keywords":item.get("supporting_keywords",[]),
                       "supporting_metrics":supports,
                       "competitors_public_only":item.get("observed_competitors",[]),
                       "organic_monthly_traffic_verified":None,"next_action":action})
    return reports

def build(candidates_path,metrics_path,now=None):
    now=now or datetime.now(timezone.utc)
    payload=json.loads(candidates_path.read_text(encoding="utf-8"))
    metrics,rejected=load_metrics(metrics_path,now.date())
    evaluations=evaluate(payload["candidates"],metrics)
    return {"generated_at_utc":now.isoformat(),
            "policy":"CORE_TOOL_DEMAND_BEFORE_COMPETITOR_TRAFFIC",
            "thresholds_heuristic_not_market_data":{"core_min_volume":CORE_MIN_VOLUME,
                "supporting_min_volume":SUPPORT_MIN_VOLUME,"kd_max":KD_LIMIT,"age_days_max":MAX_AGE_DAYS},
            "candidate_count":len(evaluations),"metrics_records":len(metrics),
            "invalid_records":rejected,"candidates":evaluations,
            "any_organic_traffic_verified_automatically":False,
            "note":"Country Volume and KD are solely manually supplied Semrush metrics; public competitor URLs only verify that a tool page exists. No synonym Volume aggregation."}

def markdown(data):
    out=["# 工具词需求前置筛选 · 流量站雷达","",
         "生成时间："+data["generated_at_utc"],"",
         "> 优先调查真实工具使用词。没有 Semrush 数据则保留未知，不能把新闻/资讯搜索量当作工具使用需求。","",
         "## 需要核查的准确关键词","",
         "| 市场 | 产品方向 | 核心关键词 | Volume | KD | 阶段 |",
         "|---|---|---|---:|---:|---|"]
    for c in data["candidates"]:
        m=c["core_metric"]
        volume=m["monthly_volume_user_supplied"] if m else "未知"
        kd=m["kd_user_supplied"] if m and m["kd_user_supplied"] is not None else "未知"
        out.append("| "+c["country"]+" | "+clean(c["name"])+" | `"+clean(c["core_keyword"])+"` | "+str(volume)+" | "+str(kd)+" | "+c["stage"]+" |")
    out+=["","## 查询顺序","",
          "先查每个国家核心工具词的 Volume/KD；弱需求方向直接拒绝，只有通过前置门槛才核对辅助词和竞品功能页自然流量。",""]
    for c in data["candidates"]:
        out.append("- "+c["country"]+" **"+c["name"]+"**："+c["next_action"]+" 辅助词："+
                   "、".join("`"+clean(x)+"`" for x in c["supporting_keywords"]))
    out+=["","## 证据纪律","",
          "- 月自然流量10k–100k目标不能由关键词搜索量直接推算；工具排名URL需随后单独验证。",
          "- 初筛 3,000 搜索量和 KD 35 是研究资源分配的启发式阈值，不是市场真实数据或普适立项公式。",
          "- 同义词不得简单相加；核心关键词需求不足就淘汰，除非出现新的独立证据。",
          "- SaaS 项目与流量站研究完全分离。",""]
    return "\n".join(out)

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--candidates",type=Path,default=ROOT/"inputs"/"demand-candidates.json")
    parser.add_argument("--metrics",type=Path,default=ROOT/"inputs"/"demand-metrics.csv")
    parser.add_argument("--output-dir",type=Path,default=ROOT/"reports")
    args=parser.parse_args()
    data=build(args.candidates,args.metrics)
    args.output_dir.mkdir(exist_ok=True,parents=True)
    (args.output_dir/"demand-gate.json").write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    (args.output_dir/"demand-gate.md").write_text(markdown(data),encoding="utf-8")
    print(f"Core-demand gate: {data['candidate_count']} hypotheses, {data['metrics_records']} real metrics, "
          f"{sum(c['stage']=='READY_FOR_COMPETITOR_ORGANIC_REVIEW' for c in data['candidates'])} ready for competitor organic review.")

if __name__=="__main__":
    main()
