#!/usr/bin/env python3
"""Render a fake terminal window as a static SVG.

Used to build the terminal-style blocks in README.md, since GitHub's
markdown renderer strips raw ANSI escape bytes from .md source before
rendering (confirmed empirically — `ansi` code fences do not colorize
in READMEs), so real colored terminal text has to ship as an image
instead of markdown text.
"""
import html
import sys

FONT_SIZE = 14
LINE_HEIGHT = 21
CHAR_WIDTH = 8.4
PAD_X = 22
PAD_TOP = 44
PAD_BOTTOM = 20
TITLEBAR_H = 34

BG = "#0d1117"
BORDER = "#30363d"
TITLEBAR = "#161b22"
FG = "#c9d1d9"

DOTS = ["#ff5f57", "#febc2e", "#28c840"]


def build_svg(rows, out_path):
    """rows: list of lines, each line a list of (text, color) segments."""
    max_len = max(sum(len(t) for t, _ in row) for row in rows) if rows else 0
    width = int(PAD_X * 2 + max_len * CHAR_WIDTH)
    height = int(PAD_TOP + len(rows) * LINE_HEIGHT + PAD_BOTTOM)

    parts = []
    parts.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" font-family="ui-monospace, SFMono-Regular, '
        f'Menlo, Consolas, \'Liberation Mono\', monospace" font-size="{FONT_SIZE}">'
    )
    parts.append(
        f'<rect x="0.5" y="0.5" width="{width - 1}" height="{height - 1}" rx="10" '
        f'fill="{BG}" stroke="{BORDER}" />'
    )
    parts.append(
        f'<path d="M0.5 {TITLEBAR_H} V11 Q0.5 0.5 11 0.5 H{width - 11} '
        f'Q{width - 0.5} 0.5 {width - 0.5} 11 V{TITLEBAR_H} Z" '
        f'fill="{TITLEBAR}" stroke="{BORDER}" />'
    )
    for i, color in enumerate(DOTS):
        cx = 22 + i * 18
        parts.append(f'<circle cx="{cx}" cy="{TITLEBAR_H / 2}" r="5.5" fill="{color}" />')

    for i, row in enumerate(rows):
        y = PAD_TOP + i * LINE_HEIGHT
        if not row:
            continue
        spans = []
        for text, color in row:
            esc = html.escape(text)
            fill = color or FG
            spans.append(f'<tspan fill="{fill}">{esc}</tspan>')
        parts.append(f'<text x="{PAD_X}" y="{y}" xml:space="preserve">{"".join(spans)}</text>')

    parts.append("</svg>")
    svg = "\n".join(parts)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(svg)
    return svg


# color palette
GREEN = "#39FF14"
CYAN = "#56d4dd"
YELLOW = "#e3b341"
DIM = "#6e7681"
FG_C = FG


def whoami_block():
    prompt = [("melika@ucph", GREEN), (":", FG_C), ("~", CYAN), ("$ ", FG_C)]
    return [
        prompt + [("whoami", FG_C)],
        [("PhD Fellow, DSDD Group — University of Copenhagen.", FG_C)],
        [("Physicist by training. AI × protein person by accident. Chaos gremlin by default.", FG_C)],
        [],
        prompt + [("cat origin_story.txt", FG_C)],
        [("Started in theoretical physics & pure math.", FG_C)],
        [("Got distracted by neural networks around year 3.", FG_C)],
        [("Now I build AI that stares at proteins until it understands them.", FG_C)],
        [("No regrets. Some deadlines.", FG_C)],
        [],
        prompt + [("ps aux | grep obsessions", FG_C)],
        [("USER      PID   OBSESSION                            STATUS", YELLOW)],
        [("melika    0001  protein-protein-interactions        ", FG_C), ("[main thread]", GREEN)],
        [("melika    0002  black-holes-and-x-ray-binaries      ", FG_C), ("[running]", GREEN)],
        [("melika    0003  fpga-vhdl-tinkering                 ", FG_C), ("[sleeping]", DIM)],
        [("melika    0004  volatility-carry-trading-bot        ", FG_C), ("[running]", GREEN)],
        [("melika    0005  deepjoke-ai                         ", FG_C), ("[training, ETA: never]", YELLOW)],
        [],
        prompt + [("█", GREEN)],
    ]


def lsquests_block():
    return [
        [("melika@ucph", GREEN), (":", FG_C), ("~", CYAN), ("$ ", FG_C), ("ls -la ./side_quests/", FG_C)],
    ]


def deepjoke_prompt_block():
    return [
        [("melika@ucph", GREEN), (":", FG_C), ("~", CYAN), ("$ ", FG_C), ("./deepjoke.sh --run", FG_C)],
    ]


def deepjoke_block(joke):
    return [
        [("$ ", CYAN), ("./deepjoke.sh --run", CYAN)],
        [("> ", GREEN), (joke, GREEN)],
        [("(refreshed daily — deepjoke.ai is still in training)", DIM)],
    ]


def outro_block():
    prompt = [("melika@ucph", GREEN), (":", FG_C), ("~", CYAN), ("$ ", FG_C)]
    return [
        prompt + [("cat contact.txt", FG_C)],
        [("CV      → github.com/Melikakmm/CV/blob/main/MelikaCV.pdf", FG_C)],
        [("GitHub  → you're already here.", FG_C)],
        [],
        prompt + [("sudo shutdown -h now", YELLOW), ("  # jk, come say hi first", DIM)],
        prompt + [("█", GREEN)],
    ]


if __name__ == "__main__":
    joke = sys.argv[1] if len(sys.argv) > 1 else "Why do programmers prefer dark mode? Because light attracts bugs."
    build_svg(whoami_block(), "assets/term-whoami.svg")
    build_svg(lsquests_block(), "assets/term-lsquests.svg")
    build_svg(deepjoke_prompt_block(), "assets/term-deepjoke-prompt.svg")
    build_svg(deepjoke_block(joke), "assets/term-deepjoke.svg")
    build_svg(outro_block(), "assets/term-outro.svg")
    print("generated 5 svgs")
