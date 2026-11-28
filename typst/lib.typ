// 前沿压缩册的公共模板（v2）。所有单篇摘要都 import 这里，保证版式一致。
// 改动要点：中文首行缩进、页脚承托版心、来源行分栏、点评块加左竖线。

#let accent = rgb("#7a1f2b")
#let ink = rgb("#1c1c1c")
#let muted = rgb("#6a6a6a")
#let hair = rgb("#cfc7bd")
#let tint = rgb("#f7f3ef")

#let digest(
  title: "",
  src: "",
  url: "",
  meta: "",
  ratio: "",
  body,
) = {
  set page(
    paper: "a4",
    margin: (x: 25mm, top: 24mm, bottom: 27mm),
    numbering: "1",
    footer: context [
      #set text(size: 7.6pt, fill: muted)
      #line(length: 100%, stroke: .4pt + hair)
      #v(-.2em)
      #grid(
        columns: (1fr, auto),
        align: (left, right),
        [人类知识前沿压缩册],
        [#counter(page).display() / #counter(page).final().first()],
      )
    ],
  )
  set text(font: ("Microsoft YaHei", "Libertinus Serif"), lang: "zh", size: 10.5pt, fill: ink)
  set par(
    justify: true,
    leading: .82em,
    spacing: .58em,
    first-line-indent: (amount: 2em, all: true),
  )

  show heading.where(level: 1): it => block(above: 0.9em, below: .62em)[
    #box(baseline: 24%, width: .28em, height: .28em, fill: accent)
    #h(.62em)
    #text(size: 11.8pt, weight: "bold", fill: ink)[#it.body]
  ]
  show heading.where(level: 2): it => block(above: 1.2em, below: .45em)[
    #text(size: 10.8pt, weight: "bold", fill: ink)[#it.body]
  ]
  show link: it => it

  // 顶端色条 + 标题 + 来源行
  block(above: 0em, below: 1.5em, breakable: false)[
    #set par(first-line-indent: 0em, justify: false)
    #line(length: 100%, stroke: 2.4pt + accent)
    #v(3.4mm)
    #text(size: 18pt, weight: "bold", fill: ink)[#title]
    #v(2.2mm)
    #text(size: 8.6pt, fill: muted)[
      #src
      #if url != "" [  ·  #link(url)[#text(fill: accent)[原文]] ]
    ]
    #v(1.4mm)
    #text(size: 8pt, fill: muted)[
      #if meta != "" [#meta]
      #if meta != "" and ratio != "" [  ·  ]
      #if ratio != "" [#ratio]
    ]
    #v(1.9mm)
    #line(length: 100%, stroke: .4pt + hair)
  ]

  body
}

// 点评块：左竖线 + 浅底，字号略小，独立缩进层级。
#let ping(body) = block(
  width: 100%,
  breakable: false,
  inset: (left: 4.6mm, right: 3.4mm, top: 3.2mm, bottom: 3.2mm),
  stroke: (left: 2.2pt + accent),
  fill: tint,
  above: 1.8em,
  below: .2em,
)[
  #set text(size: 9.5pt, fill: ink)
  #set par(leading: .8em, spacing: .5em, first-line-indent: (amount: 2em, all: true))
  #text(size: 8.2pt, weight: "bold", fill: accent, tracking: .2em)[点评]
  #v(-.1em)
  #body
]

// 数据表用的紧凑表格
#let tight-table(columns: 2, ..args) = table(
  columns: columns,
  stroke: none,
  inset: (x: 2mm, y: 1.1mm),
  align: (left, right),
  ..args,
)