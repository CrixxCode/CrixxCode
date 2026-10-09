"""Generate the README's SVG assets (dark + light) using the portfolio's design tokens.

Usage: python scripts/generate_assets.py
Output: assets/*.svg
"""
import math
import textwrap
from pathlib import Path
from xml.sax.saxutils import escape

OUT = Path(__file__).resolve().parent.parent / "assets"


def oklch(l, c, h):
    a, b = c * math.cos(math.radians(h)), c * math.sin(math.radians(h))
    l_ = l + 0.3963377774 * a + 0.2158037573 * b
    m_ = l - 0.1055613458 * a - 0.0638541728 * b
    s_ = l - 0.0894841775 * a - 1.2914855480 * b
    lc, mc, sc = l_**3, m_**3, s_**3
    rgb = (
        4.0767416621 * lc - 3.3077115913 * mc + 0.2309699292 * sc,
        -1.2684380046 * lc + 2.6097574011 * mc - 0.3413193965 * sc,
        -0.0041960863 * lc - 0.7034186147 * mc + 1.7076147010 * sc,
    )
    srgb = lambda x: max(0, min(1, 12.92 * x if x <= 0.0031308 else 1.055 * x ** (1 / 2.4) - 0.055))
    return "#" + "".join(f"{round(srgb(x) * 255):02X}" for x in rgb)


# Tokens mirrored from the portfolio's :root / .dark CSS variables.
THEMES = {
    "dark": {
        "card": oklch(0.18, 0.004, 270),
        "surface": oklch(0.21, 0.005, 270),
        "fg": oklch(0.955, 0.008, 85),
        "muted": oklch(0.70, 0.012, 260),
        "border": "#FFFFFF1F",
        "primary": oklch(0.66, 0.18, 262),
        "brand2": oklch(0.75, 0.14, 230),
        "success": oklch(0.74, 0.15, 155),
    },
    "light": {
        "card": oklch(0.992, 0.003, 85),
        "surface": oklch(0.94, 0.005, 85),
        "fg": oklch(0.24, 0.008, 260),
        "muted": oklch(0.47, 0.012, 260),
        "border": oklch(0.86, 0.005, 85),
        "primary": oklch(0.52, 0.2, 262),
        "brand2": oklch(0.62, 0.15, 230),
        "success": oklch(0.52, 0.14, 155),
    },
}

SANS = "Geist, 'Segoe UI', system-ui, -apple-system, Helvetica, Arial, sans-serif"
MONO = "'Geist Mono', ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"
SERIF = "'Instrument Serif', Georgia, 'Times New Roman', serif"


def svg(w, h, body, t):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" fill="none">'
        f"<defs><linearGradient id=\"g\" x1=\"0\" y1=\"0\" x2=\"1\" y2=\"0\">"
        f'<stop offset="0" stop-color="{t["primary"]}"/><stop offset="1" stop-color="{t["brand2"]}"/></linearGradient>'
        f'<linearGradient id="fl" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{t["border"]}" stop-opacity="0"/>'
        f'<stop offset="1" stop-color="{t["muted"]}" stop-opacity=".6"/></linearGradient>'
        f'<linearGradient id="fr" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{t["muted"]}" stop-opacity=".6"/>'
        f'<stop offset="1" stop-color="{t["border"]}" stop-opacity="0"/></linearGradient></defs>'
        f"{body}</svg>"
    )


def text(x, y, s, t, size=14, color="fg", family=SANS, anchor="start", weight=400, italic=False, spacing=0):
    style = ' font-style="italic"' if italic else ""
    ls = f' letter-spacing="{spacing}"' if spacing else ""
    return (
        f'<text x="{x}" y="{y}" fill="{t[color]}" font-family="{family}" font-size="{size}" '
        f'font-weight="{weight}" text-anchor="{anchor}"{style}{ls}>{escape(s)}</text>'
    )


def card(x, y, w, h, t, r=16):
    return (
        f'<rect x="{x + .5}" y="{y + .5}" width="{w - 1}" height="{h - 1}" rx="{r}" fill="{t["card"]}" stroke="{t["border"]}"/>'
    )


def accent(x, y, w):
    return f'<rect x="{x}" y="{y}" width="{w}" height="2" rx="1" fill="url(#g)"/>'


# ---------------------------------------------------------------- section headers

SECTIONS = [
    ("01", "FEATURED PROJECTS", "Case studies."),
    ("02", "EXPERIENCE", "Where I put it to work."),
    ("03", "ABOUT", "Engineering with product judgment."),
    ("04", "STACK", "Flexible stack. Solid fundamentals."),
    ("05", "EDUCATION & ACHIEVEMENTS", "Education, results and technical growth."),
    ("06", "GITHUB", "Code that also tells the story."),
    ("07", "SERVICES", "How I can contribute."),
    ("08", "CONTACT", "Let’s build something together."),
]


def header(num, label, title, t):
    w, h, cx = 880, 128, 440
    eyebrow = f"{num}  ·  {label}"
    half = len(eyebrow) * 10.6 / 2 + 18
    body = (
        f'<rect x="160" y="38" width="{cx - half - 160}" height="1" fill="url(#fl)"/>'
        f'<rect x="{cx + half}" y="38" width="{720 - cx - half}" height="1" fill="url(#fr)"/>'
        f'<text x="{cx}" y="43" text-anchor="middle" font-family="{MONO}" font-size="13" letter-spacing="3">'
        f'<tspan fill="{t["primary"]}">{num}</tspan><tspan fill="{t["muted"]}">  ·  {escape(label)}</tspan></text>'
        + text(cx, 98, title, t, size=44, family=SERIF, anchor="middle", italic=True)
        + accent(cx - 24, 116, 48)
    )
    return svg(w, h, body, t)


# ---------------------------------------------------------------- hero code card

def hero(t):
    w, h = 880, 236
    mono = f'font-family="{MONO}" font-size="15" xml:space="preserve"'

    def line(y, parts):
        spans = "".join(f'<tspan fill="{t[c]}">{escape(s)}</tspan>' for s, c in parts)
        return f'<text x="44" y="{y}" {mono}>{spans}</text>'

    body = (
        card(0, 0, w, h, t, r=20)
        + "".join(f'<circle cx="{36 + i * 18}" cy="32" r="5" fill="{t["surface"]}" stroke="{t["border"]}"/>' for i in range(3))
        + text(w / 2, 37, "crixxcode — end-to-end", t, size=12, color="muted", family=MONO, anchor="middle", spacing=1)
        + f'<line x1="0" y1="58" x2="{w}" y2="58" stroke="{t["border"]}"/>'
        + line(98, [("ui/   ", "muted"), ("<ReservationList />", "primary"), ("  →  reservation.service  →  ", "fg"), ("GET /reservations", "brand2")])
        + line(132, [("api/  ", "muted"), ("GET  /reservations   ", "fg"), ("200", "success")])
        + line(160, [("      ", "muted"), ("POST /exams          ", "fg"), ("201", "success")])
        + f'<line x1="44" y1="186" x2="{w - 44}" y2="186" stroke="{t["border"]}" stroke-dasharray="3 5"/>'
        + text(44, 214, "11.54°N · 72.91°W", t, size=12, color="muted", family=MONO, spacing=1)
        + text(w - 44, 214, "interface ↔ logic ↔ data", t, size=12, color="primary", family=MONO, anchor="end", spacing=1)
    )
    return svg(w, h, body, t)


# ---------------------------------------------------------------- highlight tiles

def highlights(t):
    tiles = [
        ("Full-Stack", "FRONTEND + BACKEND"),
        ("End-to-End", "FROM PROBLEM TO PRODUCT"),
        ("1st place", "PROGRAMMING MARATHON"),
        ("B2", "ENGLISH · SABER PRO"),
    ]
    tw, gap, h = 205, 20, 120
    body = ""
    for i, (value, label) in enumerate(tiles):
        x = i * (tw + gap)
        body += card(x, 0, tw, h, t) + accent(x + 24, 22, 28)
        body += text(x + tw / 2, 70, value, t, size=32, family=SERIF, anchor="middle", italic=True)
        body += text(x + tw / 2, 96, label, t, size=10, color="muted", family=MONO, anchor="middle", spacing=1.5)
    return svg(4 * tw + 3 * gap, h, body, t)


# ---------------------------------------------------------------- achievements

ACHIEVEMENTS = [
    (
        "2023",
        "PROGRAMMING MARATHON",
        "1st place",
        "First place in a competition focused on problem solving through algorithm design and implementation.",
        "Organized by the Systems Engineering program at Universidad de La Guajira",
    ),
    (
        "2026 · BOGOTÁ",
        "HACKATHON COLOMBIA 5.0",
        "National Top 10",
        "Ranked among the ten best teams nationwide in an innovation and technology development competition.",
        "",
    ),
]


def achievements(t):
    cw, gap, h = 430, 20, 230
    body = ""
    for i, (year, label, value, desc, note) in enumerate(ACHIEVEMENTS):
        x = i * (cw + gap)
        body += card(x, 0, cw, h, t) + accent(x + 28, 28, 28)
        body += text(x + cw - 28, 34, year, t, size=11, color="primary", family=MONO, anchor="end", spacing=1.5)
        body += text(x + 28, 66, label, t, size=11, color="muted", family=MONO, spacing=2)
        body += text(x + 28, 112, value, t, size=40, family=SERIF, italic=True)
        part, y = wrapped(x + 28, 148, desc, t, 58, 13, color="muted")
        body += part
        if note:
            body += text(x + 28, h - 24, note, t, size=10.5, color="muted", family=SANS, italic=True)
    return svg(2 * cw + gap, h, body, t)


# ---------------------------------------------------------------- saber pro chart

def saber_pro(t):
    w, h = 880, 260
    scores = [
        ("Citizenship Skills", 204),
        ("Critical Reading", 200),
        ("Quantitative Reasoning", 186),
        ("English", 181),
        ("Written Communication", 168),
    ]
    body = card(0, 0, w, h, t, r=20)
    body += text(150, 128, "188", t, size=96, color="primary", family=SERIF, anchor="middle", italic=True)
    body += text(150, 168, "OVERALL SCORE", t, size=11, color="muted", family=MONO, anchor="middle", spacing=2)
    body += text(150, 188, "SABER PRO · SCALE 0–300", t, size=11, color="muted", family=MONO, anchor="middle", spacing=2)
    body += f'<line x1="300" y1="36" x2="300" y2="{h - 36}" stroke="{t["border"]}"/>'
    x0, bar_w = 520, 270
    for i, (label, score) in enumerate(scores):
        y = 52 + i * 38
        body += text(336, y + 5, label, t, size=14)
        body += f'<rect x="{x0}" y="{y - 4}" width="{bar_w}" height="8" rx="4" fill="{t["surface"]}"/>'
        body += f'<rect x="{x0}" y="{y - 4}" width="{bar_w * score / 300:.1f}" height="8" rx="4" fill="url(#g)"/>'
        body += text(w - 36, y + 5, str(score), t, size=14, family=MONO, anchor="end", weight=500)
    return svg(w, h, body, t)


# ---------------------------------------------------------------- cards (repos + services)

def wrapped(x, y, s, t, width, size, color="fg", family=SANS, weight=400, lh=None):
    lh = lh or size * 1.45
    lines = textwrap.wrap(s, width)
    out = "".join(text(x, y + i * lh, ln, t, size=size, color=color, family=family, weight=weight) for i, ln in enumerate(lines))
    return out, y + len(lines) * lh


def repo_card(tag, title, desc, stack, concepts, t):
    w, h = 280, 300
    body = card(0, 0, w, h, t) + accent(24, 24, 28)
    body += text(24, 54, tag.upper(), t, size=10, color="brand2", family=MONO, spacing=1.5)
    part, y = wrapped(24, 84, title, t, 24, 18, weight=600)
    body += part
    part, y = wrapped(24, y + 6, desc, t, 38, 12.5, color="muted")
    body += part
    body += f'<line x1="24" y1="{h - 84}" x2="{w - 24}" y2="{h - 84}" stroke="{t["border"]}"/>'
    # Break the stack between items, never inside one.
    lines, current = [], ""
    for item in stack.split(" · "):
        candidate = f"{current} · {item}" if current else item
        if len(candidate) > 34 and current:
            lines.append(current)
            candidate = item
        current = candidate
    lines.append(current)
    for i, ln in enumerate(lines):
        body += text(24, h - 60 + i * 17, ln, t, size=11, color="primary", family=MONO)
    if concepts:
        body += text(24, h - 24, concepts, t, size=11, color="muted", family=MONO)
    body += text(w - 24, h - 24, "↗", t, size=14, color="fg", anchor="end")
    return svg(w, h, body, t)


def service_card(num, title, desc, t):
    w, h = 280, 210
    body = card(0, 0, w, h, t)
    body += text(24, 46, num, t, size=13, color="primary", family=MONO, spacing=2)
    body += accent(56, 41, 28)
    part, y = wrapped(24, 82, title, t, 26, 18, weight=600)
    body += part
    part, _ = wrapped(24, y + 6, desc, t, 38, 12.5, color="muted")
    body += part
    return svg(w, h, body, t)


REPOS = {
    "repo-wayra": (
        "SaaS product",
        "Wayra Travel",
        "Repository for the hotel management SaaS that evolved from an academic project and is currently in its testing phase.",
        "Django · Angular · PostgreSQL · Docker",
        "RBAC · Multitenancy",
    ),
    "repo-labclinico": (
        "Academic project",
        "Clinical laboratory management system",
        "Full-stack application developed as an academic project to manage workflows related to patients, physicians, orders, exams, samples and results.",
        "Node.js · TypeScript · Express · Angular",
        "",
    ),
    "repo-dotnet": (
        "Technical project",
        "Full-Stack .NET Project",
        "Full-stack application built as a technical exercise using ASP.NET Core, Angular, SQL Server, authentication and container tooling.",
        "ASP.NET Core · Angular · SQL Server · Docker",
        "Testing · GitHub Actions",
    ),
}

SERVICES = {
    "service-fullstack": (
        "01",
        "Full-Stack Development",
        "Building and evolving web applications, contributing from requirements and technical design through frontend, backend and testing.",
    ),
    "service-analysis": (
        "02",
        "Technical analysis & support",
        "Support with requirements analysis, data modeling, API design, technical reviews and improvements to existing solutions.",
    ),
    "service-product": (
        "03",
        "Product collaboration",
        "Joining existing teams and products to implement features, perform QA, resolve issues and support the product’s continued technical evolution.",
    ),
}


def main():
    OUT.mkdir(exist_ok=True)
    for mode, t in THEMES.items():
        files = {"hero": hero(t), "highlights": highlights(t), "achievements": achievements(t), "saber-pro": saber_pro(t)}
        for num, label, title in SECTIONS:
            files[f"header-{num}"] = header(num, label, title, t)
        for name, args in REPOS.items():
            files[name] = repo_card(*args, t)
        for name, args in SERVICES.items():
            files[name] = service_card(*args, t)
        for name, content in files.items():
            (OUT / f"{name}-{mode}.svg").write_text(content, encoding="utf-8")
    print(f"Wrote {len(list(OUT.glob('*.svg')))} SVGs to {OUT}")


if __name__ == "__main__":
    main()
