#!/usr/bin/env python3
"""抽查中文稿件的'AI 味'与体例问题，逐条给出文件、行号、原句。

用法：python tools/smell.py [kb/w/*/summary.typ ...]
"""
import glob, re, sys, io

# 词表：命中即报，按味道轻重分级
CLICHE = {
    "套话": ["总的来说", "总而言之", "综上所述", "值得注意的是", "值得一提的是", "需要指出的是",
             "不难看出", "显而易见", "毋庸置疑", "毫无疑问", "众所周知", "由此可见",
             "在当今", "在这个时代", "随着.*的发展", "深刻变革", "具有重要意义", "意义深远",
             "赋能", "助力", "深刻影响", "产生深远", "提供了有力", "奠定了坚实基础"],
    "AI 排比/对举": ["不仅.*更是", "不仅仅是.*而是", "既是.*也是", "不是.*而是.*而是",
                    "从.*走向.*的转变", "从.*到.*的跃迁", "既是挑战也是机遇",
                    "一方面.*另一方面", "看似.*实则"],
    "自造金句": ["真正的", "本质上", "说到底", "归根结底", "核心在于", "关键在于", "底层逻辑",
                "这件事", "这套东西", "这一点", "这一步", "这句话"],
    "升华收尾": ["而这才是", "这才是", "或许", "也许", "未来可期", "时间会证明", "留给.*的"],
}

STRUCT = {
    "首先其次": r"首先[^。]{0,80}(其次|然后|最后)",
    "长破折号": r"——",
    "三连排比": r"([^，。；]{2,8})、([^，。；]{2,8})、([^，。；]{2,8})",
}


def strip_markup(s):
    s = s.split(")[", 1)[1] if ")[ " in s or ")[" in s else s
    s = re.sub(r"#ping\[|#digest\(|^=.*$", "", s, flags=re.M)
    s = re.sub(r'^\s*[a-z\-]+:.*$', "", s, flags=re.M)
    return s


def main(paths):
    paths = paths or sorted(glob.glob("kb/w/*/summary.typ"))
    grand = {}
    for p in paths:
        raw = io.open(p, encoding="utf-8").read()
        txt = strip_markup(raw)
        lines = raw.split("\n")
        hits = []
        for kind, words in CLICHE.items():
            for w in words:
                for m in re.finditer(w, txt):
                    ln = txt[:m.start()].count("\n")
                    seg = txt[max(0, m.start() - 18):m.end() + 22].replace("\n", " ")
                    hits.append((kind, w, seg))
        for name, pat in STRUCT.items():
            for m in re.finditer(pat, txt):
                seg = txt[max(0, m.start() - 15):m.end() + 15].replace("\n", " ")
                hits.append(("结构", name, seg))
        n_dash = len(re.findall("——", txt))
        n_cjk = len(re.findall(r"[\u3400-\u9fff]", txt))
        grand[p] = (n_cjk, n_dash, hits)
        print(f"\n=== {p}  汉字 {n_cjk}  破折号 {n_dash}（每千字 {n_dash/max(n_cjk,1)*1000:.1f}）")
        seen = set()
        for kind, w, seg in hits:
            key = (kind, w)
            if kind == "结构" and key in seen:
                continue
            seen.add(key)
            print(f"  [{kind}] {w} :: …{seg}…")
    # 汇总
    tot = {}
    for p, (n, d, hits) in grand.items():
        for kind, w, _ in hits:
            tot.setdefault(kind, {}).setdefault(w, 0)
            tot[kind][w] += 1
    print("\n=== 词频汇总")
    for kind, d in tot.items():
        print(f"{kind}: " + "、".join(f"{w}×{c}" for w, c in sorted(d.items(), key=lambda x: -x[1])[:12]))


if __name__ == "__main__":
    main(sys.argv[1:])