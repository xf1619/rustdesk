#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成「远程桌面」定制客户端图标（PNG/ICO）。

设计：圆角方形底（蓝->青渐变）+ 白色显示器轮廓 + 右下角光标箭头。
所有图形在 4 倍画布上绘制后降采样，保证小尺寸边缘干净。
"""
import os
import sys
from PIL import Image, ImageDraw

SS = 4  # supersampling factor


def _gradient(size, color1, color2):
    """对角线性渐变。"""
    w = h = size
    base = Image.new("RGB", (w, h))
    px = base.load()
    for y in range(h):
        for x in range(w):
            t = (x + y) / (2.0 * (w - 1))
            px[x, y] = (
                int(color1[0] + (color2[0] - color1[0]) * t),
                int(color1[1] + (color2[1] - color1[1]) * t),
                int(color1[2] + (color2[2] - color1[2]) * t),
            )
    return base


def _rounded_mask(size, radius):
    m = Image.new("L", (size, size), 0)
    d = ImageDraw.Draw(m)
    d.rounded_rectangle([0, 0, size - 1, size - 1], radius=radius, fill=255)
    return m


def draw_icon(size, with_cursor=True, with_background=True):
    s = size * SS
    img = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    if with_background:
        bg = _gradient(s, (46, 107, 255), (0, 191, 166)).convert("RGBA")
        mask = _rounded_mask(s, int(s * 0.22))
        img.paste(bg, (0, 0), mask)

    white = (255, 255, 255, 255)

    # 显示器外框
    mx0, my0 = int(s * 0.14), int(s * 0.18)
    mx1, my1 = int(s * 0.78), int(s * 0.52)
    stroke = int(s * 0.046)
    d.rounded_rectangle([mx0, my0, mx1, my1], radius=int(s * 0.04), outline=white, width=stroke)

    # 屏幕内浅色填充（半透明深蓝，衬出层次）
    inset = stroke + int(s * 0.016)
    d.rounded_rectangle(
        [mx0 + inset, my0 + inset, mx1 - inset, my1 - inset],
        radius=int(s * 0.018),
        fill=(8, 46, 110, 60),
    )

    # 支架
    cx = int(s * 0.46)
    stem_w = int(s * 0.052)
    d.rectangle([cx - stem_w // 2, my1, cx + stem_w // 2, my1 + int(s * 0.08)], fill=white)
    base_w = int(s * 0.26)
    base_h = int(s * 0.038)
    by = my1 + int(s * 0.08)
    d.rounded_rectangle([cx - base_w // 2, by, cx + base_w // 2, by + base_h], radius=base_h // 2, fill=white)

    if with_cursor:
        # 屏幕内光标箭头（深蓝实心），表示"远程操作"
        ax, ay = int(s * 0.47), int(s * 0.255)
        w = int(s * 0.175)
        h = int(s * 0.185)
        unit = [
            (0.00, 0.00),
            (0.00, 0.895),
            (0.375, 0.658),
            (0.625, 1.00),
            (0.792, 0.947),
            (0.542, 0.621),
            (1.00, 0.621),
        ]
        pts = [(ax + int(u * w), ay + int(v * h)) for u, v in unit]
        d.polygon(pts, fill=(18, 52, 110, 255))

    return img.resize((size, size), Image.LANCZOS)


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else "."
    os.makedirs(out, exist_ok=True)

    master = draw_icon(1024, with_cursor=True)
    master.save(os.path.join(out, "icon-preview.png"))

    # 应用主图标
    master.resize((512, 512), Image.LANCZOS).save(os.path.join(out, "icon.png"))
    master.resize((256, 256), Image.LANCZOS).save(os.path.join(out, "128x128@2x.png"))
    master.resize((128, 128), Image.LANCZOS).save(os.path.join(out, "128x128.png"))
    master.resize((64, 64), Image.LANCZOS).save(os.path.join(out, "64x64.png"))
    master.resize((32, 32), Image.LANCZOS).save(os.path.join(out, "32x32.png"))

    # 多尺寸 ICO（应用 / Windows runner）
    for name in ("icon.ico", "app_icon.ico"):
        master.save(
            os.path.join(out, name),
            format="ICO",
            sizes=[(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)],
        )

    # 托盘图标：无光标，小尺寸更干净
    tray = draw_icon(256, with_cursor=False)
    tray.save(os.path.join(out, "tray-icon.ico"), format="ICO", sizes=[(16, 16), (20, 20), (24, 24), (32, 32)])
    print("ok:", out)


if __name__ == "__main__":
    main()
