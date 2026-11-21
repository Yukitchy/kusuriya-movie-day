#!/usr/bin/env python3
"""OGP候補5案を img/ の素材から生成する。出力は og/og1.jpg〜og5.jpg"""
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import os

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, "img"); OUT = os.path.join(HERE, "og")
os.makedirs(OUT, exist_ok=True)
W, H = 1200, 630
INK = (18, 18, 18); RED = (14, 107, 92); CREAM = (246, 241, 230); WHITE = (255, 255, 255)
JP = "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"
AC = "/home/hatch/workspace/akiba-welcome-work/ogp-new/fonts/Archivo.ttf"
TITLE = "都内で『薬屋』を観る日"
SUB = "劇場版『亡妃の秘宝』＋ランチ｜ヨシくんへのお誘い"


def cover(im, w, h, cy=.5, cx=.5):
    iw, ih = im.size; s = max(w / iw, h / ih)
    nw, nh = int(iw * s) + 1, int(ih * s) + 1
    im = im.resize((nw, nh), Image.LANCZOS)
    x = int((nw - w) * cx); y = int((nh - h) * cy)
    return im.crop((x, y, x + w, y + h))


def font(path, size):
    return ImageFont.truetype(path, size)


def fit(path, text, box_w, start, floor=28):
    s = start
    while s > floor:
        f = font(path, s)
        if ImageDraw.Draw(Image.new("RGB", (8, 8))).textbbox((0, 0), text, font=f)[2] <= box_w:
            return f
        s -= 4
    return font(path, floor)


def save(im, n):
    im.convert("RGB").save(os.path.join(OUT, f"og{n}.jpg"), quality=88)
    print("og", n, im.size)


kv = Image.open(os.path.join(IMG, "kv.jpg"))
kv2 = Image.open(os.path.join(IMG, "kv2.jpg"))
cin = Image.open(os.path.join(IMG, "cinema.jpg"))

# 案1：KV全面＋下部バンド
base = cover(kv, W, H, cy=.32)
d = ImageDraw.Draw(base)
d.rectangle([0, H - 178, W, H], fill=INK)
d.rectangle([0, H - 190, W, H - 178], fill=RED)
d.text((48, H - 168), TITLE, font=fit(JP, TITLE, W - 96, 72), fill=WHITE)
d.text((50, H - 62), SUB, font=fit(JP, SUB, W - 100, 32), fill=(205, 198, 186))
save(base, 1)

# 案2：第2弾KV左＋クリーム右にタイトル
base = Image.new("RGB", (W, H), CREAM)
base.paste(cover(kv2, 660, H, cy=.4), (0, 0))
d = ImageDraw.Draw(base)
d.rectangle([660, 0, 672, H], fill=RED)
d.text((716, 110), "MOVIE DAY", font=font(AC, 40), fill=RED)
d.text((712, 176), "都内で\n『薬屋』を\n観る日", font=font(JP, 68), fill=INK, spacing=8)
d.text((716, 486), "劇場版『亡妃の秘宝』\n12.11 FRI 公開", font=font(JP, 32), fill=(93, 90, 84), spacing=6)
save(base, 2)

# 案3：3枚コラージュ＋黒の上帯
base = Image.new("RGB", (W, H), INK)
band = 150
for i, (im, cy) in enumerate([(kv, .3), (kv2, .35), (cin, .55)]):
    base.paste(cover(im, 400, H - band, cy=cy), (i * 400, band))
d = ImageDraw.Draw(base)
d.text((48, 28), TITLE, font=fit(JP, TITLE, W - 96, 72), fill=WHITE)
d.rectangle([48, 124, 228, 132], fill=(217, 52, 43))
save(base, 3)

# 案4：緑背景＋タイポグラフィのみ
base = Image.new("RGB", (W, H), RED)
d = ImageDraw.Draw(base)
d.text((60, 66), "KUSURIYA NO HITORIGOTO — THE MOVIE", font=font(AC, 36), fill=(127, 209, 192))
d.text((56, 150), "薬屋の劇場版を、都内で。", font=fit(JP, "薬屋の劇場版を、都内で。", W - 112, 92), fill=WHITE)
d.text((60, 292), "劇場版『薬屋のひとりごと 亡妃の秘宝』", font=fit(JP, "劇場版『薬屋のひとりごと 亡妃の秘宝』", W - 120, 52), fill=WHITE)
d.rectangle([60, 396, W - 60, 402], fill=WHITE)
d.text((60, 438), "12.11 FRI 公開｜都内6劇場＋劇場近くのランチ12軒", font=fit(JP, "12.11 FRI 公開｜都内6劇場＋劇場近くのランチ12軒", W - 120, 44), fill=WHITE)
save(base, 4)

# 案5：劇場の座席全面＋上部クリーム帯
base = cover(cin, W, H, cy=.6).filter(ImageFilter.GaussianBlur(.4))
d = ImageDraw.Draw(base)
d.rectangle([0, 0, W, 190], fill=CREAM)
d.rectangle([0, 190, W, 202], fill=RED)
d.text((48, 30), TITLE, font=fit(JP, TITLE, W - 96, 80), fill=INK)
d.text((50, 132), SUB, font=fit(JP, SUB, W - 100, 34), fill=(93, 90, 84))
save(base, 5)
