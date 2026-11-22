#!/usr/bin/env python3
"""arXiv harvester for the Frontier Knowledge Base.

Only stdlib + requests. Respects arXiv API etiquette (3s/request, single connection).

Usage:
  python tools/crawl_arxiv.py --cats cs.LG,cs.CL --per-cat 200 --out corpus/arxiv.jsonl
  python tools/crawl_arxiv.py --query 'ti:"AlphaFold 3"' --per-cat 5
Window: --years 3  (relative to today)
"""
import argparse, json, sys, time, re, os, datetime, hashlib
import xml.etree.ElementTree as ET
import requests

API = "http://export.arxiv.org/api/query"
NS = {"a": "http://www.w3.org/2005/Atom", "arxiv": "http://arxiv.org/schemas/atom"}


def build_query(cat=None, q=None, since=None):
    parts = []
    if q:
        parts.append(f"({q})")
    if cat:
        parts.append(f"cat:{cat}")
    if since:
        parts.append(f"submittedDate:[{since}0000 TO 300001010000]")
    return " AND ".join(parts)


def fetch(params, retries=4):
    for i in range(retries):
        try:
            r = requests.get(API, params=params, timeout=90)
            r.raise_for_status()
            return r.text
        except Exception as e:
            wait = 5 * (i + 1)
            print(f"  ! retry {i+1}/{retries} ({e.__class__.__name__}) sleep {wait}s", file=sys.stderr)
            time.sleep(wait)
    return None


def parse(xml):
    out = []
    root = ET.fromstring(xml)
    for e in root.findall("a:entry", NS):
        def g(tag):
            n = e.find(tag, NS)
            return (n.text or "").strip() if n is not None else ""
        aid = g("a:id").rsplit("/", 1)[-1]
        cats = [c.get("term") for c in e.findall("a:category", NS)]
        prim = e.find("arxiv:primary_category", NS)
        pdf = ""
        for l in e.findall("a:link", NS):
            if l.get("title") == "pdf":
                pdf = l.get("href")
        out.append({
            "id": aid,
            "title": re.sub(r"\s+", " ", g("a:title")),
            "abstract": re.sub(r"\s+", " ", g("a:summary")),
            "published": g("a:published"),
            "updated": g("a:updated"),
            "authors": [a.find("a:name", NS).text for a in e.findall("a:author", NS)],
            "cats": cats,
            "primary": prim.get("term") if prim is not None else (cats[0] if cats else ""),
            "comment": g("arxiv:comment"),
            "journal_ref": g("arxiv:journal_ref"),
            "doi": g("arxiv:doi"),
            "pdf": pdf,
            "abs_url": f"https://arxiv.org/abs/{aid}",
        })
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cats", default="")
    ap.add_argument("--query", default="")
    ap.add_argument("--per-cat", type=int, default=200)
    ap.add_argument("--years", type=float, default=3.0)
    ap.add_argument("--sort", default="submittedDate")
    ap.add_argument("--out", default="corpus/arxiv.jsonl")
    ap.add_argument("--sleep", type=float, default=3.2)
    a = ap.parse_args()

    since = (datetime.date.today() - datetime.timedelta(days=int(365.25 * a.years))).strftime("%Y%m%d")
    seen, rows = set(), []
    os.makedirs(os.path.dirname(a.out) or ".", exist_ok=True)
    if os.path.exists(a.out):
        with open(a.out, encoding="utf-8") as f:
            for line in f:
                try:
                    r = json.loads(line)
                    seen.add(r["id"])
                except Exception:
                    pass
        print(f"existing records: {len(seen)}")

    jobs = [("cat " + c, build_query(cat=c, since=since)) for c in [x for x in a.cats.split(",") if x]]
    if a.query:
        jobs.insert(0, ("q " + a.query[:60], build_query(q=a.query, since=since)))
    if not jobs:
        print("nothing to do", file=sys.stderr)

    for label, q in jobs:
        params = {"search_query": q, "start": 0, "max_results": a.per_cat,
                  "sortBy": a.sort, "sortOrder": "descending"}
        print(f"[{label}] since={since} n={a.per_cat}", file=sys.stderr)
        xml = fetch(params)
        time.sleep(a.sleep)
        if not xml:
            print("  failed", file=sys.stderr)
            continue
        got = 0
        for r in parse(xml):
            if r["id"] in seen:
                continue
            seen.add(r["id"])
            r["harvested"] = datetime.datetime.now().isoformat(timespec="seconds")
            r["query"] = label
            rows.append(r)
            got += 1
        print(f"  +{got}", file=sys.stderr)

    with open(a.out, "a", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"wrote {len(rows)} new records -> {a.out} (total corpus {len(seen)})")


if __name__ == "__main__":
    main()