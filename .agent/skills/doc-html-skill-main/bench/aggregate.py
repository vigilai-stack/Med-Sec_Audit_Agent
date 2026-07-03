#!/usr/bin/env python3
"""aggregate.py — summarize metrics across repetitions.

Groups metrics.json by (tool, condition), computes mean/median/min/max/stdev for
the numeric fields, and writes results/aggregate.json + a printed summary plus
within-tool skill-vs-noskill deltas on the means.
"""
from __future__ import annotations
import json, os, statistics as st

BENCH = os.path.dirname(os.path.abspath(__file__))
R = os.path.join(BENCH, "results")
NUM = ["out_tokens","in_tokens","total_tokens","cost_usd","wall_ms","tool_calls",
       "doc_html_bytes","doc_yaml_bytes"]


def agg(vals):
    vals = [v for v in vals if isinstance(v,(int,float))]
    if not vals: return None
    return {"n":len(vals),"mean":round(st.mean(vals),4),"median":round(st.median(vals),4),
            "min":min(vals),"max":max(vals),
            "stdev":round(st.pstdev(vals),4) if len(vals)>1 else 0}


def main():
    metrics = json.load(open(os.path.join(R,"metrics.json")))
    groups = {}
    for m in metrics:
        if m.get("exit") not in (0,None): continue          # drop failed runs
        if not m.get("out_tokens"): continue                # drop empty/failed
        groups.setdefault((m["tool"],m["condition"]),[]).append(m)

    out = {}
    for (tool,cond),rows in sorted(groups.items()):
        out[f"{tool}/{cond}"] = {"runs":len(rows),"model":rows[0].get("model"),
                                 **{f:agg([r.get(f) for r in rows]) for f in NUM}}

    json.dump(out, open(os.path.join(R,"aggregate.json"),"w"), indent=2)

    def g(v, f, k="mean"):
        return v[f][k] if v.get(f) else None
    print(f"{'group':22} {'n':>2} {'out_tok(mean)':>13} {'total(mean)':>12} {'cost(mean)':>10} {'wall_ms':>9}")
    for k,v in out.items():
        cost = g(v,"cost_usd")
        costs = f"{cost:>10.4f}" if cost is not None else f"{'n/a':>10}"
        print(f"{k:22} {g(v,'out_tokens','n'):>2} "
              f"{g(v,'out_tokens'):>13,.0f} {g(v,'total_tokens'):>12,.0f} "
              f"{costs} {g(v,'wall_ms'):>9,.0f}")

    print("\n--- within-tool deltas on means (skill vs noskill) ---")
    tools = sorted({k.split('/')[0] for k in out})
    deltas={}
    for t in tools:
        ns=out.get(f"{t}/noskill"); sk=out.get(f"{t}/skill")
        if not ns or not sk: continue
        def d(f):
            if not ns.get(f) or not sk.get(f): return None
            a,b=ns[f]['mean'],sk[f]['mean']
            return None if not a else round((b-a)/a*100,1)
        deltas[t]={"out_tokens_pct":d("out_tokens"),"total_tokens_pct":d("total_tokens"),
                   "cost_pct":d("cost_usd"),"wall_pct":d("wall_ms"),
                   "out_ns":ns['out_tokens']['mean'],"out_sk":sk['out_tokens']['mean'],
                   "total_ns":ns['total_tokens']['mean'],"total_sk":sk['total_tokens']['mean'],
                   "cost_ns":(ns['cost_usd']['mean'] if ns.get('cost_usd') else None),
                   "cost_sk":(sk['cost_usd']['mean'] if sk.get('cost_usd') else None)}
        pp = lambda x: f"{x:+.0f}%" if x is not None else "n/a"
        print(f"  {t:10} out {pp(deltas[t]['out_tokens_pct'])}  total {pp(deltas[t]['total_tokens_pct'])}  "
              f"cost {pp(deltas[t]['cost_pct'])}  wall {pp(deltas[t]['wall_pct'])}")
    json.dump(deltas, open(os.path.join(R,"deltas.json"),"w"), indent=2)
    print("\n-> results/aggregate.json + deltas.json")


if __name__=="__main__":
    main()
