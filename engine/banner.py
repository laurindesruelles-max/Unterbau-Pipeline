"""Unterbau-Kanalbanner 2560x1440 (sicherer Bereich mittig 1546x423), 0 Credits.
Usage: python3 engine/banner.py assets/brand/profilbild.png assets/brand/banner.png"""
import sys, math
from PIL import Image, ImageDraw, ImageFont, ImageFilter
W, H = 2560, 1440
NAVY, ORANGE, CYAN, WHITE = (4, 23, 53), (255, 110, 3), (0, 247, 254), (255, 255, 255)
FD = "/usr/share/fonts/opentype/inter/"
logo_p, out = sys.argv[1], sys.argv[2]
im = Image.new("RGB", (W, H), NAVY)
# Hintergrund: großer Querschnitt (Ringe) rechts und links, sehr dezent
bg = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(bg)
def rings(cx, cy, r0, n, step, cut):
    for i in range(n):
        r = r0 + i * step; col = (CYAN if i % 2 else WHITE) + (34 if i % 2 else 22,)
        a0, a1 = cut
        d.arc([cx - r, cy - r, cx + r, cy + r], a1, a0 + 360, fill=col, width=10)
rings(2330, 720, 160, 9, 70, (-25, 25))
rings(230, 720, 160, 9, 70, (155, 205))
im.paste(bg.filter(ImageFilter.GaussianBlur(1.2)), (0, 0), bg)
# leichtes oranges Glimmen hinter dem Logo
glow = Image.new("RGBA", (W, H), (0, 0, 0, 0)); g = ImageDraw.Draw(glow)
lx, ly, ls = 830, 720, 330
g.ellipse([lx - 260, ly - 260, lx + 260, ly + 260], fill=ORANGE + (40,))
im.paste(glow.filter(ImageFilter.GaussianBlur(90)), (0, 0), glow.filter(ImageFilter.GaussianBlur(90)))
# Logo (Navy-Hintergrund des Profilbilds = Banner-Navy)
logo = Image.open(logo_p).convert("RGB").resize((ls, ls), Image.LANCZOS)
mask = Image.new("L", (ls, ls), 0); ImageDraw.Draw(mask).ellipse([4, 4, ls - 4, ls - 4], fill=255)
im.paste(logo, (lx - ls // 2, ly - ls // 2), mask)
# Schrift
d = ImageDraw.Draw(im)
f1 = ImageFont.truetype(FD + "InterDisplay-Black.otf", 170)
f2 = ImageFont.truetype(FD + "InterDisplay-Medium.otf", 58)
f3 = ImageFont.truetype(FD + "InterDisplay-Bold.otf", 40)
tx = 1040
d.text((tx, 545), "UNTERBAU", font=f1, fill=WHITE)
d.rectangle([tx + 4, 745, tx + 14, 812], fill=ORANGE)
d.text((tx + 36, 742), "Verstehen, wie die Welt funktioniert.", font=f2, fill=WHITE)
d.text((tx + 36, 832), "NEUES VIDEO ALLE 2 TAGE", font=f3, fill=ORANGE)
im.save(out, optimize=True)
print(out, im.size)
