# -*- coding: utf-8 -*-
"""
ZRH 作品集 · 版式生成器
从 21 页 SVG 反推出的设计系统，用干净的方式重建「项目页」版式。

用法：
    python ds_page.py            # 生成 demo 页 + 打印统计
所有坐标为 1122×794 画布下的绝对坐标，与原件逐像素对齐。
"""
from __future__ import annotations

import base64
import html
import mimetypes
import os
from dataclasses import dataclass, field
from pathlib import Path

# ─────────────────────────── 设计令牌 ───────────────────────────
W, H = 1122, 794

C_BG = "#111111"      # 页面底色
C_PANEL = "#171717"   # 卡片 / 右栏
C_ORANGE = "#F27314"  # 主强调
C_AMBER = "#E6AC47"   # 次强调 / 编号
C_TEAL = "#8AC0B1"    # 第三色
C_TEXT = "#F4EBDD"    # 主文字
C_MUTED = "#8A7B68"   # 次级文字 / 细线
C_BODY = "#CFC8BB"    # 方框正文

F_CN = "'Source Han Sans SC','Noto Sans SC','Microsoft YaHei',sans-serif"
F_EN = "Arial,'Helvetica Neue',sans-serif"

# 栅格
MARGIN = 38
FRAME = (16, 16, 1090, 762)
LEFT = (38, 205, 640, 492)
RIGHT = (708, 205, 374, 492)
GAP = 30

# 页头 / 页脚基线
HEADER_BASE = 51
FOOTER_RULE = 750
FOOTER_BASE = 769


# ─────────────────────────── 基础图元 ───────────────────────────
def esc(s: str) -> str:
    return html.escape(str(s), quote=False)


def text(x, y, s, size, fill, bold=False, family=F_CN, anchor="start",
         tracking=0, opacity=None):
    """一行文字。tracking 单位 em，正数放宽。"""
    w = "700" if bold else "400"
    extra = f' letter-spacing="{tracking}em"' if tracking else ""
    extra += f' opacity="{opacity}"' if opacity is not None else ""
    return (
        f'<text x="{x}" y="{y}" font-family="{family}" font-size="{size}" '
        f'font-weight="{w}" fill="{fill}" text-anchor="{anchor}"{extra}>'
        f'{esc(s)}</text>'
    )


def rect(x, y, w, h, fill="none", stroke=None, sw=1.3):
    s = f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}"'
    if stroke:
        s += f' stroke="{stroke}" stroke-width="{sw}"'
    return s + "/>"


def line(x1, y1, x2, y2, stroke=C_AMBER, sw=1.2):
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{stroke}" stroke-width="{sw}"/>'


# ─────────────────────────── 页面骨架 ───────────────────────────
def header(section_label: str, page_no: str) -> str:
    """页头：logo + 板块名 + 页码。"""
    return "\n".join([
        text(MARGIN, HEADER_BASE, "ZRH", 20, C_TEXT, bold=True, family=F_EN),
        text(MARGIN + 62, HEADER_BASE, section_label.upper(), 11, C_MUTED,
             bold=True, family=F_EN, tracking=0.14),
        text(1082, HEADER_BASE, page_no, 13, C_TEXT, bold=True, family=F_EN, anchor="end"),
    ])


def frame(accent=C_ORANGE) -> str:
    """外框 + 顶部三色条。"""
    x, y, w, h = FRAME
    return "\n".join([
        rect(x, y, w, h, stroke=accent, sw=2),
        rect(x, y, 363, 5, fill=accent),
        rect(x + 363, y, 363, 5, fill=C_AMBER),
        rect(x + 726, y, 364, 5, fill=C_TEAL),
    ])


def footer(caption="VISUAL DESIGN PORTFOLIO") -> str:
    return "\n".join([
        line(MARGIN, FOOTER_RULE, 1082, FOOTER_RULE, stroke=C_MUTED, sw=1),
        text(MARGIN, FOOTER_BASE, caption, 9, C_MUTED, bold=True, family=F_EN, tracking=0.06),
    ])


def title_block(section_no: str, cn_title: str, sub: str) -> str:
    """大数字 + 中文标题 + 副标题 + 琥珀分隔线。"""
    return "\n".join([
        text(MARGIN, 145, section_no, 64, C_AMBER, bold=True, family=F_EN),
        text(158, 126, cn_title, 28, C_TEXT, bold=True),
        text(160, 157, sub, 14, C_MUTED),
        line(MARGIN, 181, 1082, 181, stroke=C_AMBER, sw=1.2),
    ])


def image_frame(img_path: str | None, x, y, w, h, stroke=C_AMBER, sw=1.3) -> str:
    """按 cover 方式填满框（clipPath 裁切），无图时画占位。"""
    cid = f"clip{abs(hash((x, y, w, h))) % 10**8}"
    if img_path and os.path.exists(img_path):
        mime = mimetypes.guess_type(img_path)[0] or "image/jpeg"
        b64 = base64.b64encode(Path(img_path).read_bytes()).decode()
        inner = (f'<image x="{x}" y="{y}" width="{w}" height="{h}" '
                 f'preserveAspectRatio="xMidYMid slice" '
                 f'xlink:href="data:{mime};base64,{b64}"/>')
    else:
        inner = (rect(x, y, w, h, fill=C_PANEL)
                 + rect(x, y, w, h, stroke=C_MUTED, sw=0.5)
                 + text(x + w / 2, y + h / 2, f"IMAGE {int(w)}×{int(h)}",
                        10, C_MUTED, family=F_EN, anchor="middle"))
    return (f'<clipPath id="{cid}">{rect(x, y, w, h)}</clipPath>'
            f'<g clip-path="url(#{cid})">{inner}</g>'
            + rect(x, y, w, h, stroke=stroke, sw=sw))


def side_panel(en: str, cn: str, desc: str, label: str, lines: list[str],
               sign="ZRH / 2026", box_h=None) -> str:
    """右栏：英文名 / 中文名 / 一句说明 / 细线 / 标签 / 方框正文 / 署名。"""
    x, y, w, h = RIGHT
    ix = x + 27
    body_y = 411.5
    step = 17
    if box_h is None:
        box_h = min(len(lines) * step + 22, 222)
    parts = [
        rect(x, y, w, h, fill=C_PANEL, stroke=C_AMBER, sw=1.3),
        text(ix, 250, en, 12, C_AMBER, bold=True),
        text(ix, 292, cn, 20, C_TEXT, bold=True),
        text(ix, 323, desc, 14, C_MUTED),
        line(ix, 350, ix + 321, 350, stroke=C_MUTED, sw=0.5),
        text(ix, 381, label, 10, C_AMBER),
        rect(ix, 389.5, 320, box_h, stroke=C_AMBER, sw=1.3),
    ]
    for i, ln in enumerate(lines):
        parts.append(text(ix + 10, body_y + i * step, ln, 10.5, C_BODY))
    parts.append(text(ix, 653, sign, 12, C_TEXT, bold=True, family=F_EN))
    return "\n".join(parts)


@dataclass
class Page:
    page_no: str
    section_label: str
    section_no: str
    cn_title: str
    sub: str
    en: str
    panel_cn: str
    panel_desc: str
    label: str
    body: list[str] = field(default_factory=list)
    images: list = field(default_factory=list)   # [(path, x, y, w, h)]
    accent: str = C_ORANGE

    def render(self) -> str:
        layers = [
            rect(0, 0, W, H, fill=C_BG),
            frame(self.accent),
            header(self.section_label, self.page_no),
            title_block(self.section_no, self.cn_title, self.sub),
            rect(*LEFT, stroke=C_AMBER, sw=1.3),
        ]
        for im in self.images:
            layers.append(image_frame(*im))
        layers.append(side_panel(self.en, self.panel_cn, self.panel_desc,
                                 self.label, self.body))
        layers.append(footer())
        return (f'<svg xmlns="http://www.w3.org/2000/svg" '
                f'xmlns:xlink="http://www.w3.org/1999/xlink" '
                f'width="{W}" height="{H}" viewBox="0 0 {W} {H}">\n'
                + "\n".join(layers) + "\n</svg>\n")


# ─────────────────────────── demo ───────────────────────────
if __name__ == "__main__":
    demo = Page(
        page_no="/05",
        section_label="PROJECT ARCHIVE",
        section_no="01",
        cn_title="AIGC辅助生图&应用",
        sub="通过AI生图以及后期修改精准控制生图效果",
        en="Generate E-commerce Product Detail Page",
        panel_cn="电商详情页生成",
        panel_desc="通过prompt控制画面效果与布局",
        label="其一prompt:",
        body=[
            "Homepage design for sports trend e-commerce, brand name: ZRH.",
            "Special page for sneakers & athletic gear. Style: Sport Tech,",
            "Athletic Streetwear, Neo-commercial. High contrast, clean,",
            "strong visual hierarchy. Deep black base with electric lime",
            "accents, oversized bold typography, full-bleed imagery.",
            "Layout: fixed top nav, hero, horizontal product cards.",
        ],
        images=[
            (None, 53.6, 283.8, 189.1, 336.0),
            (None, 255.7, 283.8, 203.9, 335.9),
            (None, 472.6, 283.8, 189.1, 335.9),
        ],
    )
    out = Path("demo-project-page.svg")
    out.write_text(demo.render(), encoding="utf-8")
    print(f"wrote {out} ({out.stat().st_size/1024:.1f} KB)")
