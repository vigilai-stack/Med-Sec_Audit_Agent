#!/usr/bin/env python3
"""extract.py — unify metrics across the four CLIs into one table.

Reads every bench/runs/<tool>-<cond>-<rep>/ directory, parses the tool-specific
raw output, and emits a normalized record per run:

  tool, condition, rep, model, exit, wall_ms, gen_ms,
  in_tokens, out_tokens, reasoning_tokens, cache_read, cache_write, total_tokens,
  cost_usd, turns, tool_calls, files_written, doc_html_bytes, doc_yaml_bytes

Token semantics differ per provider; we map each to the same column names and
note caveats in the README. Output: results/metrics.json + results/metrics.csv.
"""
from __future__ import annotations
import json, os, csv, sys, glob

BENCH = os.path.dirname(os.path.abspath(__file__))
RUNS = os.path.join(BENCH, "runs")
OUT = os.path.join(BENCH, "results")

REC_FIELDS = ["tool","condition","rep","model","exit","wall_ms","gen_ms",
              "in_tokens","out_tokens","reasoning_tokens","cache_read","cache_write",
              "total_tokens","cost_usd","turns","tool_calls","files_written",
              "doc_html_bytes","doc_yaml_bytes","notes"]


def blank(meta):
    return {k: meta.get(k, 0) if k in ("wall_ms","doc_html_bytes","doc_yaml_bytes","exit","rep") else None
            for k in REC_FIELDS}


def parse_claude(run, rec):
    p = os.path.join(run, "raw.json")
    if not os.path.exists(p) or os.path.getsize(p) == 0:
        rec["notes"] = "no raw.json (run failed?)"; return rec
    d = json.load(open(p))
    u = d.get("usage", {}) or {}
    # pick the dominant model (Claude makes tiny haiku side-calls for titles)
    mu = d.get("modelUsage") or {}
    def _out(v): return (v or {}).get("outputTokens", 0) if isinstance(v, dict) else 0
    rec["model"] = max(mu, key=lambda k: _out(mu[k])) if mu else "claude"
    rec["in_tokens"] = u.get("input_tokens")
    rec["out_tokens"] = u.get("output_tokens")
    rec["cache_read"] = u.get("cache_read_input_tokens")
    rec["cache_write"] = u.get("cache_creation_input_tokens")
    rec["reasoning_tokens"] = 0
    rec["total_tokens"] = sum(v for v in [rec["in_tokens"],rec["out_tokens"],
                              rec["cache_read"],rec["cache_write"]] if v)
    rec["cost_usd"] = d.get("total_cost_usd")
    rec["gen_ms"] = d.get("duration_ms")
    rec["turns"] = d.get("num_turns")
    if d.get("is_error"): rec["notes"] = "is_error=" + str(d.get("subtype"))
    return rec


def parse_codex(run, rec):
    p = os.path.join(run, "raw.jsonl")
    if not os.path.exists(p) or os.path.getsize(p) == 0:
        rec["notes"] = "no raw.jsonl"; return rec
    intok=outtok=reason=cache=0; tcalls=0; model=None; err=None
    for ln in open(p):
        ln=ln.strip()
        if not ln: continue
        try: o=json.loads(ln)
        except: continue
        t=o.get("type")
        if t=="error" or t=="turn.failed":
            err=(o.get("message") or (o.get("error") or {}).get("message"))
        # usage may appear on turn.completed / token_count events
        usage = o.get("usage") or (o.get("turn") or {}).get("usage") or {}
        if isinstance(usage,dict) and usage:
            intok = usage.get("input_tokens", intok) or intok
            outtok = usage.get("output_tokens", outtok) or outtok
            reason = usage.get("reasoning_output_tokens", reason) or reason
            cache = usage.get("cached_input_tokens", cache) or cache
        if t in ("item.completed","item.started"):
            it=o.get("item",{})
            if it.get("type") in ("command_execution","file_change","local_shell_call"): tcalls+=1
        if t=="turn.completed":
            pass
        model = o.get("model", model)
    rec["model"]=model or "codex-gpt"
    rec["in_tokens"]=intok; rec["out_tokens"]=outtok; rec["reasoning_tokens"]=reason
    rec["cache_read"]=cache; rec["cache_write"]=0
    rec["total_tokens"]=intok+outtok+reason+cache
    rec["tool_calls"]=tcalls
    if err: rec["notes"]=("ERROR: "+err)[:80]
    return rec


def parse_session_export(run, rec):
    """opencode + kilo share the {info, messages[]} export shape."""
    p = os.path.join(run, "session.json")
    if not os.path.exists(p) or os.path.getsize(p)==0:
        rec["notes"]="no session.json"; return rec
    try: d=json.load(open(p))
    except: rec["notes"]="bad session.json"; return rec
    info=d.get("info",{}); msgs=d.get("messages",[])
    intok=outtok=reason=cr=cw=0; cost=0.0; tcalls=0; model=None; assistants=0
    tmin=tmax=None
    for m in msgs:
        mi=m.get("info",m)
        if mi.get("role")=="assistant":
            assistants+=1
            tk=mi.get("tokens",{}) or {}
            intok+=tk.get("input",0) or 0
            outtok+=tk.get("output",0) or 0
            reason+=tk.get("reasoning",0) or 0
            ch=tk.get("cache",{}) or {}
            cr+=ch.get("read",0) or 0; cw+=ch.get("write",0) or 0
            cost+=mi.get("cost",0) or 0
            model=mi.get("modelID",model)
            tm=mi.get("time",{}) or {}
            if tm.get("created"): tmin=min(tmin,tm["created"]) if tmin else tm["created"]
            if tm.get("completed"): tmax=max(tmax,tm["completed"]) if tmax else tm["completed"]
        # count tool-call parts
        for part in (m.get("parts") or []):
            if part.get("type") in ("tool","tool-invocation","tool_use"): tcalls+=1
    rec["model"]=model or "?"
    rec["in_tokens"]=intok; rec["out_tokens"]=outtok; rec["reasoning_tokens"]=reason
    rec["cache_read"]=cr; rec["cache_write"]=cw
    rec["total_tokens"]=intok+outtok+reason+cr+cw
    rec["cost_usd"]=round(cost,6)
    rec["turns"]=assistants
    rec["tool_calls"]=tcalls
    summ=info.get("summary",{}) or {}
    rec["files_written"]=summ.get("files")
    if tmin and tmax: rec["gen_ms"]=tmax-tmin
    return rec


PARSERS={"claude":parse_claude,"codex":parse_codex,
         "opencode":parse_session_export,"kilo":parse_session_export}


def main():
    recs=[]
    for run in sorted(glob.glob(os.path.join(RUNS,"*"))):
        if not os.path.isdir(run): continue
        meta_p=os.path.join(run,"meta.json")
        if not os.path.exists(meta_p): continue
        meta=json.load(open(meta_p))
        rec=blank(meta)
        rec.update({"tool":meta["tool"],"condition":meta["condition"],"rep":meta["rep"],
                    "exit":meta["exit"],"wall_ms":meta["wall_ms"],
                    "doc_html_bytes":meta["doc_html_bytes"],"doc_yaml_bytes":meta["doc_yaml_bytes"]})
        # files_written from FS produced list (fallback)
        rec["files_written"]=len(meta.get("produced_files",[]))
        rec=PARSERS[meta["tool"]](run,rec)
        # prefer FS file count if parser didn't set it
        if not rec.get("files_written"):
            rec["files_written"]=len(meta.get("produced_files",[]))
        recs.append(rec)
    os.makedirs(OUT,exist_ok=True)
    json.dump(recs,open(os.path.join(OUT,"metrics.json"),"w"),indent=2)
    with open(os.path.join(OUT,"metrics.csv"),"w",newline="") as f:
        w=csv.DictWriter(f,fieldnames=REC_FIELDS); w.writeheader()
        for r in recs: w.writerow(r)
    # pretty print
    cols=["tool","condition","model","exit","out_tokens","total_tokens","cost_usd",
          "wall_ms","tool_calls","files_written","doc_html_bytes","doc_yaml_bytes"]
    print(" | ".join(c[:10].rjust(10) for c in cols))
    for r in recs:
        print(" | ".join(str(r.get(c,""))[:10].rjust(10) for c in cols))
    print(f"\n{len(recs)} runs -> results/metrics.json + metrics.csv")


if __name__=="__main__":
    main()
