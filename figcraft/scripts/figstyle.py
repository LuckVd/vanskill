#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""figcraft 公共绘图库：手写 SVG 结构元素 → rsvg-convert 出高清 PNG。

用法（在每个选题目录的 gen_figs.py 中）：

    from figstyle import Canvas, BLUE, INK, ...

    c = Canvas(1200, 640, title="上传链路")
    c.card(60, 120, 240, 90, "本地 Markdown", sub="master.md")
    c.arrow(300, 165, 380, 165, label="渲染")
    ...
    c.save("assets/fig1.png")          # 或 c.save_svg("assets/fig1.svg")

设计约定（与本项目已发表文章的图保持同一视觉语言）：
- 白底、墨色正文、蓝色主线条，红/绿/琥珀仅作强调；
- 统一 1200px 宽输出，字号 13-28，中文用 WenQuanYi Micro Hei；
- 所有坐标手工布局，卡片/箭头提供便捷方法保证对齐。
"""
import os
import shutil
import subprocess

# ---------- 配色 ----------
INK    = "#1E293B"   # 主文字/深色描边
SUB    = "#64748B"   # 次要文字
BLUE   = "#3B5BDB"   # 主色（线条、强调框）
BLUE_L = "#EEF2FF"   # 蓝浅底
BLUE_B = "#C7D2FE"   # 蓝边框
AMBER   = "#B45309"
AMBER_L = "#FEF3C7"
GREEN   = "#047857"
GREEN_L = "#ECFDF5"
RED     = "#E03131"
RED_L   = "#FFE3E3"
GRAY_L  = "#F1F5F9"
GRAY_B  = "#CBD5E1"
WHITE   = "#FFFFFF"

FONT = "WenQuanYi Micro Hei"


def esc(s: str) -> str:
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


class Canvas:
    """一张图。坐标单位为 px，宽度惯例 1200。"""

    def __init__(self, w=1200, h=640, title=None, bg=WHITE):
        self.w, self.h = w, h
        self.parts = []
        self.parts.append(f'<rect x="0" y="0" width="{w}" height="{h}" fill="{bg}"/>')
        self._marker_defs()
        if title:
            self.text(24, 44, title, fs=26, color=INK, bold=True, anchor="start")
            self.line(24, 58, w - 24, 58, color=GRAY_B, width=1.5)

    # ---------- 内部 ----------
    def _marker_defs(self):
        self.parts.append(
            '<defs>'
            f'<marker id="arr" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto">'
            f'<path d="M0,0 L8,3 L0,6 Z" fill="{BLUE}"/></marker>'
            f'<marker id="arrsub" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto">'
            f'<path d="M0,0 L8,3 L0,6 Z" fill="{SUB}"/></marker>'
            f'<marker id="arrred" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto">'
            f'<path d="M0,0 L8,3 L0,6 Z" fill="{RED}"/></marker>'
            f'<marker id="arrgreen" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto">'
            f'<path d="M0,0 L8,3 L0,6 Z" fill="{GREEN}"/></marker>'
            '</defs>\n')

    def _marker(self, color):
        return {BLUE: "url(#arr)", SUB: "url(#arrsub)",
                RED: "url(#arrred)", GREEN: "url(#arrgreen)"}.get(color, "url(#arr)")

    def raw(self, svg: str):
        self.parts.append(svg)

    # ---------- 基础元素 ----------
    def text(self, x, y, s, fs=15, color=INK, anchor="start", bold=False):
        fw = "600" if bold else "normal"
        self.parts.append(
            f'<text x="{x}" y="{y}" font-family="{FONT}" font-size="{fs}" '
            f'font-weight="{fw}" fill="{color}" text-anchor="{anchor}">{esc(s)}</text>')

    def rect(self, x, y, w, h, fill, stroke, rx=10, dash="", sw=1.5):
        d = f' stroke-dasharray="{dash}"' if dash else ""
        self.parts.append(
            f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" '
            f'stroke="{stroke}" stroke-width="{sw}"{d}/>')

    def line(self, x1, y1, x2, y2, color=GRAY_B, width=1.5, dash="", arrow=False):
        d = f' stroke-dasharray="{dash}"' if dash else ""
        m = f' marker-end="{self._marker(color)}"' if arrow else ""
        self.parts.append(
            f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" '
            f'stroke-width="{width}"{d}{m}/>')

    def dot(self, x, y, r=5, fill=BLUE):
        self.parts.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{fill}"/>')

    # ---------- 复合元素 ----------
    def card(self, x, y, w, h, label, sub=None, fill=BLUE_L, stroke=BLUE_B,
             color=INK, fs=16, rx=10, dash="", bold=True, icon=None):
        """卡片：可选副标题与左上角小图标文字。文字自动垂直居中。"""
        self.rect(x, y, w, h, fill, stroke, rx=rx, dash=dash)
        cy = y + h / 2
        if sub:
            self.text(x + w / 2, cy - 4, label, fs=fs, color=color, anchor="middle", bold=bold)
            self.text(x + w / 2, cy + 16, sub, fs=fs - 4, color=SUB, anchor="middle")
        else:
            self.text(x + w / 2, cy + fs / 3, label, fs=fs, color=color, anchor="middle", bold=bold)
        if icon:
            self.text(x + 10, y + 20, icon, fs=13, color=SUB, anchor="start")

    def arrow(self, x1, y1, x2, y2, color=BLUE, dash="", label=None, lx=None, ly=None, fs=13):
        """带箭头连线，label 默认放在中点上方。"""
        self.line(x1, y1, x2, y2, color=color, width=1.8, dash=dash, arrow=True)
        if label:
            lx = (x1 + x2) / 2 if lx is None else lx
            ly = (y1 + y2) / 2 - 8 if ly is None else ly
            self.text(lx, ly, label, fs=fs, color=color if color != BLUE else BLUE, anchor="middle")

    def badge(self, x, y, label, fill=RED_L, color=RED, fs=12, pad=8):
        """小标签（无宽自适应近似：按字数估宽）。"""
        w = int(fs * len(label) * 1.05) + pad * 2
        h = fs + pad + 6
        self.rect(x, y, w, h, fill, "none", rx=h / 2)
        self.text(x + w / 2, y + h / 2 + fs / 3, label, fs=fs, color=color, anchor="middle", bold=True)
        return w  # 返回宽度便于横向排布

    def caption(self, y, s, fs=13):
        """图底注释。"""
        self.text(self.w / 2, y, s, fs=fs, color=SUB, anchor="middle")

    def panel(self, x, y, w, h, title=None, fill=GRAY_L, stroke=GRAY_B, dash=""):
        """分区底板（虚线分组框），标题放在左上角内侧。"""
        self.rect(x, y, w, h, fill, stroke, rx=12, dash=dash or "6 4")
        if title:
            self.text(x + 14, y + 24, title, fs=14, color=SUB, anchor="start", bold=True)

    # ---------- 输出 ----------
    def svg(self) -> str:
        return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.w}" height="{self.h}" '
                f'viewBox="0 0 {self.w} {self.h}">\n' + "\n".join(self.parts) + "\n</svg>\n")

    def save_svg(self, path):
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(self.svg())
        return path

    def save(self, path, width=1200):
        """写出 PNG。优先 rsvg-convert，其次 cairosvg；都没有则报清晰错误。"""
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        svg_tmp = (os.path.splitext(path)[0] if path.endswith(".png") else path) + ".svg.tmp"
        self.save_svg(svg_tmp)
        try:
            if shutil.which("rsvg-convert"):
                subprocess.run(["rsvg-convert", "-w", str(width), svg_tmp, "-o", path], check=True)
            else:
                import cairosvg  # 可选回退
                cairosvg.svg2png(url=svg_tmp, write_to=path, output_width=width)
        finally:
            os.remove(svg_tmp)
        return path


def png_width(px=1200, scale=2):
    """导出更高清时把 width 传成 1200*scale。"""
    return px * scale
