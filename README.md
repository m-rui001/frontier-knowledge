# 人类知识前沿压缩册

2023-11 至 2026-11 三年窗口的人类前沿产出，扫一遍、挑出来、压成中文笔记，篇末附点评。

成品：`kb/w/<id>/summary.pdf`，一篇一个 PDF（当前 64 篇）。索引 `INDEX.md`，领域地图 `kb/领域地图.pdf`，另一份 `kb/技术报告与代码库.pdf` 收论文之外的系统卡与开源实现。
不合并成一本：单篇改一篇只重编译一两页，合并会把每次改动都变成重排整本。

## 目录结构

```
corpus/        原始抓取数据
  openalex.jsonl   19997 条，20 个一级领域，按被引前 600 + 最新 400 各取
  arxiv.jsonl      arXiv 补充抓取（受速率限制，仅 cs.LG 完整）
meta/          中间产物
  stats.json       分领域统计、被引榜、增速榜
  scan.md          人读版扫描报告
  usable.json      过滤后的可用记录（13000+ 条）
  field_counts.json 各领域窗口内全库计数
  biblio.json      起止页码（算压缩比用）
  ratios.md        每篇的实测压缩指标
kb/
  w/<OpenAlex ID>/   source.txt（原文摘要与元数据）+ summary.typ + summary.pdf
  地图.typ          领域地图源文件（生成物，勿手改）
  领域地图.pdf       上面那页编译出来的成品
  卡片.typ / 技术报告与代码库.pdf   系统卡与代码库的速查卡（两页）
typst/lib.typ  版式模板（digest / ping）
tools/         流水线
  crawl_openalex.py  扫描层主力，支持分领域、分排序、游标/页码分页
  crawl_arxiv.py     arXiv 备线（注意 3s 限速，300 条/请求会触发 429）
  analyze.py         过滤 + 分领域统计
  ratios.py          实测压缩比并回填每篇的 ratio 字段
  make_index.py      生成 INDEX.md 与领域地图（不再合并成册）
  smell.py           中文稿件的腔调体检（套话/对举/破折号密度）
  fixbracket.py      修 typst 方括号配平
  BRIEF.md           新篇目的写作简报
  REVISE.md          旧篇目的精修简报（去 AI 味）
```

## 重建

```bash
python tools/crawl_openalex.py --per-field 200 --pages 3 --sorts "cited_by_count:desc" --out corpus/openalex.jsonl
python tools/crawl_openalex.py --per-field 200 --pages 2 --sorts "publication_date:desc" --out corpus/openalex.jsonl
python tools/analyze.py
python tools/ratios.py --write      # 实测压缩比并回填每篇 ratio
python tools/make_index.py          # INDEX.md + kb/领域地图.pdf
```

单篇重编译：

```bash
typst compile --root . kb/w/<ID>/summary.typ kb/w/<ID>/summary.pdf
```

## 稿件规矩（三条硬线）

1. 摘要里没有的数字不写。宁可定性。
2. 一篇最多一处"不是 A 而是 B"、一处"真正的 X"、两处极值词、两处格言收尾，一个主隐喻。
3. 破折号每千字 2–4 个，超过 6 个就是毛病。
4. 新增篇目 4–5 页 / 3200–4200 字，先抓全文再写；抓不到全文的只用摘要，数字不许编。

细节见 `tools/BRIEF.md`（新篇目）与 `tools/REVISE.md`（精修）。

## 已知偏差

- 被引数对 2025–2026 的新作极不公平，用年均被引部分缓解，没有解决。
- 医学与生物占全库产出近半，本书只取两三篇，比例严重低估。
- OpenAlex 的"发表年份"含再版与重印，教科书经典会混进前沿榜（已在过滤里剔掉一部分）。
- 只能读到摘要的篇目（部分 Nature / Cell 正文有墙），细节会偏薄，`source.txt` 里记着来源。

## 许可

代码与中文笔记：MIT（见 `LICENSE`）。论文摘要与元数据版权归原作者与出版方，仅作溯源之用；抓取到的论文全文不随仓库分发。

## 仓库里没什么

- **没有 PDF**：所有 `summary.pdf` 都是本地编译产物，`.gitignore` 已排除。克隆后按上面的命令重新编译即可。
- **没有原始抓取数据**：`corpus/` 与 `meta/usable.json`（约 70MB）同样被排除，用 `tools/crawl_openalex.py` 与 `tools/analyze.py` 可重新生成。
- **没有论文全文**：`full.txt` 一类是抓下来给写稿用的，版权在别人手上，不进仓库。
