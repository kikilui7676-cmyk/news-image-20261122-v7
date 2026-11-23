#!/usr/bin/env python3
"""Render the v7 'classic broadsheet' front page for Sunday 22 November 2026.

Draws a 1024x1024 PNG (entry.png) in the style of a traditional elite
newspaper: serif masthead, ruled dateline bar, a lead story across the
top, and ten more stories in three ruled columns. Deterministic: pure
Pillow drawing from fixed strings, no randomness, no external assets
beyond the DejaVu fonts.
"""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

W = H = 1024
MARGIN = 34
CONTENT_W = W - 2 * MARGIN
INK = (18, 18, 18)
GREY = (90, 90, 90)
WHITE = (255, 255, 255)

FONT_DIR = "/usr/share/fonts/truetype/dejavu"


def font(name, size):
    return ImageFont.truetype(f"{FONT_DIR}/{name}", size)


SERIF = "DejaVuSerif.ttf"
SERIF_B = "DejaVuSerif-Bold.ttf"
SANS = "DejaVuSans.ttf"
SANS_B = "DejaVuSans-Bold.ttf"


def text_w(draw, s, f):
    return draw.textlength(s, font=f)


def spaced_w(draw, s, f, tracking):
    return sum(draw.textlength(ch, font=f) for ch in s) + tracking * max(0, len(s) - 1)


def draw_spaced(draw, x, y, s, f, tracking, fill=INK):
    """Draw letter-spaced text starting at x; return the end x."""
    cx = x
    for ch in s:
        draw.text((cx, y), ch, font=f, fill=fill)
        cx += draw.textlength(ch, font=f) + tracking
    return cx - tracking


def draw_spaced_centered(draw, cx, y, s, f, tracking, fill=INK):
    w = spaced_w(draw, s, f, tracking)
    return draw_spaced(draw, cx - w / 2, y, s, f, tracking, fill)


def wrap(draw, s, f, max_w):
    words = s.split()
    lines, cur = [], ""
    for word in words:
        trial = word if not cur else cur + " " + word
        if text_w(draw, trial, f) <= max_w:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def rule(draw, y, x0=MARGIN, x1=W - MARGIN, width=1, fill=INK):
    draw.line([(x0, y), (x1, y)], fill=fill, width=width)


def story(draw, x, y, col_w, kicker, headline, summary):
    """Draw one column story; return y just below it."""
    kf = font(SANS_B, 14)
    hf = font(SERIF_B, 23)
    bf = font(SERIF, 17)
    draw_spaced(draw, x, y, kicker, kf, 1.2, fill=GREY)
    y += 19
    for line in wrap(draw, headline, hf, col_w):
        draw.text((x, y), line, font=hf, fill=INK)
        y += 26
    y += 2
    for line in wrap(draw, summary, bf, col_w):
        draw.text((x, y), line, font=bf, fill=INK)
        y += 21
    return y


def column(draw, x, y_top, col_w, items, y_bottom):
    y = y_top
    for i, (kicker, headline, summary) in enumerate(items):
        if i:
            rule(draw, y + 4, x0=x, x1=x + col_w, width=1, fill=(170, 170, 170))
            y += 13
        y = story(draw, x, y, col_w, kicker, headline, summary)
    return y


def main():
    img = Image.new("RGB", (W, H), WHITE)
    d = ImageDraw.Draw(img)

    # ---- top rules + eyebrow line -------------------------------------
    rule(d, 22, width=3)
    rule(d, 29, width=1)
    eyebrow = font(SANS_B, 14)
    draw_spaced(d, MARGIN, 40, "VOL. I - No. 22", eyebrow, 1.2, fill=GREY)
    label = "ALL THE DAY'S NEWS - ON ONE PAGE"
    lw = spaced_w(d, label, eyebrow, 1.2)
    draw_spaced(d, W - MARGIN - lw, 40, label, eyebrow, 1.2, fill=GREY)

    # ---- masthead ------------------------------------------------------
    masthead = font(SERIF_B, 58)
    title = "The World in One Image"
    tw = text_w(d, title, masthead)
    d.text(((W - tw) / 2, 56), title, font=masthead, fill=INK)

    # ---- dateline bar --------------------------------------------------
    rule(d, 130, width=1)
    rule(d, 134, width=3)
    date_f = font(SANS_B, 33)
    draw_spaced_centered(d, W / 2, 146, "SUNDAY 22 NOVEMBER 2026", date_f, 3)
    rule(d, 192, width=3)
    rule(d, 196, width=1)

    # ---- lead story ----------------------------------------------------
    y = 212
    kick_f = font(SANS_B, 17)
    draw_spaced(d, MARGIN, y, "ANTALYA, TURKEY - CLIMATE SUMMIT", kick_f, 1.5)
    y += 28
    lead_h = font(SERIF_B, 54)
    d.text((MARGIN, y), "COP31 Ends Without a Deal", font=lead_h, fill=INK)
    y += 68
    lead_b = font(SERIF, 20)
    lead_text = (
        "Nearly 200 countries ended the COP31 climate summit in Antalya "
        "without an overall agreement, deadlocked over how fast to phase "
        "out fossil fuels and who should pay for climate finance. After "
        "two weeks of talks, delegates went home with no deal - and a "
        "promise to try again next year."
    )
    for line in wrap(d, lead_text, lead_b, CONTENT_W):
        d.text((MARGIN, y), line, font=lead_b, fill=INK)
        y += 27

    # ---- section header ------------------------------------------------
    y += 14
    rule(d, y, width=1)
    sec_f = font(SANS_B, 16)
    sec = "AROUND THE WORLD"
    sw = spaced_w(d, sec, sec_f, 4)
    d.rectangle([W / 2 - sw / 2 - 14, y - 9, W / 2 + sw / 2 + 14, y + 15], fill=WHITE)
    draw_spaced(d, W / 2 - sw / 2, y - 8, sec, sec_f, 4)
    y += 26

    # ---- columns -------------------------------------------------------
    gutter = 26
    col_w = (CONTENT_W - 2 * gutter) // 3
    xs = [MARGIN, MARGIN + col_w + gutter, MARGIN + 2 * (col_w + gutter)]
    # vertical rules between columns
    for gx in (xs[1] - gutter // 2 - 1, xs[2] - gutter // 2 - 1):
        d.line([(gx, y + 2), (gx, 952)], fill=(170, 170, 170), width=1)

    col1 = [
        ("WARSAW, POLAND - WAR",
         "Russian Missiles Land in Poland",
         "Missiles fell on Polish soil during strikes on Ukraine. "
         "NATO called it a violation."),
        ("KYIV, UKRAINE - WAR",
         "Russian Strikes Kill Five in Ukraine",
         "Three died in an apartment block near Kyiv; two in a missile "
         "hit on Zelenskyy's hometown."),
        ("INDONESIA - DISASTER",
         "34 Workers Missing After Factory Fire",
         "The search goes on for 34 workers missing after a candy "
         "factory fire; more remains recovered."),
    ]
    col2 = [
        ("THE HAGUE - JUSTICE",
         "ICJ: Myanmar Committed Genocide",
         "The International Court of Justice ruled Myanmar committed "
         "genocide against the Rohingya."),
        ("NIGERIA - DISASTER",
         "Funeral Boat Capsizes, 24 Dead",
         "A boat carrying mourners to a funeral capsized in Nigeria; "
         "at least 24 people died."),
        ("LONDON & BRUSSELS - POLITICS",
         "Britain and EU Seek Closer Ties",
         "Britain and the EU pursue a major post-Brexit agreement "
         "to draw closer again."),
    ]
    col3 = [
        ("BENGHAZI, LIBYA - WAR",
         "Sea Drones Hit Warship",
         "Ukrainian drones struck a Russian warship at Benghazi base."),
        ("SITRA, BAHRAIN - GULF",
         "Iran Hits Bahrain Plant",
         "Sitra plant attack injures two; tankers hit near Hormuz."),
        ("SINALOA, MEXICO - CRIME",
         "Cartel Leader Captured",
         "'El Chapo Isidro' seized after firefights left 11 dead."),
        ("OKINAWA, JAPAN - CULTURE",
         "Shuri Castle Restored",
         "Okinawa's main hall celebrated, seven years after the fire."),
    ]
    ends = [
        column(d, xs[0], y, col_w, col1, 952),
        column(d, xs[1], y, col_w, col2, 952),
        column(d, xs[2], y, col_w, col3, 952),
    ]

    # ---- footer ---------------------------------------------------------
    fy = 966
    rule(d, fy, width=3)
    rule(d, fy + 5, width=1)
    foot_f = font(SANS, 14)
    foot = "Eleven stories - five continents - one page"
    fw = text_w(d, foot, foot_f)
    d.text(((W - fw) / 2, fy + 14), foot, font=foot_f, fill=GREY)

    out = Path(__file__).resolve().parent / "entry.png"
    img.save(out, format="PNG", optimize=True)
    print(f"wrote {out} ({out.stat().st_size} bytes); column ends: {ends}")


if __name__ == "__main__":
    main()
