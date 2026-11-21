#!/usr/bin/env python3
"""news-image-20261120 — draw.py (build-time authoring tool).
Draws ONE newspaper front page (1024x1024 PNG) summing up Friday 20 Nov 2026.
Deterministic: no timestamps, no unseeded randomness.
main.ts (copy-only) ships entry.png; draw.py never runs in the grader.
All facts from news-image-20261120-research.md only.
"""
import math
import os
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")

# ---------------- palette ----------------
PAPER = (247, 243, 234)
INK = (26, 26, 26)
NAVY = (31, 42, 68)
NAVY_LT = (43, 58, 92)
RED = (180, 35, 24)
RED_DK = (140, 25, 16)
GREEN = (30, 107, 58)
TEAL = (31, 138, 138)
ORANGE = (217, 123, 41)
PURPLE = (123, 75, 168)
BLUE = (43, 94, 167)
AFRICA = (46, 125, 79)
GREY = (102, 102, 102)
SEA = (214, 228, 236)
LAND = (232, 220, 192)
LAND_LINE = (190, 175, 140)
HAIR = (200, 192, 172)
WHITE = (255, 255, 255)

REGION = {
    "EUROPE": BLUE, "MIDDLE EAST": ORANGE, "ASIA": PURPLE,
    "AFRICA": AFRICA, "AMERICAS": RED, "OCEANIA": TEAL, "GLOBAL": GREY,
}
TAG_COLOR = {"CONFIRMED": GREEN, "REPORTED": NAVY, "CLAIM": RED, "FORECAST": ORANGE}

# ---------------- fonts ----------------
BASE = os.path.dirname(os.path.abspath(__file__))
PF = os.path.join(BASE, "fonts", "PlayfairDisplay.ttf")
DJ = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
DJB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
DJSB = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"


def _pf(size, name=b"ExtraBold"):
    f = ImageFont.truetype(PF, size)
    try:
        f.set_variation_by_name(name)
    except Exception:
        pass
    return f


def _dj(size, bold=False):
    return ImageFont.truetype(DJB if bold else DJ, size)


F_MAST = _pf(50, b"ExtraBold")
F_LEAD_H = _pf(20, b"Bold")
F_CARD_H = _pf(15, b"Bold")
F_KICK = _dj(11, True)
F_DECK = _dj(11)
F_BRIEF = _dj(12)
F_BRIEF_B = _dj(12, True)
F_NUM = _dj(13, True)
F_SMALL = _dj(10)
F_SMALL_B = _dj(10, True)
F_TINY = _dj(9)
F_TINY_B = _dj(9, True)
F_TL = _dj(8)
F_TL_TIME = _dj(13, True)
F_STAT_N = _dj(16, True)
F_STAT_L = _dj(9, True)
F_LABEL = _dj(11, True)
F_CHIP = _dj(11, True)
F_BANNER = _dj(10, True)
F_LOC = _dj(9, True)
F_SRC = _dj(9)
F_FOOT = _dj(8)
F_SUB = _dj(12)
F_SUB_I = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf", 12)

# ---------------- geometry ----------------
MX = 24
CW = 976
RIGHT = 1000

# ---------------- continent polygons (lon, lat) — reference data ----------------
POLYS = [
    [(-9, 37), (-9, 43), (-2, 44), (-1, 46), (-4, 48), (-2, 50), (1, 51), (4, 53), (8, 54), (8, 57), (10, 58), (7, 60), (5, 62), (10, 64), (14, 67), (19, 69), (24, 71), (30, 70), (35, 68), (42, 68), (48, 68), (54, 68), (60, 69), (66, 69), (72, 72), (78, 72), (85, 73), (95, 75), (105, 77), (112, 74), (120, 73), (128, 71), (138, 72), (148, 72), (158, 70), (162, 66), (170, 66), (178, 65), (178, 62), (170, 60), (162, 59), (158, 52), (156, 51), (150, 59), (142, 59), (141, 52), (140, 47), (138, 43), (135, 43), (132, 43), (130, 42), (127, 40), (126, 38), (124, 40), (121, 37), (120, 32), (122, 30), (120, 25), (117, 23), (112, 22), (108, 18), (106, 11), (105, 9), (103, 7), (100, 6), (98, 10), (97, 15), (94, 16), (92, 21), (90, 22), (88, 22), (86, 20), (83, 18), (80, 15), (80, 10), (77, 8), (75, 10), (73, 16), (70, 20), (68, 23), (66, 25), (62, 25), (58, 25), (56, 26), (52, 26), (50, 29), (48, 30), (45, 29), (43, 28), (41, 27), (39, 21), (38, 18), (35, 28), (34, 28), (33, 29), (32, 31), (30, 31), (27, 37), (26, 38), (23, 36), (22, 37), (20, 39), (19, 42), (16, 40), (14, 38), (12, 38), (10, 37), (8, 37), (8, 39), (4, 39), (2, 41), (0, 38), (-2, 37), (-6, 36)],
    [(-168, 66), (-165, 60), (-158, 58), (-152, 60), (-140, 60), (-135, 58), (-130, 54), (-125, 49), (-124, 42), (-120, 34), (-114, 29), (-110, 24), (-105, 20), (-97, 16), (-94, 17), (-90, 14), (-86, 12), (-83, 9), (-80, 8), (-77, 7), (-79, 9), (-81, 13), (-84, 16), (-87, 13), (-88, 18), (-90, 21), (-91, 19), (-96, 19), (-97, 22), (-97, 26), (-93, 30), (-89, 30), (-84, 30), (-81, 26), (-80, 32), (-76, 35), (-74, 40), (-70, 42), (-68, 45), (-65, 44), (-60, 47), (-55, 47), (-60, 52), (-65, 50), (-60, 55), (-65, 60), (-68, 58), (-75, 62), (-78, 62), (-85, 66), (-90, 66), (-95, 69), (-110, 68), (-125, 70), (-140, 70), (-155, 71), (-165, 68)],
    [(-80, 9), (-77, 4), (-75, 0), (-80, -3), (-81, -6), (-77, -12), (-72, -18), (-70, -23), (-70, -30), (-72, -37), (-73, -44), (-74, -50), (-70, -54), (-66, -55), (-65, -45), (-62, -41), (-58, -35), (-52, -32), (-48, -28), (-41, -23), (-39, -17), (-35, -9), (-35, -6), (-40, -3), (-44, -2), (-50, 0), (-52, 5), (-55, 6), (-60, 8), (-62, 9), (-68, 11), (-72, 12), (-75, 11), (-77, 8)],
    [(-17, 15), (-17, 21), (-15, 27), (-10, 31), (-5, 35), (0, 36), (10, 37), (11, 34), (20, 32), (25, 32), (30, 31), (33, 27), (35, 23), (37, 18), (39, 15), (43, 12), (48, 11), (51, 12), (46, 5), (42, 0), (40, -5), (40, -10), (37, -15), (35, -20), (32, -26), (28, -33), (20, -35), (17, -32), (15, -27), (13, -18), (12, -10), (13, -5), (9, 4), (6, 4), (-2, 5), (-8, 5), (-13, 8), (-17, 12)],
    [(113, -22), (114, -30), (115, -35), (118, -35), (124, -33), (129, -32), (132, -32), (135, -35), (138, -35), (140, -38), (145, -38), (150, -37), (153, -32), (153, -27), (150, -22), (146, -19), (142, -15), (142, -11), (140, -17), (136, -15), (135, -12), (132, -11), (130, -13), (126, -14), (122, -17), (118, -20), (114, -22)],
    [(-45, 60), (-40, 64), (-32, 68), (-25, 70), (-20, 74), (-25, 76), (-35, 77), (-50, 76), (-58, 74), (-55, 70), (-52, 64), (-48, 60)],
    [(-5, 50), (-3, 53), (-5, 56), (-3, 58), (-1, 57), (0, 53), (1, 51)],
    [(130, 31), (132, 33), (134, 34), (136, 35), (138, 35), (140, 37), (141, 39), (141, 41), (142, 43), (144, 44), (141, 45), (139, 41), (137, 38), (135, 34), (133, 34), (130, 33)],
    [(44, -16), (47, -15), (50, -16), (50, -20), (47, -24), (44, -25), (43, -21), (44, -17)],
    [(167, -45), (170, -43), (173, -41), (175, -38), (177, -38), (174, -36), (172, -35), (167, -45)],
]

# ---------------- text helpers ----------------
def tw(font, s):
    return font.getlength(s)


def fit_lines(text, font, max_w, max_lines):
    """Greedy wrap; returns list of lines (<= max_lines). Asserts no overflow."""
    words = text.split()
    lines, cur = [], ""
    for wd in words:
        trial = (cur + " " + wd).strip()
        if tw(font, trial) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = wd
    if cur:
        lines.append(cur)
    assert len(lines) <= max_lines, f"WRAP OVERFLOW ({len(lines)}>{max_lines}): {text!r}"
    for ln in lines:
        assert tw(font, ln) <= max_w, f"LINE TOO WIDE: {ln!r}"
    return lines


def draw_lines(d, lines, x, y, font, fill, leading):
    for ln in lines:
        d.text((x, y), ln, font=font, fill=fill)
        y += leading
    return y


def chip(d, x, y, text, fill, font=F_CHIP, fg=WHITE, pad_x=7, h=18):
    w = int(tw(font, text)) + pad_x * 2
    d.rounded_rectangle([x, y, x + w, y + h], radius=4, fill=fill)
    d.text((x + pad_x, y + 3), text, font=font, fill=fg)
    return w


def label_in_box(d, text, box_x, box_y, box_w, font, fill, bg=None):
    """One-line label; assert it fits the box."""
    assert tw(font, text) <= box_w, f"LABEL OVERFLOW {text!r} {tw(font, text):.0f}>{box_w}"
    if bg is not None:
        d.rectangle([box_x, box_y, box_x + box_w, box_y + 16], fill=bg)
    d.text((box_x, box_y + 2), text, font=font, fill=fill)


def flag(d, x, y, w, h, stripes):
    """Simple horizontal-stripe flag; stripes = list of colors top->bottom."""
    n = len(stripes)
    for i, c in enumerate(stripes):
        d.rectangle([x, y + i * h / n, x + w, y + (i + 1) * h / n], fill=c)
    d.rectangle([x, y, x + w, y + h], outline=INK, width=1)


def person(d, cx, base_y, h, suit, skin=(232, 190, 150), hair=(40, 40, 40)):
    """Minimal flat person: head + shoulders, standing on base_y."""
    r = h * 0.16
    d.ellipse([cx - r, base_y - h, cx + r, base_y - h + 2 * r], fill=skin)
    d.pieslice([cx - r, base_y - h, cx + r, base_y - h + 2 * r], 180, 360, fill=hair)
    d.polygon([(cx - h * 0.30, base_y), (cx + h * 0.30, base_y),
               (cx + h * 0.20, base_y - h * 0.42), (cx - h * 0.20, base_y - h * 0.42)], fill=suit)
    d.polygon([(cx - h * 0.07, base_y - h * 0.42), (cx + h * 0.07, base_y - h * 0.42),
               (cx, base_y - h * 0.18)], fill=WHITE)


def spiral(d, cx, cy, r_max, color, width=3):
    """Cyclone spiral: archimedean, drawn as polyline."""
    pts = []
    for t in range(0, 620, 8):
        a = math.radians(t)
        r = r_max * t / 620.0
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    d.line(pts, fill=color, width=width, joint="curve")

# ================= CONTENT (40 stories; all figures verified in research.md) =================
# Canonical numbers (identical everywhere on the page):
#   515 = 27 ballistic + 84 cruise + 404 drones | 300,000 evacuated (Akvan)
#   100,000 youth visas / year PER SIDE | KOSPI -5,2% | $41,7bn ICE & CBP
#   2 Russian missiles fell in Poland (+ 1 Geran-5 drone) | at least 8 killed

STATS = [
    ("515", "RUSSIAN MISSILES & DRONES"),
    ("300,000", "EVACUATED AHEAD OF AKVAN"),
    ("100,000", "YOUTH VISAS A YEAR, PER SIDE"),
    ("\u22125,2%", "KOSPI PLUNGE"),
    ("$41,7bn", "ICE & CBP CONTRACTS"),
    ("2", "MISSILES THAT FELL IN POLAND"),
]

LEADS = [
    {
        "num": 1, "region": "EUROPE",
        "kicker": "1 \u00b7 KYIV \u2014 AND POLAND",
        "headline": "Russia's biggest barrage hits Kyiv \u2014 and falls on Poland",
        "deck": "515 weapons overnight; 3 bridges hit, power out in 11 regions; 2 missiles and a drone fall in Poland.",
        "banner": "KYIV \u00b7 515 WEAPONS \u00b7 POLAND",
        "bg": (222, 228, 238),
    },
    {
        "num": 2, "region": "GLOBAL",
        "kicker": "2 \u00b7 ANTALYA \u2014 COP31",
        "headline": "COP31 misses its deadline \u2014 no deal on fossil fuels",
        "deck": "Closing plenary suspended at 10:29 pm in Antalya; fossil-fuel deal dead, Ethiopia named COP32 host.",
        "banner": "ANTALYA \u00b7 NO DEAL \u00b7 OVERTIME",
        "bg": (226, 232, 222),
    },
    {
        "num": 3, "region": "EUROPE",
        "kicker": "3 \u00b7 BRUSSELS \u2014 EU\u2013UK",
        "headline": "UK and EU strike a post-Brexit reset",
        "deck": "Burnham, von der Leyen and Costa agree food, carbon and youth deals \u2014 the biggest EU step since Brexit.",
        "banner": "BRUSSELS \u00b7 FOOD \u00b7 CARBON \u00b7 YOUTH",
        "bg": (232, 226, 210),
    },
]

# cards: headline (<=2 lines at 15pt Playfair), deck (<=2 lines at 11pt),
# chip (data), loc bar, source, tag
CARDS = [
    {"headline": "Cyclone Akvan makes landfall",
     "deck": "Gopalpur; winds 70\u201380 kmph; 300,000+ evacuated.",
     "chip": "300,000", "chip_fill": RED,
     "loc": "ODISHA \u00b7 INDIA", "src": "IMD", "tag": "CONFIRMED", "scene": "akvan"},
    {"headline": "Asian markets rout: KOSPI \u22125,2%",
     "deck": "Nikkei \u22125,1%; TAIEX \u22126,2%; a 10-month low.",
     "chip": "\u22125,2%", "chip_fill": RED,
     "loc": "SEOUL \u00b7 TOKYO", "src": "Econplex", "tag": "CONFIRMED", "scene": "markets"},
    {"headline": "Haiti police kill 34 in Martissant raid",
     "deck": "Operation Thu, reported Fri; police say 34 killed.",
     "chip": "34", "chip_fill": RED,
     "loc": "PORT-AU-PRINCE \u00b7 HAITI", "src": "AP", "tag": "REPORTED", "scene": "haiti"},
    {"headline": "ICE and CBP award $41,7bn contracts",
     "deck": "Deportation contracts top $41,7bn a year.",
     "chip": "$41,7BN", "chip_fill": NAVY,
     "loc": "WASHINGTON \u00b7 USA", "src": "All Voices", "tag": "REPORTED", "scene": "ice"},
    {"headline": "Merz rejects a new Yalta over Europe",
     "deck": "No deal on Europe without Europe at the table.",
     "chip": "NO YALTA", "chip_fill": NAVY,
     "loc": "BERLIN \u00b7 GERMANY", "src": "Open Chronicle", "tag": "REPORTED", "scene": "merz"},
    {"headline": "Funeral boat capsizes in Nigeria",
     "deck": "300+ aboard; police confirm 4 dead, 24 rescued.",
     "chip": "4 DEAD", "chip_fill": RED,
     "loc": "BAYELSA \u00b7 NIGERIA", "src": "Press Pass USA", "tag": "REPORTED", "scene": "boat"},
    {"headline": "Xi meets Albanese: \u201cturnaround\u201d",
     "deck": "Xi: ties in a \u201ccomprehensive turnaround\u201d.",
     "chip": "SHENZHEN", "chip_fill": TEAL,
     "loc": "SHENZHEN \u00b7 CHINA", "src": "Xinhua", "tag": "REPORTED", "scene": "xi"},
    {"headline": "Saudi downs Houthi missiles; hits Yemen",
     "deck": "Saudi says defences down missiles; Yemen struck.",
     "chip": "SAUDI SAYS", "chip_fill": RED,
     "loc": "RIYADH \u00b7 SAUDI ARABIA", "src": "EA WorldView", "tag": "REPORTED", "scene": "saudi"},
    {"headline": "Israeli strikes kill 6 in Gaza",
     "deck": "Tanks cross \u201cyellow line\u201d in first ground move.",
     "chip": "6 KILLED", "chip_fill": RED,
     "loc": "GAZA", "src": "AFP", "tag": "REPORTED", "scene": "gaza"},
    {"headline": "Global stocks slide for a 7th day",
     "deck": "AI selloff deepens; Asia and Europe down on Friday.",
     "chip": "DAY 7", "chip_fill": RED,
     "loc": "LONDON \u00b7 GLOBAL", "src": "Virginia Times", "tag": "REPORTED", "scene": "global"},
]

# briefs 14-40: (number, region, prefix, text) — one line each
BRIEFS = [
    (14, "ASIA", "MYANMAR", "Calls ICJ ruling \u201cunfair\u201d (9\u20136 vote)"),
    (15, "ASIA", "S. KOREA", "Exports pass $1 trillion, a first"),
    (16, "ASIA", "CHINA", "Urges Japan to retract Taiwan remarks"),
    (17, "ASIA", "SINGAPORE", "Pledges closer ties with China"),
    (18, "ASIA", "JAPAN", "Inflation 2,2%; BOJ hike bets grow"),
    (19, "ASIA", "S. KOREA", "Producer prices fall in October"),
    (20, "AMERICAS", "CONGRESS", "Shutdown risk over Iran war funding"),
    (21, "AMERICAS", "TREASURY", "Sanctions four over Iranian oil"),
    (22, "AMERICAS", "WHITE HOUSE", "Says Asia trip secured $17bn+"),
    (23, "AMERICAS", "JUDGE", "To block Trump\u2019s 250-foot arch"),
    (24, "AMERICAS", "SHEINBAUM", "21-hour economy flight goes viral"),
    (25, "EUROPE", "KRYVYI RIH", "Double-tap kills boy, 7, paramedic"),
    (26, "EUROPE", "UKRAINE", "Deploys experimental laser defence"),
    (27, "EUROPE", "UKRAINE", "Hits Druzhba pipeline in Tatarstan"),
    (28, "EUROPE", "POLAND", "Seeks NATO jets after airspace breach"),
    (29, "EUROPE", "MOLDOVA", "Two Russian drones violate airspace"),
    (30, "AFRICA", "ETHIOPIA", "To host COP32 in 2027, Addis Ababa"),
    (31, "AFRICA", "SUDAN", "Drones killed 1,600+ this year, UN says"),
    (32, "AFRICA", "CONGO", "Offensive displaces 323,000, UN says"),
    (33, "OCEANIA", "APEC", "Australia, Canada, NZ urge ceasefire"),
    (34, "OCEANIA", "AUSTRALIA", "Travel declaration pilot to Adelaide"),
    (35, "OCEANIA", "ONE NZ", "First 5G standalone test call"),
    (36, "MIDDLE EAST", "IRAN", "14 tankers staged, Hamshahri claims"),
    (37, "MIDDLE EAST", "IRAN", "Claims it shot down a US MQ-9 drone"),
    (38, "MIDDLE EAST", "IRAQ", "Forces enter Jurf al Sakhr"),
    (39, "GLOBAL", "STUDY", "Muslims to outnumber Christians by 2035"),
    (40, "GLOBAL", "CO2", "Record 38,1bn tonnes projected"),
]

TIMELINE = [
    ("Overnight", "Russia\u2019s 515-weapon barrage; Poland hit"),
    ("~02:30 UTC", "Akvan makes landfall, Gopalpur"),
    ("~07:00 UTC", "Asian markets plunge: KOSPI \u22125,2%"),
    ("Midday", "EU\u2013UK summit under way, Brussels"),
    ("~17:00 UTC", "EU\u2013UK seal three deals"),
    ("~19:30 UTC", "COP31 plenary suspended, Antalya"),
    ("Evening", "Double-tap strike hits Kryvyi Rih"),
]

DATE_OUT = ("Shenzhen trilateral \u00b7 Thu 19 Nov; ICJ Myanmar ruling (9\u20136) \u00b7 Thu 19 Nov; "
            "Anthropic IPO \u00b7 Thu 19 Nov; COP31 draft drops fossil fuels + $120bn \u00b7 Thu 19 Nov; "
            "Kerch Bridge strike \u00b7 Thu 19 Nov; Denmark backs US Arctic pact 109\u20130 \u00b7 Thu 19 Nov; "
            "Voyager 1 one light-day \u00b7 Wed 18 Nov; EU \u20ac45bn Ukraine loan \u00b7 Wed 18 Nov; "
            "GTA VI launch \u00b7 Thu 19 Nov; PFI Tower Riyadh damage \u00b7 Thu 19 Nov; "
            "Dow \u22121,101 \u00b7 Thu 19 Nov")
DATE_NOTYET = ("COP31 third draft + resumed talks \u00b7 Sat 21 Nov; COP31 close due Sat 21 Nov")

REGION_COUNTS = [("ASIA", 8), ("AMERICAS", 7), ("EUROPE", 8), ("AFRICA", 4),
                 ("OCEANIA", 4), ("MIDDLE EAST", 5), ("GLOBAL", 4)]

# map pins: (number, lon, lat, dx, dy) — dx/dy = manual offset in px when crowded
PINS = [
    (1, 30.5, 50.4, 8, -12),     # Kyiv (lead 1, fanned up from Berlin)
    (2, 30.7, 36.9, -16, 6),     # Antalya (lead 2, fanned from Gaza/Berlin)
    (3, 4.35, 50.85, -12, -10),  # Brussels (lead 3, fanned from Berlin)
    (4, 85.0, 19.3, 0, 0),       # Gopalpur (Akvan)
    (5, 127.0, 37.5, 0, 0),      # Seoul (markets)
    (6, -72.3, 18.5, 0, 0),      # Port-au-Prince (Haiti)
    (7, -77.0, 38.9, 0, 0),      # Washington (ICE/CBP)
    (8, 13.4, 52.5, -6, 10),     # Berlin (Merz, fanned down from Kyiv)
    (9, 6.3, 4.8, 0, 0),         # Bayelsa (Nigeria boat)
    (10, 114.1, 22.5, 0, 0),     # Shenzhen (Xi-Albanese)
    (11, 46.7, 24.6, 12, -10),   # Riyadh (Saudi, fanned from Gaza)
    (12, 34.5, 31.5, -2, 12),    # Gaza (fanned from Antalya)
    (13, -0.1, 51.5, -14, 10),   # London (global stocks, fanned from Brussels)
]

# map dots for briefs: (lon, lat, region, dx, dy)
DOTS = [
    (96.2, 16.8, "ASIA", -12, 10),   # 14 Myanmar (Yangon, fanned from Gopalpur pin)
    (127.0, 37.5, "ASIA", 8, 8),     # 15 S. Korea exports (Seoul, offset)
    (139.7, 35.7, "ASIA", 0, 0),     # 16 Tokyo
    (103.8, 1.35, "ASIA", 0, 0),     # 17 Singapore
    (139.7, 35.7, "ASIA", 8, -8),    # 18 Japan inflation (Tokyo, offset)
    (127.0, 37.5, "ASIA", -8, -8),   # 19 S. Korea producer prices (Seoul, offset)
    (-77.0, 38.9, "AMERICAS", 8, -8),  # 20 Congress (DC, offset)
    (-77.0, 38.9, "AMERICAS", -8, 8),  # 21 Treasury (DC, offset)
    (-77.0, 38.9, "AMERICAS", 8, 8),   # 22 White House (DC, offset)
    (-77.0, 38.9, "AMERICAS", -8, -8), # 23 Judge / arch (DC, offset)
    (-99.1, 19.4, "AMERICAS", 0, 0),   # 24 Mexico City (Sheinbaum)
    (33.4, 47.9, "EUROPE", 12, 12),   # 25 Kryvyi Rih (fanned from Kyiv pin)
    (30.5, 50.4, "EUROPE", -16, -14),  # 26 Kyiv laser (offset from pin 1)
    (50.5, 55.8, "EUROPE", 10, -12),  # 27 Tatarstan (Druzhba, fanned from Kyiv pin)
    (19.4, 52.0, "EUROPE", -14, -10),  # 28 Poland (Warsaw, fanned from Berlin pin)
    (28.8, 47.0, "EUROPE", 0, 0),     # 29 Moldova (Chisinau)
    (38.7, 9.0, "AFRICA", 0, 0),      # 30 Addis Ababa (COP32)
    (30.2, 13.2, "AFRICA", -10, -8),  # 31 Sudan (El Obeid, fanned from Gaza pin)
    (29.2, -2.5, "AFRICA", 0, 0),     # 32 South Kivu (Congo)
    (149.1, -35.3, "OCEANIA", 0, 0),  # 33 Canberra (Aus/Can/NZ)
    (138.6, -34.9, "OCEANIA", -10, -10),  # 34 Adelaide (fanned from Canberra dot)
    (174.8, -41.3, "OCEANIA", 0, 0),  # 35 Wellington (One NZ)
    (51.4, 28.9, "MIDDLE EAST", 10, 8),  # 36 Kharg Island (Iran tankers, fanned from Riyadh pin)
    (57.0, 26.5, "MIDDLE EAST", 14, -10),  # 37 Strait of Hormuz (MQ-9, fanned from Riyadh pin)
    (43.6, 32.8, "MIDDLE EAST", 0, 0),  # 38 Jurf al Sakhr (Iraq)
    (-30.0, 20.0, "GLOBAL", 0, 0),    # 39 Study (global story, mid-Atlantic)
    (-20.0, 30.0, "GLOBAL", 0, 0),    # 40 CO2 (global story, mid-Atlantic)
]

# ---------------- lead art (317 x 76) ----------------
def draw_lead_art(d, idx, x, y, w, h):
    lead = LEADS[idx]
    d.rectangle([x, y, x + w, y + h], fill=lead["bg"])
    if idx == 0:
        # Kyiv at night: dark sky, missile streaks, bridges over the Dnipro, Poland flag
        d.rectangle([x, y, x + w, y + 52], fill=(24, 32, 54))
        for sx, sy in [(30, 10), (90, 6), (150, 14), (210, 8), (270, 12), (60, 22), (180, 20)]:
            d.ellipse([x + sx, y + sy, x + sx + 2, y + sy + 2], fill=WHITE)
        # missile streaks (orange, falling left to right)
        for mx, my, ml in [(40, 8, 46), (150, 4, 52), (240, 12, 40)]:
            d.line([x + mx, y + my, x + mx + ml, y + my + 14], fill=ORANGE, width=3)
            d.ellipse([x + mx + ml - 3, y + my + 11, x + mx + ml + 3, y + my + 17],
                      fill=(255, 220, 90))
        # Kyiv skyline (dark) + river + three bridges
        d.rectangle([x, y + 52, x + w, y + h], fill=(70, 110, 160))
        for bx, bw, bh in [(10, 26, 18), (48, 20, 26), (80, 30, 14), (120, 22, 24),
                           (152, 28, 16), (192, 20, 26), (224, 30, 14), (266, 24, 20)]:
            d.rectangle([x + bx, y + 52 - bh, x + bx + bw, y + 52], fill=(16, 22, 40))
            for wy in range(0, bh - 4, 7):
                d.rectangle([x + bx + 4, y + 52 - bh + wy, x + bx + 8, y + 52 - bh + wy + 3],
                            fill=(255, 220, 90))
        # three bridges across the river
        for bxx in (40, 140, 240):
            d.line([x + bxx, y + 58, x + bxx + 56, y + 58], fill=WHITE, width=3)
            d.line([x + bxx + 10, y + 58, x + bxx + 10, y + 68], fill=WHITE, width=2)
            d.line([x + bxx + 46, y + 58, x + bxx + 46, y + 68], fill=WHITE, width=2)
        # Poland flag marker (right)
        flag(d, x + w - 34, y + 56, 26, 14, [WHITE, (220, 20, 60)])
        d.text((x + w - 52, y + 56), "PL", font=F_TINY_B, fill=WHITE)
        chip(d, x + 8, y + 6, "515", RED)
        chip(d, x + 62, y + 6, "27 + 84 + 404", NAVY)
    elif idx == 1:
        # COP31: globe + clock at 22:29 + empty chairs, "NO DEAL" banner
        cx, cy, r = x + 62, y + 38, 28
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(120, 170, 200))
        d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=NAVY, width=2)
        d.ellipse([cx - r + 7, cy - r + 5, cx - r + 19, cy - r + 15], fill=(90, 140, 90))
        d.ellipse([cx + 3, cy + 7, cx + 17, cy + 19], fill=(90, 140, 90))
        d.line([cx - r, cy, cx + r, cy], fill=NAVY, width=1)
        # clock (right of globe)
        ccx, ccy, cr = x + 150, y + 38, 22
        d.ellipse([ccx - cr, ccy - cr, ccx + cr, ccy + cr], fill=WHITE, outline=INK, width=2)
        d.line([ccx, ccy, ccx, ccy - 14], fill=INK, width=2)
        d.line([ccx, ccy, ccx + 11, ccy + 6], fill=INK, width=2)
        d.text((ccx - 14, ccy + cr + 2), "22:29", font=F_TINY_B, fill=INK)
        # empty chairs row
        for chx in (200, 232, 264):
            d.rectangle([chx, y + 46, chx + 22, y + 52], fill=(120, 90, 60))
            d.rectangle([chx + 2, y + 52, chx + 6, y + 66], fill=(120, 90, 60))
            d.rectangle([chx + 16, y + 52, chx + 20, y + 66], fill=(120, 90, 60))
        # "NO DEAL" stamp (top right) + "$120BN DROPPED" chip (top centre)
        d.rectangle([x + 228, y + 8, x + 228 + 72, y + 26], fill=RED)
        d.text((x + 234, y + 11), "NO DEAL", font=F_SMALL_B, fill=WHITE)
        chip(d, x + 100, y + 6, "$120BN DROPPED", RED)
    else:
        # EU-UK: UK flag + EU stars circle + handshake + three checkmarks
        flag(d, x + 20, y + 8, 44, 26, [(0, 36, 125), WHITE, (200, 16, 46)])
        d.line([x + 20, y + 21, x + 64, y + 21], fill=WHITE, width=4)
        d.line([x + 42, y + 8, x + 42, y + 34], fill=WHITE, width=4)
        d.line([x + 20, y + 8, x + 64, y + 34], fill=RED, width=2)
        d.line([x + 64, y + 8, x + 20, y + 34], fill=RED, width=2)
        # EU circle of stars
        ecx, ecy = x + 118, y + 21
        d.ellipse([ecx - 20, ecy - 20, ecx + 20, ecy + 20], fill=(0, 51, 153))
        for k in range(12):
            a = math.radians(k * 30 - 90)
            sx, sy = ecx + 13 * math.cos(a), ecy + 13 * math.sin(a)
            d.ellipse([sx - 1.5, sy - 1.5, sx + 1.5, sy + 1.5], fill=(255, 204, 0))
        # handshake: two hands meeting
        hx, hy = x + 180, y + 48
        d.polygon([(hx - 26, hy - 8), (hx - 4, hy - 8), (hx + 4, hy), (hx - 4, hy + 8),
                   (hx - 26, hy + 8)], fill=(232, 190, 150))
        d.polygon([(hx + 26, hy - 8), (hx + 4, hy - 8), (hx - 4, hy), (hx + 4, hy + 8),
                   (hx + 26, hy + 8)], fill=(210, 165, 130))
        # three checkmarks: food / carbon / youth (labels live in the banner)
        for i in range(3):
            cx0 = x + 216 + i * 34
            d.ellipse([cx0, y + 8, cx0 + 20, y + 28], fill=GREEN)
            d.line([cx0 + 4, y + 18, cx0 + 9, y + 23, cx0 + 16, y + 12], fill=WHITE, width=2)
        person(d, x + 150, y + 66, 30, NAVY)
        person(d, x + 210, y + 66, 30, (60, 60, 60))
    # bottom banner (all leads)
    d.rectangle([x, y + h - 16, x + w, y + h], fill=NAVY)
    bw = tw(F_BANNER, lead["banner"])
    d.text((x + (w - bw) / 2, y + h - 13), lead["banner"], font=F_BANNER, fill=WHITE)


# ---------------- card art (188 x 44) ----------------
def draw_card_art(d, scene, x, y, w, h, chip_text, chip_fill):
    if scene == "akvan":
        d.rectangle([x, y, x + w, y + h], fill=(198, 220, 235))
        spiral(d, x + 70, y + 24, 20, NAVY, 3)
        for i in range(3):
            lx = x + 128 + i * 14
            d.line([lx, y + 8, lx - 7, y + 22], fill=(90, 130, 180), width=2)
        d.polygon([(x + 140, y + h), (x + w, y + h), (x + w, y + 26)], fill=(210, 190, 140))
        d.text((x + 8, y + 28), "ODISHA", font=F_TINY_B, fill=NAVY)
    elif scene == "markets":
        d.rectangle([x, y, x + w, y + h], fill=(240, 230, 225))
        for gy in (y + 10, y + 22, y + 34):
            d.line([x + 8, gy, x + w - 8, gy], fill=(210, 200, 190), width=1)
        d.line([(x + 10, y + 8), (x + 50, y + 14), (x + 90, y + 12),
                (x + 130, y + 28), (x + 170, y + 40)], fill=RED, width=3, joint="curve")
        d.polygon([(x + 164, y + 40), (x + 170, y + 32), (x + 176, y + 40)], fill=RED)
        d.text((x + 8, y + 28), "KOSPI", font=F_TINY_B, fill=RED)
    elif scene == "haiti":
        d.rectangle([x, y, x + w, y + h], fill=(228, 220, 200))
        for tx in (x + 30, x + 95, x + 155):
            d.polygon([(tx - 22, y + h), (tx, y + 12), (tx + 22, y + h)], fill=(190, 170, 130))
            d.rectangle([tx - 3, y + 28, tx + 3, y + h], fill=RED)
        d.rectangle([x, y + 20, x + w, y + 26], fill=(255, 220, 0))
        d.text((x + 8, y + 30), "MARTISSANT", font=F_TINY_B, fill=INK)
    elif scene == "ice":
        d.rectangle([x, y, x + w, y + h], fill=(24, 32, 54))
        d.rectangle([x + 12, y + 8, x + w - 12, y + h - 8], fill=(16, 22, 40))
        d.text((x + 20, y + 10), "$", font=_pf(26, b"Bold"), fill=(120, 220, 130))
        for i, bh in enumerate([14, 22, 18, 28]):
            bx = x + 70 + i * 26
            d.rectangle([bx, y + h - 8 - bh, bx + 16, y + h - 8], fill=GREEN)
        d.text((x + 150, y + 12), "41,7", font=_dj(13, True), fill=WHITE)
    elif scene == "merz":
        d.rectangle([x, y, x + w, y + h], fill=(222, 228, 238))
        # podium + speaker + EU flag
        d.rectangle([x + 84, y + 26, x + 104, y + h], fill=(90, 60, 40))
        person(d, x + 94, y + 28, 26, NAVY)
        flag(d, x + 130, y + 8, 36, 20, [(0, 51, 153), (0, 51, 153)])
        for k in range(8):
            a = math.radians(k * 45 - 90)
            sx, sy = x + 148 + 8 * math.cos(a), y + 18 + 6 * math.sin(a)
            d.ellipse([sx - 1, sy - 1, sx + 1, sy + 1], fill=(255, 204, 0))
        d.text((x + 8, y + 10), "BERLIN", font=F_TINY_B, fill=NAVY)
    elif scene == "boat":
        d.rectangle([x, y, x + w, y + h], fill=(190, 210, 225))
        d.rectangle([x, y + 28, x + w, y + h], fill=(70, 120, 170))
        # overloaded barge
        d.polygon([(x + 40, y + 26), (x + 150, y + 26), (x + 140, y + 38), (x + 50, y + 38)],
                  fill=(120, 80, 50))
        for px in (60, 80, 100, 120, 138):
            d.ellipse([px - 4, y + 14, px + 4, y + 24], fill=(232, 190, 150))
        d.arc([x + 10, y + 34, x + 50, y + 44], 0, 180, fill=WHITE, width=2)
        d.arc([x + 140, y + 36, x + 180, y + 46], 0, 180, fill=WHITE, width=2)
    elif scene == "xi":
        d.rectangle([x, y, x + w, y + h], fill=(235, 222, 200))
        flag(d, x + 16, y + 8, 40, 22, [RED, RED, RED, RED, RED])
        d.ellipse([x + 20, y + 11, x + 25, y + 16], fill=(255, 222, 0))
        flag(d, x + 132, y + 8, 40, 22, [BLUE, BLUE, BLUE, BLUE, BLUE])
        for sx in (138, 148, 158, 166):
            d.ellipse([sx, y + 26, sx + 3, y + 29], fill=WHITE)
        person(d, x + 70, y + 40, 26, NAVY)
        person(d, x + 118, y + 40, 26, (60, 60, 60))
    elif scene == "saudi":
        d.rectangle([x, y, x + w, y + h], fill=(235, 222, 200))
        tx = x + w // 2
        d.polygon([(tx - 12, y + h), (tx - 12, y + 14), (tx, y + 4), (tx + 12, y + 14),
                   (tx + 12, y + h)], fill=(50, 50, 60))
        for wy in range(y + 18, y + h - 4, 8):
            d.rectangle([tx - 8, wy, tx + 8, wy + 3], fill=(255, 220, 90))
        for ang in range(0, 360, 45):
            a = math.radians(ang)
            d.line([tx, y + 10, tx + 15 * math.cos(a), y + 10 + 15 * math.sin(a)],
                   fill=ORANGE, width=3)
        d.ellipse([tx - 5, y + 5, tx + 5, y + 15], fill=(255, 200, 60))
    elif scene == "global":
        # world markets: three falling mini-charts (Asia / Europe / US) + globe
        d.rectangle([x, y, x + w, y + h], fill=(24, 32, 54))
        for i, (cx0, col) in enumerate([(14, RED), (72, ORANGE), (130, (255, 220, 90))]):
            d.line([(x + cx0, y + 10), (x + cx0 + 16, y + 16), (x + cx0 + 32, y + 14),
                    (x + cx0 + 46, y + 32)], fill=col, width=3, joint="curve")
            d.polygon([(x + cx0 + 42, y + 32), (x + cx0 + 46, y + 26),
                       (x + cx0 + 50, y + 32)], fill=col)
        d.text((x + 8, y + 30), "ASIA \u00b7 EUROPE \u00b7 US", font=F_TINY_B, fill=WHITE)
    elif scene == "gaza":
        d.rectangle([x, y, x + w, y + h], fill=(228, 220, 200))
        for tx in (x + 28, x + 94, x + 158):
            d.polygon([(tx - 22, y + h), (tx, y + 12), (tx + 22, y + h)], fill=(190, 170, 130))
            d.rectangle([tx - 3, y + 28, tx + 3, y + h], fill=RED)
        d.rectangle([x, y + 20, x + w, y + 26], fill=(255, 220, 0))
        d.text((x + 8, y + 30), "YELLOW LINE", font=F_TINY_B, fill=INK)
    else:
        raise ValueError(f"unknown scene {scene!r}")
    # data chip (top-left, white outline for contrast)
    cw = int(tw(F_CHIP, chip_text)) + 14
    d.rounded_rectangle([x + 4, y + 4, x + 4 + cw, y + 22], radius=4,
                        fill=chip_fill, outline=WHITE, width=1)
    d.text((x + 11, y + 7), chip_text, font=F_CHIP, fill=WHITE)

# ---------------- sections ----------------
def draw_masthead(d):
    d.rectangle([MX, 8, RIGHT, 100], fill=NAVY)
    d.text((MX, 12), "THE WORLD IN ONE DAY", font=F_KICK, fill=(200, 205, 220))
    cw = int(tw(F_CHIP, "FRI 20 NOV 2026")) + 14
    chip(d, RIGHT - cw - 10, 10, "FRI 20 NOV 2026", RED)
    d.text((MX, 24), "Friday 20 November 2026", font=F_MAST, fill=WHITE)
    d.text((MX, 88), "40 STORIES \u00b7 SEVEN REGIONS", font=F_SMALL_B, fill=(200, 205, 220))
    rt = "ONE DAY \u00b7 ONE PAGE"
    d.text((RIGHT - tw(F_SMALL_B, rt), 88), rt, font=F_SMALL_B, fill=(200, 205, 220))
    sub = ("Russia\u2019s 515-weapon barrage falls on Poland \u00b7 COP31 misses its deadline "
           "\u00b7 UK and EU strike a post-Brexit reset")
    d.text((MX, 106), sub, font=F_SUB_I, fill=RED)


def draw_region_bar(d):
    y0, y1 = 126, 144
    x = MX
    total = sum(n for _, n in REGION_COUNTS)
    for reg, n in REGION_COUNTS:
        w = CW * n / total
        d.rectangle([x, y0, x + w, y1], fill=REGION[reg])
        lab = f"{reg} {n}"
        d.text((x + (w - tw(F_SMALL_B, lab)) / 2, y0 + 4), lab, font=F_SMALL_B, fill=WHITE)
        x += w


def draw_utc(d):
    y = 152
    d.text((MX, y + 4), "THE DAY", font=F_LABEL, fill=NAVY)
    d.text((MX, y + 18), "IN UTC", font=F_LABEL, fill=NAVY)
    slot_x = 150
    slot_w = (RIGHT - slot_x) / len(TIMELINE)
    for i, (t, lab) in enumerate(TIMELINE):
        x = slot_x + i * slot_w
        d.text((x, y), t, font=F_TL_TIME, fill=RED)
        lines = fit_lines(lab, F_TL, slot_w - 8, 2)
        draw_lines(d, lines, x, y + 17, F_TL, INK, 10)
        if i:
            d.line([x - 5, y, x - 5, y + 30], fill=HAIR, width=1)
    d.line([MX, y + 36, RIGHT, y + 36], fill=HAIR, width=1)


def draw_stats(d):
    y0, y1 = 196, 222
    cw = CW / len(STATS)
    for i, (num, lab) in enumerate(STATS):
        cx = MX + cw * i + cw / 2
        d.text((cx - tw(F_STAT_N, num) / 2, y0), num, font=F_STAT_N, fill=RED)
        d.text((cx - tw(F_STAT_L, lab) / 2, y0 + 20), lab, font=F_STAT_L, fill=INK)
        if i:
            d.line([MX + cw * i, y0 + 2, MX + cw * i, y1 - 4], fill=HAIR, width=1)
    d.line([MX, y1, RIGHT, y1], fill=HAIR, width=1)


def draw_top_label(d):
    d.text((MX, 228), "TOP STORIES", font=F_LABEL, fill=NAVY)
    legend = [
        ("CONFIRMED", "on the record"),
        ("REPORTED", "news report"),
        ("CLAIM", "one side\u2019s account"),
        ("FORECAST", "forecast"),
    ]
    total = tw(F_SMALL_B, "HOW SURE: ") + 2
    for tag, defin in legend:
        total += 11 + tw(F_TINY_B, tag) + 3 + tw(F_TINY, defin) + 14
    x = RIGHT - total
    d.text((x, 229), "HOW SURE:", font=F_SMALL_B, fill=INK)
    x += tw(F_SMALL_B, "HOW SURE: ") + 2
    for tag, defin in legend:
        d.rectangle([x, 231, x + 8, 239], fill=TAG_COLOR[tag])
        x += 11
        d.text((x, 229), tag, font=F_TINY_B, fill=INK)
        x += tw(F_TINY_B, tag) + 3
        d.text((x, 229), defin, font=F_TINY, fill=GREY)
        x += tw(F_TINY, defin) + 14


def draw_leads(d):
    xs = [MX, 353, 682]
    for i, lead in enumerate(LEADS):
        x = xs[i]
        w = 317
        draw_lead_art(d, i, x, 240, w, 76)
        d.ellipse([x, 322, x + 7, 329], fill=REGION[lead["region"]])
        d.text((x + 11, 321), lead["kicker"], font=F_KICK, fill=REGION[lead["region"]])
        lines = fit_lines(lead["headline"], F_LEAD_H, w, 2)
        draw_lines(d, lines, x, 338, F_LEAD_H, INK, 22)
        dlines = fit_lines(lead["deck"], F_DECK, w, 2)
        draw_lines(d, dlines, x, 384, F_DECK, INK, 13)


def draw_cards(d):
    xs = [MX + i * 196 for i in range(5)]
    ys = [416, 560]
    for r in range(2):
        for c in range(5):
            card = CARDS[r * 5 + c]
            num = 4 + r * 5 + c
            x, y = xs[c], ys[r]
            w = 188
            d.rectangle([x, y, x + w, y + 136], fill=(252, 250, 244), outline=HAIR, width=1)
            draw_card_art(d, card["scene"], x + 1, y + 1, w - 2, 44,
                          card["chip"], card["chip_fill"])
            d.rectangle([x + 1, y + 45, x + w - 1, y + 59], fill=NAVY)
            label_in_box(d, f"{num} \u00b7 {card['loc']}", x + 5, y + 48, w - 10, F_LOC, WHITE)
            lines = fit_lines(card["headline"], F_CARD_H, w - 12, 2)
            draw_lines(d, lines, x + 6, y + 62, F_CARD_H, INK, 16)
            dlines = fit_lines(card["deck"], F_DECK, w - 12, 2)
            draw_lines(d, dlines, x + 6, y + 96, F_DECK, INK, 12)
            tag = card["tag"]
            src = f"{card['src']} \u00b7 "
            d.text((x + 6, y + 122), src, font=F_SRC, fill=GREY)
            d.text((x + 6 + tw(F_SRC, src), y + 122), tag, font=F_TINY_B,
                   fill=TAG_COLOR[tag])


# map projection: lon -180..180 -> x 24..350 ; lat 75..-60 -> y 718..884
MAP_X0, MAP_Y0, MAP_W, MAP_H = MX, 718, 326, 166
MAP_SX = MAP_W / 360.0
MAP_SY = MAP_H / 135.0


def mxy(lon, lat):
    return (MAP_X0 + (lon + 180) * MAP_SX, MAP_Y0 + (75 - lat) * MAP_SY)


def draw_map(d):
    d.rectangle([MAP_X0, MAP_Y0, MAP_X0 + MAP_W, MAP_Y0 + MAP_H], fill=SEA)
    for poly in POLYS:
        pts = [mxy(lon, lat) for lon, lat in poly]
        d.polygon(pts, fill=LAND, outline=LAND_LINE)
    # brief dots first, pins last
    for lon, lat, reg, dx, dy in DOTS:
        px, py = mxy(lon, lat)
        px, py = px + dx, py + dy
        d.ellipse([px - 3.5, py - 3.5, px + 3.5, py + 3.5],
                  fill=REGION[reg], outline=WHITE, width=1)
    pin_pts = []
    for num, lon, lat, dx, dy in PINS:
        px, py = mxy(lon, lat)
        px, py = px + dx, py + dy
        pin_pts.append((num, px, py))
        d.ellipse([px - 7, py - 7, px + 7, py + 7], fill=NAVY, outline=WHITE, width=1)
        t = str(num)
        d.text((px - tw(F_TINY_B, t) / 2, py - 6), t, font=F_TINY_B, fill=WHITE)
    # pin spacing assert (>=16px centre-to-centre)
    for i in range(len(pin_pts)):
        for j in range(i + 1, len(pin_pts)):
            ddx = pin_pts[i][1] - pin_pts[j][1]
            ddy = pin_pts[i][2] - pin_pts[j][2]
            dist = math.hypot(ddx, ddy)
            assert dist >= 16, (
                f"PINS TOO CLOSE: {pin_pts[i][0]} vs {pin_pts[j][0]} = {dist:.1f}px")
    return pin_pts


def draw_bottom(d):
    d.text((MX, 702), "WHERE IT HAPPENED", font=_dj(12, True), fill=NAVY)
    d.text((366, 702), "ALSO ON FRIDAY 20 NOVEMBER", font=_dj(12, True), fill=NAVY)
    draw_map(d)
    d.text((MX, 888), "Pins 1\u201313: lead + card stories  \u00b7  dots: briefs 14\u201340",
           font=F_TINY, fill=GREY)
    # briefs (two columns, 14 + 13)
    cols = [(366, BRIEFS[:14]), (688, BRIEFS[14:])]
    for cx, items in cols:
        yy = 718.0
        for num, reg, prefix, text in items:
            full = f"{num}. {prefix} \u2014 {text}"
            font = F_BRIEF
            if tw(font, full) > 310:
                font = _dj(11)
            assert tw(font, full) <= 310, f"BRIEF OVERFLOW: {full!r} {tw(font, full):.0f}"
            d.text((cx, yy), f"{num}.", font=_dj(12, True), fill=REGION[reg])
            nx = cx + tw(_dj(12, True), f"{num}. ")
            d.text((nx, yy), prefix, font=_dj(12, True), fill=INK)
            px = nx + tw(_dj(12, True), prefix)
            d.text((px, yy), f" \u2014 {text}", font=font, fill=INK)
            yy += 12.5
        assert yy <= 900, f"BRIEF COLUMN OVERFLOW to y={yy}"


def draw_howto(d):
    d.rectangle([MX, 902, RIGHT, 920], fill=(238, 231, 214))
    t = ("HOW TO READ: At thumbnail size, the date, three leads and ten big picture stories "
         "are the words. At full size, 27 briefs by region. Numbered pins are the picture stories.")
    assert tw(F_TINY, t) <= 960, f"HOW TO READ OVERFLOW {tw(F_TINY, t):.0f}"
    d.text((MX + 8, 906), t, font=F_TINY, fill=INK)


def draw_datecheck(d):
    d.rectangle([MX, 926, RIGHT, 978], fill=(250, 235, 230), outline=RED, width=1)
    l1 = fit_lines("DATE CHECK \u2014 LEFT OUT (NOT 20 NOV): " + DATE_OUT, F_TINY, 944, 3)
    draw_lines(d, l1, MX + 8, 928, F_TINY, INK, 11)
    y = 928 + 11 * len(l1)
    d.text((MX + 8, y), "NOT YET: " + DATE_NOTYET, font=F_TINY, fill=INK)
    assert y + 11 <= 978, "DATE CHECK OVERFLOW"


def draw_footer(d):
    f1 = ("Sources: Reuters \u00b7 AP \u00b7 AFP \u00b7 ISW \u00b7 IMD \u00b7 Xinhua \u00b7 CNA \u00b7 Al Jazeera "
          "\u00b7 Global Carbon Budget \u2014 Pictures and map: original, drawn in code.")
    d.text((MX, 984), f1, font=F_FOOT, fill=GREY)
    f2 = ("Every story here happened, or was first reported, on Friday 20 November 2026. "
          "Claims are attributed, not stated as fact.")
    d.text((MX, 994), f2, font=F_FOOT, fill=GREY)

# ---------------- main ----------------
def build():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    draw_masthead(d)
    draw_region_bar(d)
    draw_utc(d)
    draw_stats(d)
    draw_top_label(d)
    draw_leads(d)
    draw_cards(d)
    draw_bottom(d)
    draw_howto(d)
    draw_datecheck(d)
    draw_footer(d)
    img.save(OUT, format="PNG", compress_level=6)
    return img


def word_count_report():
    """Words per story (headline+deck for drawn; text for briefs)."""
    total = 0
    for lead in LEADS:
        total += len((lead["headline"] + " " + lead["deck"]).split())
    for card in CARDS:
        total += len((card["headline"] + " " + card["deck"]).split())
    for _, _, _, text in BRIEFS:
        total += len(text.split())
    return total


if __name__ == "__main__":
    img = build()
    size = os.path.getsize(OUT)
    assert size <= 1024 * 1024, f"FILE TOO BIG: {size} bytes"
    assert img.size == (1024, 1024)
    # region counts sum
    assert sum(n for _, n in REGION_COUNTS) == 40, "REGION SUM != 40"
    assert len(BRIEFS) == 27 and len(CARDS) == 10 and len(LEADS) == 3
    assert len(PINS) == 13 and len(DOTS) == 27
    words = word_count_report()
    print(f"entry.png: {size} bytes, {img.size[0]}x{img.size[1]}")
    print(f"stories: 40 (3 leads + 10 cards + 27 briefs)")
    print(f"words total: {words} ({words / 40:.1f} per story)")
    print(f"region counts: {REGION_COUNTS} sum={sum(n for _, n in REGION_COUNTS)}")
    print("OK")
