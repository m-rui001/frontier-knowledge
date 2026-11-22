#!/usr/bin/env python3
"""OpenAlex harvester — the *scan layer* of the frontier KB.

OpenAlex covers journals, books, preprints, reports and conference papers across
every discipline, with citation counts, so it is the right substrate for a
"3-year window, whole of knowledge" sweep. arXiv alone only sees one slice.

Usage:
  python tools/crawl_openalex.py --per-field 200 --out corpus/openalex.jsonl
  python tools/crawl_openalex.py --field 17 --sort cited_by_count:desc --per-field 50
"""
import argparse, json, os, sys, time, datetime, requests

API = "https://api.openalex.org/works"
MAIL = "frontier-kb@example.org"   # polite pool
SEL = ",".join([
    "id", "doi", "title", "display_name", "publication_year", "publication_date",
    "cited_by_count", "type", "type_crossref", "primary_location", "primary_topic",
    "topics", "abstract_inverted_index", "authorships", "open_access",
    "referenced_works_count", "language",
])

# OpenAlex top-level fields worth tracking for a frontier KB
FIELDS = {
    17: "Computer Science", 27: "Medicine", 13: "Biochemistry/Genetics/MolBio",
    31: "Physics & Astronomy", 26: "Mathematics", 25: "Materials Science",
    28: "Neuroscience", 22: "Engineering", 21: "Energy", 23: "Environmental Science",
    20: "Economics", 32: "Psychology", 33: "Social Sciences", 11: "Agricultural & Bio",
    19: "Earth & Planetary", 18: "Decision Sciences", 30: "Pharmacology",
    14: "Business", 12: "Arts & Humanities", 24: "Immunology & Microbiology",
}


def abstract_from_inverted(inv):
    if not inv:
        return ""
    pos = []
    for word, idxs in inv.items():
        for i in idxs:
            pos.append((i, word))
    pos.sort()
    return " ".join(w for _, w in pos)


def slim(w):
    loc = w.get("primary_location") or {}
    src = (loc.get("source") or {})
    pt = w.get("primary_topic") or {}
    return {
        "id": (w.get("id") or "").rsplit("/", 1)[-1],
        "doi": w.get("doi"),
        "title": w.get("display_name") or w.get("title"),
        "year": w.get("publication_year"),
        "date": w.get("publication_date"),
        "cited": w.get("cited_by_count"),
        "type": w.get("type"),
        "venue": src.get("display_name"),
        "venue_type": src.get("type"),
        "is_oa": (w.get("open_access") or {}).get("is_oa"),
        "oa_url": (w.get("open_access") or {}).get("oa_url"),
        "landing": loc.get("landing_page_url"),
        "pdf": loc.get("pdf_url"),
        "field": (pt.get("field") or {}).get("display_name"),
        "subfield": (pt.get("subfield") or {}).get("display_name"),
        "topic": pt.get("display_name"),
        "authors": [a["author"]["display_name"] for a in (w.get("authorships") or [])][:12],
        "n_refs": w.get("referenced_works_count"),
        "abstract": abstract_from_inverted(w.get("abstract_inverted_index")),
    }


def harvest(filter_str, sort, per_page, pages=1, label=""):
    out = []
    for p in range(pages):
        params = {"filter": filter_str, "sort": sort, "per-page": per_page,
                  "page": p + 1, "select": SEL, "mailto": MAIL}
        for attempt in range(4):
            try:
                r = requests.get(API, params=params, timeout=90)
                if r.status_code == 200:
                    break
                print(f"  ! {r.status_code} {label} retry", file=sys.stderr)
            except Exception as e:
                print(f"  ! {e.__class__.__name__} {label} retry", file=sys.stderr)
            time.sleep(4 * (attempt + 1))
        else:
            print(f"  x failed {label}", file=sys.stderr)
            return out
        d = r.json()
        for w in d["results"]:
            x = slim(w)
            x["query"] = label
            out.append(x)
        print(f"  [{label}] page {p+1}: +{len(d['results'])} (window {d['meta']['count']})", file=sys.stderr)
        if not d["results"]:
            break
        time.sleep(0.7)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--per-field", type=int, default=200)
    ap.add_argument("--pages", type=int, default=1)
    ap.add_argument("--field", type=int, default=None)
    ap.add_argument("--sort", default="cited_by_count:desc")
    ap.add_argument("--sorts", default="cited_by_count:desc,publication_date:desc")
    ap.add_argument("--since", default="2023-11-22")
    ap.add_argument("--until", default=str(datetime.date.today()))
    ap.add_argument("--out", default="corpus/openalex.jsonl")
    a = ap.parse_args()

    os.makedirs(os.path.dirname(a.out) or ".", exist_ok=True)
    seen = set()
    if os.path.exists(a.out):
        for line in open(a.out, encoding="utf-8"):
            try:
                seen.add(json.loads(line)["id"])
            except Exception:
                pass
        print(f"existing: {len(seen)}", file=sys.stderr)

    fields = [a.field] if a.field else list(FIELDS)
    sorts = [a.sort] if a.field else a.sorts.split(",")
    rows = []
    for fid in fields:
        for s in sorts:
            f = (f"from_publication_date:{a.since},to_publication_date:{a.until},"
                 f"primary_topic.field.id:https://openalex.org/fields/{fid}")
            label = f"{FIELDS.get(fid, fid)}/{s.split(':')[0]}"
            for x in harvest(f, s, a.per_field, a.pages, label):
                if x["id"] in seen:
                    continue
                seen.add(x["id"])
                x["harvested"] = datetime.datetime.now().isoformat(timespec="seconds")
                rows.append(x)

    with open(a.out, "a", encoding="utf-8") as fh:
        for x in rows:
            fh.write(json.dumps(x, ensure_ascii=False) + "\n")
    print(f"wrote {len(rows)} new -> {a.out} (corpus {len(seen)})")


if __name__ == "__main__":
    main()