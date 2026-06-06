"""Programmatic clock renderer for the Salon clocks experiment.

Renders deterministic analog clocks with known ground-truth times.
Mimics the visual style categories of the Jing Hu benchmark clocks
(not pixel-perfect mimicry — style category match, with our own
ground-truth times we control).

Each public render_clock_NN() function returns the output path and
the ground-truth time as a tuple.
"""
import math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

OUT = Path("rendered")
OUT.mkdir(exist_ok=True)

SIZE = 512  # output square pixel size

# ---------- font helpers ----------
FONTS = {
    "sans": "/System/Library/Fonts/Helvetica.ttc",
    "sans_bold": "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
    "serif_bold": "/System/Library/Fonts/Supplemental/Times New Roman Bold.ttf",
}

def font(kind, px):
    path = FONTS.get(kind, FONTS["sans"])
    try:
        return ImageFont.truetype(path, px)
    except Exception:
        return ImageFont.load_default()

def draw_text_centered(d, x, y, text, fnt, fill):
    bbox = d.textbbox((0, 0), text, font=fnt)
    w = bbox[2] - bbox[0]; h = bbox[3] - bbox[1]
    d.text((x - w / 2 - bbox[0], y - h / 2 - bbox[1]), text, fill=fill, font=fnt)

# ---------- geometry ----------
def angle_for(hour, minute):
    """Return (hour_angle_deg, minute_angle_deg). 0 deg = up, increasing clockwise."""
    minute_angle = minute * 6
    hour_angle = (hour % 12) * 30 + minute * 0.5
    return hour_angle, minute_angle

def polar(cx, cy, angle_deg, radius):
    rad = math.radians(angle_deg - 90)
    return (cx + radius * math.cos(rad), cy + radius * math.sin(rad))

def hand(d, cx, cy, angle_deg, length, base_w, tip_w, fill):
    rad = math.radians(angle_deg - 90)
    dx, dy = math.cos(rad), math.sin(rad)
    px, py = -dy, dx
    tx, ty = cx + length * dx, cy + length * dy
    poly = [
        (cx + base_w/2 * px, cy + base_w/2 * py),
        (tx + tip_w/2 * px, ty + tip_w/2 * py),
        (tx - tip_w/2 * px, ty - tip_w/2 * py),
        (cx - base_w/2 * px, cy - base_w/2 * py),
    ]
    d.polygon(poly, fill=fill)

# ---------- shared face elements ----------
def tick_marks(d, cx, cy, r, hour_color, minute_color, hour_w, minute_w,
               hour_inset=0.86, minute_inset=0.92, outer=0.97):
    for i in range(60):
        angle = i * 6
        is_hour = (i % 5 == 0)
        x1, y1 = polar(cx, cy, angle, r * outer)
        x2, y2 = polar(cx, cy, angle, r * (hour_inset if is_hour else minute_inset))
        d.line([(x1, y1), (x2, y2)],
               fill=hour_color if is_hour else minute_color,
               width=hour_w if is_hour else minute_w)

ROMAN = ["XII","I","II","III","IV","V","VI","VII","VIII","IX","X","XI"]

def numerals_arabic(d, cx, cy, r, color, fnt, mirror=False):
    for h in range(1, 13):
        angle = (h % 12) * 30
        nx, ny = polar(cx, cy, angle, r * 0.78)
        text = str(h)
        if mirror:
            # Mirror by drawing flipped: we render text to a temp image, flip horizontally, paste.
            tmp = Image.new("RGBA", (96, 96), (0,0,0,0))
            td = ImageDraw.Draw(tmp)
            tb = td.textbbox((0,0), text, font=fnt)
            tw, th = tb[2]-tb[0], tb[3]-tb[1]
            td.text(((96-tw)/2 - tb[0], (96-th)/2 - tb[1]), text, fill=color, font=fnt)
            tmp = tmp.transpose(Image.FLIP_LEFT_RIGHT)
            d._image.paste(tmp, (int(nx - 48), int(ny - 48)), tmp)
        else:
            draw_text_centered(d, nx, ny, text, fnt, color)

def numerals_arabic_mirrored_layout(d, cx, cy, r, color, fnt):
    """Numerals arranged counter-clockwise (1 to LEFT of 12) and each glyph mirrored."""
    for h in range(1, 13):
        angle = -(h % 12) * 30  # negative = CCW
        nx, ny = polar(cx, cy, angle, r * 0.78)
        text = str(h)
        tmp = Image.new("RGBA", (120, 120), (0,0,0,0))
        td = ImageDraw.Draw(tmp)
        tb = td.textbbox((0,0), text, font=fnt)
        tw, th = tb[2]-tb[0], tb[3]-tb[1]
        td.text(((120-tw)/2 - tb[0], (120-th)/2 - tb[1]), text, fill=color, font=fnt)
        tmp = tmp.transpose(Image.FLIP_LEFT_RIGHT)
        d._image.paste(tmp, (int(nx - 60), int(ny - 60)), tmp)

def numerals_roman(d, cx, cy, r, color, fnt):
    for i, t in enumerate(ROMAN):
        angle = i * 30
        nx, ny = polar(cx, cy, angle, r * 0.80)
        draw_text_centered(d, nx, ny, t, fnt, color)

def numerals_24hour(d, cx, cy, r, color, fnt_outer, fnt_inner):
    """24-hour clock: inner ring 1-12 standard positions (30° intervals),
    outer ring 24 numerals at 15° intervals with 24 at top going clockwise
    (24, 1, 2, ..., 12 at bottom, ..., 23). Decorative outer; functional
    inner. Hands move on standard 12-hour movement (30°/hour)."""
    for h in range(1, 13):
        angle = (h % 12) * 30
        nx, ny = polar(cx, cy, angle, r * 0.62)
        draw_text_centered(d, nx, ny, str(h), fnt_inner, color)
    for i in range(24):
        # Position 0 = top (24), then go clockwise at 15° per step.
        angle = i * 15
        # i=0 -> "24", i=1 -> "1", ..., i=12 -> "12", i=13 -> "13", ..., i=23 -> "23"
        label = str(24 if i == 0 else i)
        nx, ny = polar(cx, cy, angle, r * 0.87)
        draw_text_centered(d, nx, ny, label, fnt_outer, color)

def date_window(d, cx, cy, w, h, text, fnt, bg=(245,245,245), fg=(20,20,20),
                outline=(60,60,60), outline_w=1):
    d.rectangle([cx - w/2, cy - h/2, cx + w/2, cy + h/2],
                fill=bg, outline=outline, width=outline_w)
    draw_text_centered(d, cx, cy, text, fnt, fg)

def center_pin(d, cx, cy, r, fill):
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=fill)

# ---------- gradient / rainbow faces ----------
def make_gradient_face(size, top_rgb, bottom_rgb):
    """Return an RGBA image with a vertical gradient masked to a circle."""
    im = Image.new("RGBA", (size, size), (0,0,0,0))
    grad = Image.new("RGB", (1, size))
    for y in range(size):
        t = y / (size - 1)
        r = int(top_rgb[0] * (1-t) + bottom_rgb[0] * t)
        g = int(top_rgb[1] * (1-t) + bottom_rgb[1] * t)
        b = int(top_rgb[2] * (1-t) + bottom_rgb[2] * t)
        grad.putpixel((0, y), (r, g, b))
    grad = grad.resize((size, size))
    mask = Image.new("L", (size, size), 0)
    md = ImageDraw.Draw(mask)
    md.ellipse([0, 0, size-1, size-1], fill=255)
    im.paste(grad, (0,0), mask)
    return im

RAINBOW_BANDS = [
    (255, 90, 90),    # red
    (255, 165, 80),   # orange
    (255, 230, 90),   # yellow
    (110, 220, 110),  # green
    (90, 170, 230),   # blue
    (160, 110, 220),  # purple
]

def make_rainbow_face(size):
    """Horizontal bands of rainbow color, masked to circle."""
    im = Image.new("RGBA", (size, size), (0,0,0,0))
    band = Image.new("RGB", (size, size), (255,255,255))
    bd = ImageDraw.Draw(band)
    n = len(RAINBOW_BANDS)
    band_h = size / n
    for i, c in enumerate(RAINBOW_BANDS):
        bd.rectangle([0, int(i*band_h), size, int((i+1)*band_h)], fill=c)
    mask = Image.new("L", (size, size), 0)
    md = ImageDraw.Draw(mask)
    md.ellipse([0, 0, size-1, size-1], fill=255)
    im.paste(band, (0,0), mask)
    return im

# ---------- per-clock renderers ----------
def base_canvas():
    im = Image.new("RGB", (SIZE, SIZE), (255, 255, 255))
    return im, ImageDraw.Draw(im), SIZE/2, SIZE/2

def save(im, name):
    p = OUT / name
    im.save(p, "PNG")
    return p

def render_clock_01_chronograph_arabic(hour=10, minute=10):
    """Arabic numerals 1-12, three subdials, white face."""
    im, d, cx, cy = base_canvas()
    bezel_r = SIZE * 0.49
    face_r = SIZE * 0.46
    d.ellipse([cx-bezel_r, cy-bezel_r, cx+bezel_r, cy+bezel_r], fill=(40,40,40))
    d.ellipse([cx-face_r, cy-face_r, cx+face_r, cy+face_r], fill=(252,252,252))
    tick_marks(d, cx, cy, face_r, (30,30,30), (120,120,120),
               hour_w=4, minute_w=2)
    numerals_arabic(d, cx, cy, face_r, (20,20,20),
                    font("sans_bold", int(SIZE*0.050)))
    # Three subdials at 10, 2, 7 o'clock positions
    sub_r = face_r * 0.20
    for sub_angle in [300, 60, 210]:  # 10, 2, 7 o'clock
        sx, sy = polar(cx, cy, sub_angle, face_r * 0.45)
        d.ellipse([sx-sub_r, sy-sub_r, sx+sub_r, sy+sub_r],
                  outline=(60,60,60), width=2, fill=(252,252,252))
        # tiny tick marks on subdial
        for i in range(12):
            a = i * 30
            x1, y1 = polar(sx, sy, a, sub_r * 0.95)
            x2, y2 = polar(sx, sy, a, sub_r * 0.78)
            d.line([(x1,y1),(x2,y2)], fill=(60,60,60), width=1)
        # tiny hand on subdial pointing somewhere fixed
        hand(d, sx, sy, 60, sub_r * 0.7, 2, 1, (40,40,40))
        center_pin(d, sx, sy, 2, (40,40,40))
    # Main hands
    ha, ma = angle_for(hour, minute)
    hand(d, cx, cy, ha, face_r * 0.50, 8, 4, (20,20,20))
    hand(d, cx, cy, ma, face_r * 0.78, 6, 3, (20,20,20))
    center_pin(d, cx, cy, 6, (20,20,20))
    return save(im, "clock_01.png"), (hour, minute)

def render_clock_02_roman_date(hour=3, minute=25):
    """Roman numerals with small Tue date window at 3 o'clock."""
    im, d, cx, cy = base_canvas()
    bezel_r = SIZE * 0.49
    face_r = SIZE * 0.46
    d.ellipse([cx-bezel_r, cy-bezel_r, cx+bezel_r, cy+bezel_r], fill=(40,40,40))
    d.ellipse([cx-face_r, cy-face_r, cx+face_r, cy+face_r], fill=(252,252,252))
    tick_marks(d, cx, cy, face_r, (30,30,30), (120,120,120),
               hour_w=4, minute_w=2)
    numerals_roman(d, cx, cy, face_r, (20,20,20),
                   font("serif_bold", int(SIZE*0.06)))
    # Date window at 3 o'clock
    win_cx, win_cy = polar(cx, cy, 90, face_r * 0.55)
    date_window(d, win_cx, win_cy, SIZE*0.10, SIZE*0.06, "MON",
                font("sans_bold", int(SIZE*0.035)),
                bg=(220,40,40), fg=(255,255,255), outline=(120,20,20))
    ha, ma = angle_for(hour, minute)
    hand(d, cx, cy, ha, face_r * 0.55, 9, 5, (20,20,20))
    hand(d, cx, cy, ma, face_r * 0.78, 7, 3, (20,20,20))
    center_pin(d, cx, cy, 6, (20,20,20))
    return save(im, "clock_02.png"), (hour, minute)

def render_clock_03_24hour(hour=7, minute=50):
    """24-hour clock: outer ring of 24 Arabic numerals at 15° intervals,
    inner ring of 12 numerals at 30°. Short ticks at outer edge only,
    so outer numerals have a clean band."""
    im, d, cx, cy = base_canvas()
    bezel_r = SIZE * 0.49
    face_r = SIZE * 0.46
    d.ellipse([cx-bezel_r, cy-bezel_r, cx+bezel_r, cy+bezel_r], fill=(40,40,40))
    d.ellipse([cx-face_r, cy-face_r, cx+face_r, cy+face_r], fill=(252,252,252))
    # Short ticks at outer edge only — leaves clean radial band for outer numerals
    tick_marks(d, cx, cy, face_r, (30,30,30), (160,160,160),
               hour_w=3, minute_w=1,
               hour_inset=0.94, minute_inset=0.96, outer=0.99)
    numerals_24hour(d, cx, cy, face_r, (20,20,20),
                    font("sans_bold", int(SIZE*0.030)),
                    font("sans", int(SIZE*0.030)))
    ha, ma = angle_for(hour, minute)
    hand(d, cx, cy, ha, face_r * 0.42, 7, 4, (20,20,20))
    hand(d, cx, cy, ma, face_r * 0.55, 5, 2, (20,20,20))
    center_pin(d, cx, cy, 5, (20,20,20))
    return save(im, "clock_03.png"), (hour, minute)

def render_clock_04_naked_hands(hour=8, minute=20):
    """Just two hands floating on white. No face, no border, no markers.
    Hands sized to match the implied clock face of the other 7 (face_r = 0.46*SIZE),
    so the stimulus has the same visible scale as the rest of the set.
    """
    im, d, cx, cy = base_canvas()
    implied_r = SIZE * 0.46  # match other clocks' face radius
    ha, ma = angle_for(hour, minute)
    hand(d, cx, cy, ha, implied_r * 0.55, 8, 4, (60,60,60))
    hand(d, cx, cy, ma, implied_r * 0.80, 6, 3, (60,60,60))
    center_pin(d, cx, cy, 5, (60,60,60))
    return save(im, "clock_04.png"), (hour, minute)

def render_clock_05_gradient(hour=4, minute=15):
    """Vertical red->blue gradient, Arabic numerals, day+date windows."""
    im, d, cx, cy = base_canvas()
    bezel_r = SIZE * 0.49
    face_r = SIZE * 0.46
    grad = make_gradient_face(int(face_r*2), (200, 20, 60), (40, 80, 200))
    d.ellipse([cx-bezel_r, cy-bezel_r, cx+bezel_r, cy+bezel_r], fill=(20,20,20))
    im.paste(grad, (int(cx-face_r), int(cy-face_r)), grad)
    d2 = ImageDraw.Draw(im)
    tick_marks(d2, cx, cy, face_r, (255,255,255), (255,255,255),
               hour_w=3, minute_w=1)
    numerals_arabic(d2, cx, cy, face_r, (255,255,255),
                    font("sans_bold", int(SIZE*0.06)))
    # Three-cell day/date strip in horizontal row at 4-5 o'clock area,
    # matching source format: DAY | DATE | MONTH
    strip_center_x, strip_center_y = polar(cx, cy, 130, face_r * 0.55)
    cell_w = SIZE * 0.075
    cell_h = SIZE * 0.045
    cell_gap = SIZE * 0.005
    fnt = font("sans_bold", int(SIZE * 0.024))
    cells = [("MON", -1), ("03", 0), ("MAY", 1)]
    for text, offset in cells:
        wx = strip_center_x + offset * (cell_w + cell_gap)
        date_window(d2, wx, strip_center_y, cell_w, cell_h, text, fnt,
                    bg=(245,245,245), fg=(20,20,20), outline=(60,60,60))
    ha, ma = angle_for(hour, minute)
    hand(d2, cx, cy, ha, face_r * 0.55, 9, 5, (245,245,245))
    hand(d2, cx, cy, ma, face_r * 0.80, 6, 3, (245,245,245))
    center_pin(d2, cx, cy, 6, (245,245,245))
    return save(im, "clock_05.png"), (hour, minute)

def render_clock_06_rainbow_no_numerals(hour=6, minute=30):
    """Rainbow horizontal bands, no numerals at all, day+date windows."""
    im, d, cx, cy = base_canvas()
    bezel_r = SIZE * 0.49
    face_r = SIZE * 0.46
    rainbow = make_rainbow_face(int(face_r*2))
    d.ellipse([cx-bezel_r, cy-bezel_r, cx+bezel_r, cy+bezel_r], fill=(60,60,60))
    im.paste(rainbow, (int(cx-face_r), int(cy-face_r)), rainbow)
    d2 = ImageDraw.Draw(im)
    # subtle tick marks only at hours
    for i in range(60):
        if i % 5 == 0:
            angle = i * 6
            x1, y1 = polar(cx, cy, angle, face_r * 0.97)
            x2, y2 = polar(cx, cy, angle, face_r * 0.88)
            d2.line([(x1,y1),(x2,y2)], fill=(60,60,60), width=3)
        else:
            angle = i * 6
            x1, y1 = polar(cx, cy, angle, face_r * 0.97)
            x2, y2 = polar(cx, cy, angle, face_r * 0.93)
            d2.line([(x1,y1),(x2,y2)], fill=(80,80,80), width=1)
    # day+date windows in middle
    win_cy = cy + face_r * 0.12
    date_window(d2, cx - SIZE*0.06, win_cy, SIZE*0.07, SIZE*0.045, "MON",
                font("sans_bold", int(SIZE*0.025)))
    date_window(d2, cx + SIZE*0.025, win_cy, SIZE*0.05, SIZE*0.045, "03",
                font("sans_bold", int(SIZE*0.025)))
    date_window(d2, cx + SIZE*0.09, win_cy, SIZE*0.06, SIZE*0.045, "MAY",
                font("sans_bold", int(SIZE*0.025)))
    ha, ma = angle_for(hour, minute)
    hand(d2, cx, cy, ha, face_r * 0.55, 9, 5, (255,255,255))
    hand(d2, cx, cy, ma, face_r * 0.80, 6, 3, (255,255,255))
    center_pin(d2, cx, cy, 6, (60,60,60))
    return save(im, "clock_06.png"), (hour, minute)

def render_clock_07_dark_simple(hour=11, minute=55):
    """Dark face, slim white hands, small date window below center."""
    im, d, cx, cy = base_canvas()
    bezel_r = SIZE * 0.49
    face_r = SIZE * 0.46
    d.ellipse([cx-bezel_r, cy-bezel_r, cx+bezel_r, cy+bezel_r], fill=(20,20,20))
    d.ellipse([cx-face_r, cy-face_r, cx+face_r, cy+face_r], fill=(15,15,15))
    # sparse tick marks only at hours
    for i in range(60):
        if i % 5 == 0:
            angle = i * 6
            x1, y1 = polar(cx, cy, angle, face_r * 0.97)
            x2, y2 = polar(cx, cy, angle, face_r * 0.86)
            d.line([(x1,y1),(x2,y2)], fill=(240,240,240), width=3)
    # Three-cell day/date strip horizontal, just below center
    strip_cy = cy + face_r * 0.18
    cell_w = SIZE * 0.06
    cell_h = SIZE * 0.038
    cell_gap = SIZE * 0.004
    fnt = font("sans_bold", int(SIZE * 0.020))
    cells = [("MON", -1), ("03", 0), ("MAY", 1)]
    for text, offset in cells:
        wx = cx + offset * (cell_w + cell_gap)
        date_window(d, wx, strip_cy, cell_w, cell_h, text, fnt,
                    bg=(245,245,245), fg=(20,20,20), outline=(120,120,120))
    ha, ma = angle_for(hour, minute)
    hand(d, cx, cy, ha, face_r * 0.55, 6, 3, (245,245,245))
    hand(d, cx, cy, ma, face_r * 0.80, 5, 2, (245,245,245))
    center_pin(d, cx, cy, 4, (245,245,245))
    return save(im, "clock_07.png"), (hour, minute)

def render_clock_08_mirrored(hour=9, minute=45):
    """Dark face with numerals arranged counter-clockwise AND mirrored."""
    im, d, cx, cy = base_canvas()
    bezel_r = SIZE * 0.49
    face_r = SIZE * 0.46
    d.ellipse([cx-bezel_r, cy-bezel_r, cx+bezel_r, cy+bezel_r], fill=(20,20,20))
    d.ellipse([cx-face_r, cy-face_r, cx+face_r, cy+face_r], fill=(15,15,15))
    # tick marks (regular)
    tick_marks(d, cx, cy, face_r, (240,240,240), (140,140,140),
               hour_w=3, minute_w=1)
    numerals_arabic_mirrored_layout(d, cx, cy, face_r, (245,245,245),
                                    font("sans_bold", int(SIZE*0.07)))
    # Date window left of center, with text MIRRORED to match the rest
    # of the clock face. "MON" displayed as horizontally-flipped glyphs.
    win_cx, win_cy = cx - face_r * 0.30, cy
    win_w, win_h = SIZE*0.10, SIZE*0.05
    d.rectangle([win_cx-win_w/2, win_cy-win_h/2, win_cx+win_w/2, win_cy+win_h/2],
                fill=(245,245,245), outline=(60,60,60), width=1)
    fnt_date = font("sans_bold", int(SIZE*0.030))
    tmp = Image.new("RGBA", (160, 80), (0,0,0,0))
    td = ImageDraw.Draw(tmp)
    tb = td.textbbox((0,0), "MON", font=fnt_date)
    tw, th = tb[2]-tb[0], tb[3]-tb[1]
    td.text(((160-tw)/2 - tb[0], (80-th)/2 - tb[1]), "MON", fill=(20,20,20), font=fnt_date)
    tmp = tmp.transpose(Image.FLIP_LEFT_RIGHT)
    im.paste(tmp, (int(win_cx - 80), int(win_cy - 40)), tmp)
    # Mirrored hand positions: a mirror clock at 9:45 displays hands as if
    # the clock were rotated. We render using normal angles so the visual
    # ground truth matches the displayed numerals.
    ha, ma = angle_for(hour, minute)
    # Mirror the angles horizontally: angle' = -angle
    hand(d, cx, cy, -ha, face_r * 0.55, 8, 4, (245,245,245))
    hand(d, cx, cy, -ma, face_r * 0.80, 6, 3, (245,245,245))
    center_pin(d, cx, cy, 5, (245,245,245))
    return save(im, "clock_08.png"), (hour, minute)


if __name__ == "__main__":
    results = [
        render_clock_01_chronograph_arabic(10, 10),
        render_clock_02_roman_date(3, 25),
        render_clock_03_24hour(7, 50),
        render_clock_04_naked_hands(8, 20),
        render_clock_05_gradient(4, 15),
        render_clock_06_rainbow_no_numerals(6, 30),
        render_clock_07_dark_simple(11, 55),
        render_clock_08_mirrored(9, 45),
    ]
    print("RENDERED CLOCKS — ground truth times:")
    for path, (h, m) in results:
        print(f"  {path.name}: {h:02d}:{m:02d}")
