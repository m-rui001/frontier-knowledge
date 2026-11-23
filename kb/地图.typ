#import "../typst/lib.typ": *
#set page(paper: "a4", margin: (x: 22mm, y: 20mm))
#set text(font: ("Microsoft YaHei",), lang: "zh", size: 10pt)
#set par(leading: .8em, spacing: .55em, justify: true, first-line-indent: (amount: 2em, all: true))
#text(size: 16pt, weight: "bold")[领域地图]
#v(.7em)
三年窗口（2023-11-22 至 2026-11-22）里，OpenAlex 全库收了四千五百多万条作品。下表第二列是各领域在这个窗口内的总量，用来看体量差距；第三列是这套笔记在那个方向上挑了几篇。
#v(.4em)
数字之间的差距有好几个量级：医学与生物加起来占半壁，这里只挑了十几篇，比例上被严重低估；数学与理论物理产出量小，但单篇分量常常更重。取样偏差就在这里，读到哪一行觉得不对劲，那一行就是该自己去补的地方。
#v(.6em)
#set par(first-line-indent: 0em)
#table(
  columns: (auto, auto, auto, 1fr),
  stroke: none,
  inset: (x: 2.4mm, y: 1.6mm),
  align: (left, right, right, left),
  table.header([*领域*], [*窗口内作品数*], [*收录*], [*篇目*]),
  table.hline(stroke: .9pt + ink),
  [计算机科学], [2,491,772], [6], [不给人写解题过程，模型自己学会了反思、百万 token 上下文，算力账算在缓存上 等 6 篇],
  table.hline(stroke: .25pt + hair),
  [医学], [5,771,952], [37], [病理切片的基础模型，把稀有癌症也认了出来、让模型一次读完一整张病理切片 等 37 篇],
  table.hline(stroke: .25pt + hair),
  [法学], [—], [1], [六成引用是编的：大模型到底记不记得住判例],
  table.hline(stroke: .25pt + hair),
  [生化与分子生物学], [1,096,471], [7], [一个模型同时摆平蛋白、核酸、小分子和离子、形状算对了，力气还是空白：Boltz-2 去抢亲和力 等 7 篇],
  table.hline(stroke: .25pt + hair),
  [物理与天文], [985,737], [12], [宇宙学常数没被推翻，只是被数据拧了一下、红点太多，两种解释都得付账 等 12 篇],
  table.hline(stroke: .25pt + hair),
  [数学], [524,323], [3], [一亿条自造定理，教机器学会画辅助线、往对数凹分布里硬塞一个高斯 等 3 篇],
  table.hline(stroke: .25pt + hair),
  [材料科学], [900,133], [3], [一个通用原子间势，开箱就跑、氯会跑，那就派钾去追它 等 3 篇],
  table.hline(stroke: .25pt + hair),
  [神经科学], [407,589], [13], [雄性果蝇整条中枢的连接组，和雌性逐突触对了一遍、替人写字的那二十分钟，大脑少干了什么 等 13 篇],
  table.hline(stroke: .25pt + hair),
  [工程], [3,429,942], [3], [把视觉语言模型接上动作，机器人学会了叠衣服、人形机器人等不到互联网数据，于是自己造了一座金字塔 等 3 篇],
  table.hline(stroke: .25pt + hair),
  [能源], [460,412], [3], [公告堆到四百吉瓦，落地只有百分之七、钌想替铱，卡在溶解上——钽把这个死结解开了一半 等 3 篇],
  table.hline(stroke: .25pt + hair),
  [地球与行星], [813,296], [10], [八分钟算完十五天的天气集合预报、一次预训练，四个圈层的预报都换了底座 等 10 篇],
  table.hline(stroke: .25pt + hair),
  [经济学], [869,938], [6], [五千名客服的数据显示：AI 帮的是新手，不是老手、AI 抢单：外包市场上，写作和设计岗的收入掉了 5.2% 等 6 篇],
  table.hline(stroke: .25pt + hair),
  [决策科学], [366,109], [4], [27 条清单，管住 AI 医疗模型的报告、审一个 AI 预测模型，该怀疑什么 等 4 篇],
  table.hline(stroke: .25pt + hair),
  [免疫与微生物], [320,983], [5], [在不在，和有多少，是两件事、健康菌群：一个还没定义就已经卖掉的词 等 5 篇],
  table.hline(stroke: .25pt + hair),
  [农业与生物], [5,682,837], [3], [产量差在收窄的地方，正是下一次停涨的地方、一百年前的种子，今天才读得懂 等 3 篇],
  table.hline(stroke: .25pt + hair),
  [社会科学], [6,020,765], [1], [把雨林掀开，底下是一条规划过的山谷],
  table.hline(stroke: .25pt + hair),
)
#v(.5em)
#text(size: 8.2pt, fill: muted)[计数取自 OpenAlex，按作品的首个主题字段归类；同一作品可能跨多个领域，各行之和大于全库总量。被引近零的新作在计数里和大作同权，这是纯计数指标的局限。]
