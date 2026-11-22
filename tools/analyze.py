#!/usr/bin/env python3
"""Scan-layer analysis: per-field stats, momentum ranking, shortlist for deep reading."""
import json, os, statistics, datetime, collections, sys

CORPUS = "corpus/openalex.jsonl"
TODAY = datetime.date(2026, 11, 22)

JUNK_TYPE = {"peer-review","paratext","erratum","editorial","libguides","reference-entry",
             "supplementary-materials","registration","grant","retraction","reference","other"}
JUNK_TITLE = {"personal communication","front matter","back matter","table of contents",
              "editorial board","cover","index"}

def usable(r):
    if r.get("type") in JUNK_TYPE:
        return False
    t = (r.get("title") or "").strip()
    if len(t) < 12 or t.lower() in JUNK_TITLE:
        return False
    v = (r.get("venue") or "").strip()
    if v and (t.lower() == v.lower() or (v.lower() in t.lower() and len(t) < len(v) + 12)):
        return False          # journal-issue records masquerading as works
    if len(r.get("abstract") or "") < 400:
        return False          # no readable substance -> cannot compress it
    return True

def load():
    rows = []
    for line in open(CORPUS, encoding="utf-8"):
        try:
            r = json.loads(line)
        except Exception:
            continue
        if not r.get("date"):
            continue
        r["_d"] = datetime.date.fromisoformat(r["date"])
        r["_age"] = max((TODAY - r["_d"]).days / 365.25, 0.25)
        r["_score"] = (r.get("cited") or 0) / r["_age"]      # citations per year
        r["_ok"] = usable(r)
        rows.append(r)
    return rows

def main():
    rows = load()
    byf = collections.defaultdict(list)
    for r in rows:
        if r["_ok"]:
            byf[r.get("field") or "?"].append(r)
    dropped = sum(1 for r in rows if not r["_ok"])
    os.makedirs("meta", exist_ok=True)
    stats, brief = {}, []
    brief.append(f"# Scan layer\n\n- records: {len(rows)}\n- window: 2023-11-22 .. 2026-11-22\n")
    for f, rs in sorted(byf.items(), key=lambda kv: -len(kv[1])):
        c = [r.get("cited") or 0 for r in rs]
        stats[f] = {
            "n": len(rs),
            "cited_median": statistics.median(c),
            "cited_mean": round(statistics.mean(c), 1),
            "oa_frac": round(sum(1 for r in rs if r.get("is_oa")) / len(rs), 3),
            "types": dict(collections.Counter(r.get("type") for r in rs).most_common(6)),
            "top_cited": [{"t": r["title"], "c": r["cited"], "y": r["year"], "id": r["id"],
                           "v": r.get("venue")} for r in sorted(rs, key=lambda r: -(r.get("cited") or 0))[:12]],
            "top_momentum": [{"t": r["title"], "c": r["cited"], "y": r["year"], "id": r["id"],
                              "v": r.get("venue"), "s": round(r["_score"], 1)}
                             for r in sorted(rs, key=lambda r: -r["_score"])[:8]],
        }
        brief.append(f"\n## {f}\n\nn={len(rs)}  median cites={stats[f]['cited_median']}  OA={stats[f]['oa_frac']}\n")
        for x in stats[f]["top_cited"][:8]:
            brief.append(f"- [{x['c']}] {x['t'][:110]} ({x['y']}, {x['v']})\n")

    ok = [r for r in rows if r["_ok"]]
    glob_top = sorted(ok, key=lambda r: -(r.get("cited") or 0))[:80]
    glob_mom = sorted(ok, key=lambda r: -r["_score"])[:120]
    stats["_global_top"] = [{"t": r["title"], "c": r["cited"], "y": r["year"], "id": r["id"],
                             "f": r.get("field"), "v": r.get("venue")} for r in glob_top]
    stats["_global_momentum"] = [{"t": r["title"], "c": r["cited"], "y": r["year"], "id": r["id"],
                                  "f": r.get("field"), "v": r.get("venue"),
                                  "s": round(r["_score"], 1)} for r in glob_mom]
    json.dump(stats, open("meta/stats.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    open("meta/scan.md", "w", encoding="utf-8").write("".join(brief))
    print(f"records={len(rows)} fields={len(byf)} -> meta/stats.json, meta/scan.md")

if __name__ == "__main__":
    main()