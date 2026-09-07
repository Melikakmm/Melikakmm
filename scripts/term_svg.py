#!/usr/bin/env python3
"""Render the profile's terminal/hero panels as static SVG.

Used to build the terminal-style blocks in README.md, since GitHub's
markdown renderer strips raw ANSI escape bytes from .md source before
rendering (confirmed empirically — `ansi` code fences do not colorize
in READMEs), so real colored terminal text has to ship as an image
instead of markdown text.
"""
import html
import sys

FONT = "ui-monospace, SFMono-Regular, Menlo, Consolas, 'Liberation Mono', monospace"
FONT_SIZE = 14
LINE_HEIGHT = 21
CHAR_WIDTH = 8.4
PAD_X = 22
PAD_TOP = 44
PAD_BOTTOM = 20
TITLEBAR_H = 34

# palette
BG = "#05070a"
TITLEBAR = "#0a0f14"
BORDER = "#1c2430"
FG = "#dbe4ec"
GREEN = "#00ffa3"
MAGENTA = "#ff2e88"
CYAN = "#56d4dd"
YELLOW = "#e3b341"
DIM = "#5b6674"


def _defs():
    return (
        "<defs>"
        f'<linearGradient id="accent" x1="0" y1="0" x2="1" y2="0">'
        f'<stop offset="0" stop-color="{GREEN}"/><stop offset="1" stop-color="{MAGENTA}"/>'
        "</linearGradient>"
        '<filter id="glow" x="-60%" y="-60%" width="220%" height="220%">'
        '<feGaussianBlur stdDeviation="2" result="blur"/>'
        '<feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>'
        "</filter>"
        '<pattern id="scan" width="3" height="3" patternUnits="userSpaceOnUse">'
        f'<rect width="3" height="1" fill="{FG}" opacity="0.025"/>'
        "</pattern>"
        "</defs>"
    )


def build_svg(rows, out_path, title=None):
    """rows: list of lines, each line a list of (text, color) segments.

    A segment's color may be a plain hex string, or the tuple (color, "glow")
    to render that run with the soft glow filter (use sparingly).
    """
    max_len = max(sum(len(seg[0]) for seg in row) for row in rows) if rows else 0
    width = int(PAD_X * 2 + max_len * CHAR_WIDTH)
    height = int(PAD_TOP + len(rows) * LINE_HEIGHT + PAD_BOTTOM)

    parts = []
    parts.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" font-family="{FONT}" font-size="{FONT_SIZE}">'
    )
    parts.append(_defs())
    parts.append(
        f'<rect x="0.5" y="0.5" width="{width - 1}" height="{height - 1}" rx="10" '
        f'fill="{BG}" stroke="{BORDER}" />'
    )
    parts.append(
        f'<rect x="1" y="1" width="{width - 2}" height="{height - 2}" rx="9.5" '
        f'fill="url(#scan)" />'
    )
    parts.append(
        f'<path d="M0.5 {TITLEBAR_H} V11 Q0.5 0.5 11 0.5 H{width - 11} '
        f'Q{width - 0.5} 0.5 {width - 0.5} 11 V{TITLEBAR_H} Z" '
        f'fill="{TITLEBAR}" />'
    )
    parts.append(f'<rect x="10" y="{TITLEBAR_H - 1.5}" width="{width - 20}" height="2" fill="url(#accent)" opacity="0.8" />')
    for i, color in enumerate([GREEN, YELLOW, MAGENTA]):
        cx = 22 + i * 15
        parts.append(f'<circle cx="{cx}" cy="{TITLEBAR_H / 2}" r="4" fill="{color}" opacity="0.85" />')
    if title:
        parts.append(
            f'<text x="{width / 2}" y="{TITLEBAR_H / 2 + 4}" text-anchor="middle" '
            f'font-size="11" letter-spacing="1.5" fill="{DIM}">{html.escape(title)}</text>'
        )

    for i, row in enumerate(rows):
        y = PAD_TOP + i * LINE_HEIGHT
        if not row:
            continue
        spans = []
        for seg in row:
            text, color = seg[0], seg[1]
            glow = len(seg) > 2 and seg[2] == "glow"
            esc = html.escape(text)
            fill = color or FG
            attrs = f'fill="{fill}"'
            if glow:
                attrs += ' filter="url(#glow)"'
            if "█" in text and glow:
                blink = (
                    '<animate attributeName="opacity" values="1;1;0;0;1" '
                    'keyTimes="0;0.45;0.5;0.95;1" dur="1.1s" repeatCount="indefinite" />'
                )
                spans.append(f'<tspan {attrs}>{esc}{blink}</tspan>')
            else:
                spans.append(f'<tspan {attrs}>{esc}</tspan>')
        text_body = "".join(spans)
        parts.append(f'<text x="{PAD_X}" y="{y}" xml:space="preserve">{text_body}</text>')

    parts.append("</svg>")
    svg = "\n".join(parts)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(svg)
    return svg


def build_hero_svg(out_path="assets/hero.svg"):
    width, height = 760, 168
    title = "MELIKA"
    subtitle = "PHD FELLOW  ·  DSDD GROUP  ·  UNIVERSITY OF COPENHAGEN"
    tag = "SYSTEM: ONLINE"

    cx, cy = width / 2, 88

    parts = []
    parts.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" font-family="{FONT}">'
    )
    parts.append(_defs())
    parts.append(f'<rect x="0.5" y="0.5" width="{width - 1}" height="{height - 1}" rx="14" fill="{BG}" stroke="{BORDER}" />')
    parts.append(f'<rect x="1" y="1" width="{width - 2}" height="{height - 2}" rx="13.5" fill="url(#scan)" />')

    parts.append(
        f'<text x="40" y="36" font-size="11" letter-spacing="2" fill="{GREEN}" filter="url(#glow)">● {tag}</text>'
    )

    # glitch title: two offset colored ghosts (screen-blended) behind a crisp top layer
    parts.append(
        f'<text x="{cx - 2}" y="{cy + 1}" text-anchor="middle" font-size="58" font-weight="700" '
        f'letter-spacing="6" fill="{MAGENTA}" opacity="0.55" style="mix-blend-mode:screen">{title}</text>'
    )
    parts.append(
        f'<text x="{cx + 2}" y="{cy - 1}" text-anchor="middle" font-size="58" font-weight="700" '
        f'letter-spacing="6" fill="{CYAN}" opacity="0.55" style="mix-blend-mode:screen">{title}</text>'
    )
    parts.append(
        f'<text x="{cx}" y="{cy}" text-anchor="middle" font-size="58" font-weight="700" '
        f'letter-spacing="6" fill="{FG}" filter="url(#glow)">{title}</text>'
    )

    parts.append(
        f'<text x="{cx}" y="{cy + 34}" text-anchor="middle" font-size="12" letter-spacing="2" fill="{DIM}">{subtitle}</text>'
    )

    parts.append(f'<rect x="40" y="{height - 20}" width="{width - 80}" height="2.5" rx="1.25" fill="url(#accent)" />')

    parts.append("</svg>")
    svg = "\n".join(parts)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(svg)
    return svg


def whoami_block():
    """A fake boot log, then the usual whoami/origin-story/ps-aux content."""
    prompt = [("melika@ucph", GREEN), (":", FG), ("~", CYAN), ("$ ", FG)]
    boot = [
        [("[ OK ]", GREEN), (" mounting /dev/curiosity", DIM)],
        [("[ OK ]", GREEN), (" loading theoretical_physics.dll", DIM)],
        [("[ OK ]", GREEN), (" loading structural_biology.dll", DIM)],
        [("[ OK ]", GREEN), (" starting neural-network-daemon", DIM)],
        [("[WARN]", YELLOW), (" attention_span.service — restarting (loop)", DIM)],
        [("[ OK ]", GREEN), (" melika-os v3.7 ready", DIM)],
        [],
    ]
    rest = [
        prompt + [("whoami", FG)],
        [("PhD Fellow, DSDD Group — University of Copenhagen.", FG)],
        [("Physicist by training. AI × protein person by accident. Chaos gremlin by default.", FG)],
        [],
        prompt + [("cat origin_story.txt", FG)],
        [("Started in theoretical physics & pure math.", FG)],
        [("Got distracted by neural networks around year 3.", FG)],
        [("Now I build AI that stares at proteins until it understands them.", FG)],
        [("No regrets. Some deadlines.", FG)],
        [],
        prompt + [("ps aux | grep obsessions", FG)],
        [("USER      PID   OBSESSION                            STATUS", YELLOW)],
        [("melika    0001  protein-protein-interactions        ", FG), ("[main thread]", GREEN)],
        [("melika    0002  black-holes-and-x-ray-binaries      ", FG), ("[running]", GREEN)],
        [("melika    0003  fpga-vhdl-tinkering                 ", FG), ("[sleeping]", DIM)],
        [("melika    0004  volatility-carry-trading-bot        ", FG), ("[running]", GREEN)],
        [("melika    0005  deepjoke-ai                         ", FG), ("[training, ETA: never]", YELLOW)],
        [],
        prompt + [("█", GREEN, "glow")],
    ]
    return boot + rest


def lsquests_block():
    return [
        [("melika@ucph", GREEN), (":", FG), ("~", CYAN), ("$ ", FG), ("ls -la ./side_quests/", FG)],
    ]


def deepjoke_prompt_block():
    return [
        [("melika@ucph", GREEN), (":", FG), ("~", CYAN), ("$ ", FG), ("./deepjoke.sh --run", FG)],
    ]


def deepjoke_block(joke):
    return [
        [("$ ", CYAN), ("./deepjoke.sh --run", CYAN)],
        [("> ", GREEN, "glow"), (joke, GREEN)],
        [("(refreshed daily — deepjoke.ai is still in training)", DIM)],
    ]


def outro_block():
    prompt = [("melika@ucph", GREEN), (":", FG), ("~", CYAN), ("$ ", FG)]
    return [
        prompt + [("cat contact.txt", FG)],
        [("CV      → github.com/Melikakmm/CV/blob/main/MelikaCV.pdf", FG)],
        [("GitHub  → you're already here.", FG)],
        [],
        prompt + [("sudo shutdown -h now", YELLOW), ("  # jk, come say hi first", DIM)],
        prompt + [("█", GREEN, "glow")],
    ]


def neofetch_block():
    fields = [
        ("OS", "melika-OS (Copenhagen Edition)"),
        ("Host", "University of Copenhagen — DSDD Group"),
        ("Kernel", "theoretical-physics 5.∞"),
        ("Uptime", "since 2019 (PhD chapter)"),
        ("Shell", "curiosity --interactive"),
        ("DE", "vscode + tmux"),
        ("CPU", "neurons @ variable GHz (coffee-throttled)"),
        ("GPU", "whatever the cluster gives me"),
        ("Memory", "16GB coffee / 4GB sleep"),
        ("Disk", "/dev/side_quests — 98% full"),
    ]
    label_w = max(len(k) for k, _ in fields) + 1
    rows = [[("melika@ucph", GREEN), (":", FG), ("~", CYAN), ("$ ", FG), ("neofetch", FG)], []]
    for k, v in fields:
        rows.append([(f"{k.ljust(label_w)}", GREEN), ("  " + v, FG)])
    return rows


if __name__ == "__main__":
    joke = sys.argv[1] if len(sys.argv) > 1 else "Why do programmers prefer dark mode? Because light attracts bugs."
    build_hero_svg("assets/hero.svg")
    build_svg(whoami_block(), "assets/term-whoami.svg", title="melika@ucph — whoami.sh")
    build_svg(lsquests_block(), "assets/term-lsquests.svg", title="side_quests/")
    build_svg(neofetch_block(), "assets/term-neofetch.svg", title="melika@ucph — neofetch")
    build_svg(deepjoke_prompt_block(), "assets/term-deepjoke-prompt.svg", title="deepjoke.sh")
    build_svg(deepjoke_block(joke), "assets/term-deepjoke.svg", title="deepjoke.sh — output")
    build_svg(outro_block(), "assets/term-outro.svg", title="contact.sh")
    print("generated 8 svgs")
