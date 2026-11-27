"""Makes the Stream Deck button icons (144x144 PNG) in your colours.

Run again after changing colours in config.yaml:
    .venv/bin/python tools/make_icons.py
The icons land in the  stream-deck-icons  folder.
"""
import math
import random
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE))
from settings import load_config  # noqa: E402

S = 4                    # draw 4x bigger, then shrink: smooth edges
SIZE = 144
OUT = HERE / "stream-deck-icons"


def rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def font(px, weight="SemiBold"):
    return ImageFont.truetype(str(HERE / "fonts" / f"Inter-{weight}.ttf"), px * S)


def base(colours, top=None):
    """Rounded Marine Blue tile with a soft top-to-bottom gradient."""
    n = SIZE * S
    top = rgb(top or colours["primary"])
    bottom = rgb(colours["deep"])
    grad = Image.new("RGB", (1, n))
    for y in range(n):
        t = y / (n - 1)
        grad.putpixel((0, y), tuple(int(a + (b - a) * t) for a, b in zip(top, bottom)))
    return grad.resize((n, n)).convert("RGBA")


def label(img, text, colour):
    d = ImageDraw.Draw(img)
    d.text((SIZE * S / 2, 118 * S), text, font=font(17), fill=colour, anchor="mm")


def finish(img, name):
    img = img.resize((SIZE, SIZE), Image.LANCZOS)
    img.save(OUT / f"{name}.png")


def main():
    c = load_config()["colours"]
    white, accent = rgb(c["text"]), rgb(c["accent"])
    gold, coral = (233, 196, 106), (224, 122, 95)
    OUT.mkdir(exist_ok=True)
    k = S  # shorthand for "points"

    # Key word: a small card with a text line and accent stripe
    img = base(c); d = ImageDraw.Draw(img)
    d.rounded_rectangle((30 * k, 34 * k, 114 * k, 82 * k), 10 * k, fill=white)
    d.rounded_rectangle((40 * k, 44 * k, 45 * k, 72 * k), 3 * k, fill=accent)
    d.text((80 * k, 58 * k), "Aa", font=font(26, "Bold"), fill=rgb(c["primary"]), anchor="mm")
    label(img, "Key word", white); finish(img, "keyword")

    # Confetti: tumbling paper pieces
    img = base(c); d = ImageDraw.Draw(img)
    rnd = random.Random(7)
    palette = [white, accent, gold, coral, (168, 218, 220)]
    for i in range(16):
        cx, cy = rnd.uniform(26, 118), rnd.uniform(22, 92)
        w, h, a = rnd.uniform(9, 14), rnd.uniform(5, 7), rnd.uniform(0, math.pi)
        pts = [(cx + dx * math.cos(a) - dy * math.sin(a), cy + dx * math.sin(a) + dy * math.cos(a))
               for dx, dy in ((-w / 2, -h / 2), (w / 2, -h / 2), (w / 2, h / 2), (-w / 2, h / 2))]
        d.polygon([(x * k, y * k) for x, y in pts], fill=palette[i % len(palette)])
    label(img, "Confetti", white); finish(img, "confetti")

    # Countdown: progress ring with "5:00"
    img = base(c); d = ImageDraw.Draw(img)
    box = (34 * k, 18 * k, 110 * k, 94 * k)
    d.ellipse(box, outline=rgb(c["deep"]), width=7 * k)
    d.arc(box, -90, 200, fill=accent, width=7 * k)
    d.text((72 * k, 56 * k), "5:00", font=font(21, "SemiBold"), fill=white, anchor="mm")
    label(img, "Countdown", white); finish(img, "countdown")

    # Logo: a frame with a small mark in the top-left corner
    img = base(c); d = ImageDraw.Draw(img)
    d.rounded_rectangle((26 * k, 26 * k, 118 * k, 90 * k), 8 * k, outline=white, width=4 * k)
    d.rounded_rectangle((34 * k, 34 * k, 56 * k, 56 * k), 5 * k, fill=accent)
    label(img, "Logo", white); finish(img, "logo")

    # Warm glow: soft warm sun
    img = base(c); glow = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(glow).ellipse((36 * k, 18 * k, 108 * k, 90 * k), fill=(255, 184, 112, 200))
    img = Image.alpha_composite(img, glow.filter(ImageFilter.GaussianBlur(12 * k)))
    d = ImageDraw.Draw(img)
    d.ellipse((54 * k, 36 * k, 90 * k, 72 * k), fill=(255, 214, 160))
    label(img, "Warm glow", white); finish(img, "glow")

    # Back in a moment: three calm dots under a pause bar pair
    img = base(c, top=c["deep"]); d = ImageDraw.Draw(img)
    d.rounded_rectangle((56 * k, 28 * k, 66 * k, 66 * k), 4 * k, fill=white)
    d.rounded_rectangle((78 * k, 28 * k, 88 * k, 66 * k), 4 * k, fill=white)
    for i, shade in enumerate((0.45, 0.75, 1.0)):
        col = tuple(int(a * shade + b * (1 - shade)) for a, b in zip(accent, rgb(c["deep"])))
        d.ellipse(((60 + i * 12) * k - 4 * k, 82 * k, (60 + i * 12) * k + 4 * k, 90 * k), fill=col)
    label(img, "Back soon", white); finish(img, "brb")

    # Clear all: a soft coral tile with a cross
    img = base(c, top="#E07A5F"); d = ImageDraw.Draw(img)
    for a, b in (((50, 32), (94, 76)), ((94, 32), (50, 76))):
        d.line((a[0] * k, a[1] * k, b[0] * k, b[1] * k), fill=white, width=9 * k)
    for x, y in ((50, 32), (94, 76), (94, 32), (50, 76)):
        d.ellipse(((x - 4.5) * k, (y - 4.5) * k, (x + 4.5) * k, (y + 4.5) * k), fill=white)
    label(img, "Clear all", white); finish(img, "clear")

    # Slides: a slide card beside a small person
    img = base(c); d = ImageDraw.Draw(img)
    d.ellipse((22 * k, 40 * k, 40 * k, 58 * k), fill=white)
    d.rounded_rectangle((16 * k, 62 * k, 46 * k, 92 * k), 10 * k, fill=white)
    d.rounded_rectangle((54 * k, 30 * k, 126 * k, 82 * k), 6 * k, fill=white)
    d.rectangle((54 * k + 5 * k, 30 * k + 5 * k, 76 * k, 82 * k - 5 * k), fill=accent)
    d.rounded_rectangle((82 * k, 46 * k, 118 * k, 51 * k), 2 * k, fill=rgb(c["primary"]))
    d.rounded_rectangle((82 * k, 57 * k, 108 * k, 61 * k), 2 * k, fill=accent)
    label(img, "Slides", white); finish(img, "slides")

    # Next / previous slide: a big chevron
    for name, text, pts in (("slide-next", "Next slide", ((58, 30), (86, 58), (58, 86))),
                            ("slide-prev", "Prev slide", ((86, 30), (58, 58), (86, 86)))):
        img = base(c); d = ImageDraw.Draw(img)
        d.line([(x * k, y * k) for x, y in pts], fill=white, width=11 * k, joint="curve")
        for x, y in (pts[0], pts[2]):
            d.ellipse(((x - 5.5) * k, (y - 5.5) * k, (x + 5.5) * k, (y + 5.5) * k), fill=white)
        label(img, text, white); finish(img, name)

    # Poll: green and red result bars
    for name, text in (("poll", "Poll"), ("poll-next", "Next poll")):
        img = base(c); d = ImageDraw.Draw(img)
        d.rounded_rectangle((30 * k, 26 * k, 70 * k, 54 * k), 7 * k, fill=(62, 158, 100))
        d.rounded_rectangle((74 * k, 26 * k, 114 * k, 54 * k), 7 * k, fill=(214, 76, 69))
        d.text((50 * k, 40 * k), "JA", font=font(13, "Bold"), fill=white, anchor="mm")
        d.text((94 * k, 40 * k), "NEE", font=font(13, "Bold"), fill=white, anchor="mm")
        d.rounded_rectangle((30 * k, 68 * k, 114 * k, 73 * k), 2 * k, fill=(214, 76, 69))
        d.rounded_rectangle((30 * k, 68 * k, 82 * k, 73 * k), 2 * k, fill=(62, 158, 100))
        d.ellipse((76 * k, 64 * k, 88 * k, 76 * k), fill=white)
        if name == "poll-next":
            d.line((100 * k, 84 * k, 110 * k, 92 * k, 100 * k, 100 * k), fill=white, width=4 * k, joint="curve")
        label(img, text, white); finish(img, name)

    print(f"Icons saved in {OUT}")


if __name__ == "__main__":
    main()
