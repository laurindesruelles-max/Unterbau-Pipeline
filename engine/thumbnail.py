"""Unterbau-Thumbnail-Vorlage (Laurin): Bild ohne Text aus Higgsfield, Text als feste Vorlage darüber.
Kasten rechts: dunkel halbdurchsichtig rgba(5,14,30,200), Radius 22, oranger Balken links (255,122,26),
Inter Display Black, Zeile 1 weiß, Schlüsselwort orange, 2–3 Wörter in Groß-/Kleinschreibung. Export 1280x720.

python3 engine/thumbnail.py <bild.png> <out.jpg> "Nur ein" "Kabel."      (letzte Zeile = orange)
"""
import sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter
FB = "/usr/share/fonts/opentype/inter/InterDisplay-Black.otf"
ORANGE = (255, 122, 26)

def make(src, out, lines, side="right"):
    W, H = 1344, 752
    im = Image.open(src).convert("RGB")
    s = max(W/im.width, H/im.height); im = im.resize((int(im.width*s)+1, int(im.height*s)+1), Image.LANCZOS)
    im = im.crop(((im.width-W)//2, (im.height-H)//2, (im.width-W)//2+W, (im.height-H)//2+H)).convert("RGBA")
    f = ImageFont.truetype(FB, 118); d = ImageDraw.Draw(im)
    tw = max(d.textlength(l, font=f) for l in lines); lh = 128
    bw, bh = int(tw+110), int(len(lines)*lh+70)
    x0 = W-bw-56 if side == "right" else 56; y0 = (H-bh)//2
    sh = Image.new("RGBA", im.size, (0, 0, 0, 0)); ImageDraw.Draw(sh).rounded_rectangle([x0+8, y0+12, x0+bw+8, y0+bh+12], 22, fill=(0, 0, 0, 120))
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(14)))
    p = Image.new("RGBA", im.size, (0, 0, 0, 0)); pd = ImageDraw.Draw(p)
    pd.rounded_rectangle([x0, y0, x0+bw, y0+bh], 22, fill=(5, 14, 30, 200)); pd.rounded_rectangle([x0, y0, x0+14, y0+bh], 6, fill=ORANGE+(255,))
    im.alpha_composite(p); d = ImageDraw.Draw(im)
    for i, l in enumerate(lines):
        d.text((x0+56, y0+30+i*lh), l, font=f, fill=(ORANGE if i == len(lines)-1 else (255, 255, 255))+(255,))
    im.convert("RGB").resize((1280, 720), Image.LANCZOS).save(out, quality=92)

if __name__ == "__main__":
    make(sys.argv[1], sys.argv[2], sys.argv[3:])
