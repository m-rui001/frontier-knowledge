#!/usr/bin/env python3
"""測量並回填每篇的壓縮指標：原文頁數、摘要字符數、正文漢字數。

用法：python tools/ratios.py [--write]
  --write  把 ratio: "..." 寫回 summary.typ
"""
import argparse, glob, json, os, re, shutil, subprocess, tempfile

CJK = re.compile(r"[\u3400-\u9fff]")
LAT = re.compile(r"[A-Za-z][A-Za-z0-9\-\.]*")


def load_abstracts():
    ab = {}
    for p in ("meta/usable.json",):
        if not os.path.exists(p):
            continue
        for f, rs in json.load(open(p, encoding="utf-8")).items():
            for r in rs:
                ab[r["id"]] = r.get("abstract") or ""
    return ab


def body_text(src):
    """取出 digest(...)[ ... ] 的正文，粗略去掉標記。"""
    i = src.index(")[") + 2
    txt = src[i:]
    txt = txt.rsplit("]", 1)[0]
    txt = txt.replace("#ping[", " ")
    lines = [ln for ln in txt.split("\n") if not ln.strip().startswith("#") and not ln.strip().startswith("=")]
    return " ".join(lines)


def own_pages(typ_path, root="."):
    """編譯成逐頁 PNG，數出來是幾頁。"""
    tmp = tempfile.mkdtemp()
    try:
        subprocess.run(["typst", "compile", "--root", root, typ_path,
                        os.path.join(tmp, "p{n}.png")],
                       capture_output=True, text=True, timeout=180)
        return len([f for f in os.listdir(tmp) if f.endswith(".png")])
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def measure(txt):
    cjk = len(CJK.findall(txt))
    lat = len(LAT.findall(txt))
    return cjk, lat, cjk + lat


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    a = ap.parse_args()
    ab = load_abstracts()
    bib = json.load(open("meta/biblio.json", encoding="utf-8")) if os.path.exists("meta/biblio.json") else {}
    rows = []
    for d in sorted(glob.glob("kb/w/*")):
        wid = os.path.basename(d)
        f = f"{d}/summary.typ"
        if not os.path.exists(f):
            continue
        src = open(f, encoding="utf-8").read()
        cjk, lat, total = measure(body_text(src))
        abs_chars = len(ab.get(wid, ""))
        pages = None
        b = bib.get(wid) or {}
        fp, lp = b.get("first"), b.get("last")
        def num(v):
            m = re.search(r"(\d+)", str(v or ""))
            return int(m.group(1)) if m else None
        a_, b_ = num(fp), num(lp)
        if a_ and b_ and b_ >= a_:
            pages = b_ - a_ + 1
        mine = own_pages(f)
        if pages:
            ratio = f"原文 {pages} 页 → 本篇 {mine} 页（约 1/{pages/mine:.0f}）"
        else:
            ratio = f"原文页数未收录 · 摘要 {abs_chars} 字符 · 本篇 {mine} 页"
        rows.append((wid, pages, abs_chars, cjk, lat, total, ratio))
        if a.write:
            src2, n = re.subn(r'(?m)^(\s*ratio:\s*)".*?",$', lambda m: f'{m.group(1)}"{ratio}",', src)
            if n == 0:
                print("  ! no ratio field:", f)
            else:
                open(f, "w", encoding="utf-8").write(src2)

    out = ["# 压缩指标（自动测量）\n", "| id | 原文页数 | 摘要字符 | 正文汉字 | 正文西文 | 压缩说明 |", "|---|---|---|---|---|---|"]
    for wid, pages, ac, cjk, lat, total, ratio in rows:
        out.append(f"| {wid} | {pages or '-'} | {ac} | {cjk} | {lat} | {ratio} |")
    open("meta/ratios.md", "w", encoding="utf-8").write("\n".join(out) + "\n")
    for r in rows:
        print(f"{r[0]}  pages={r[1]}  abs={r[2]}  body={r[5]}  | {r[6]}")
    print(f"\n{len(rows)} digests -> meta/ratios.md" + (" (files updated)" if a.write else " (dry run)"))


if __name__ == "__main__":
    main()