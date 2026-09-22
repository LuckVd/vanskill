#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""figcraft 示例：一张链路图 + 一张时间线，演示全部常用元素。

运行：python3 example_gen_figs.py   （在任意目录，输出到 ./figcraft-sample/）
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from figstyle import (Canvas, INK, SUB, BLUE, BLUE_L, BLUE_B, RED, RED_L,
                      GREEN, GREEN_L, AMBER, AMBER_L, GRAY_L, GRAY_B)

OUT = "figcraft-sample"
os.makedirs(OUT, exist_ok=True)

# ---------- 图 1：三层链路图（卡片 + 箭头 + 分区 + 徽标） ----------
c = Canvas(1200, 560, title="示例：AI 辅助攻击链路")

c.panel(40, 90, 340, 380, "攻击者侧")
c.card(70, 140, 280, 80, "公开漏洞情报", sub="CVE / PoC 抓取")
c.card(70, 260, 280, 80, "LLM 改写利用代码", sub="提示注入 → 变体生成", fill=RED_L, stroke=RED)
c.badge(280, 130, "自动化")

c.panel(430, 90, 340, 380, "目标侧")
c.card(460, 140, 280, 80, "企业代码仓库", sub="含历史密钥")
c.card(460, 260, 280, 80, "CI/CD 流水线", sub="依赖安装阶段")

c.panel(820, 90, 340, 380, "防御侧")
c.card(850, 140, 280, 80, "SCA 依赖扫描", sub="提交前拦截", fill=GREEN_L, stroke=GREEN)
c.card(850, 260, 280, 80, "密钥轮换响应", sub="平均 4.2 小时", fill=GREEN_L, stroke=GREEN)

c.arrow(350, 180, 460, 180, label="投毒 PR")
c.arrow(600, 220, 600, 260, color=SUB, label="触发构建")
c.arrow(740, 300, 850, 180, color=GREEN, label="检出异常依赖")
c.arrow(990, 220, 990, 260, color=GREEN)

c.caption(520, "示例图：三种颜色只表达三条语义（主流程 / 攻击 / 防御），其余信息进副标题。")
c.save(os.path.join(OUT, "fig1-pipeline.png"))

# ---------- 图 2：时间线（dot + 日期 + 事件） ----------
t = Canvas(1200, 420, title="示例：72 小时处置时间线")

xs = [160, 440, 720, 1000]
t.line(120, 200, 1080, 200, color=GRAY_B, width=2)
events = [
    ("D0 09:00", "漏洞公开", "PoC 出现在 GitHub", AMBER, AMBER_L),
    ("D0 18:00", "首轮扫描", "内网 3 台主机命中", RED, RED_L),
    ("D1 12:00", "补丁上线", "全量灰度完成", BLUE, BLUE_L),
    ("D2 09:00", "复盘归档", "IOC 入库、规则回填", GREEN, GREEN_L),
]
for x, (d, title_, sub, col, fill) in zip(xs, events):
    t.dot(x, 200, r=7, fill=col)
    t.text(x, 150, d, fs=14, color=SUB, anchor="middle", bold=True)
    t.card(x - 110, 240, 220, 84, title_, sub=sub, fill=fill,
           stroke=col, fs=17)

t.caption(380, "时间线画法：主轴一条线，事件上下交错可避免文字拥挤（本例全放下方）。")
t.save(os.path.join(OUT, "fig2-timeline.png"))

print("done:", os.path.abspath(OUT))
