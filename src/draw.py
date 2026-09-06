"""
Draw system networks for a sentence.

Usage from Python:

    from src.draw import draw

    draw("The lion caught the tourist.")
    draw("She saw the bird.", networks=["transitivity", "theme"])
    draw("He laughed.", png=True)

Usage from the command line:

    python -m src.draw "The lion caught the tourist."
    python -m src.draw "She saw the bird." --png
"""

import os
import re

from src.analyser import analyse_text, NETWORKS
from src.model import SelectionExpression
from src.renderer import render_network

OUTPUT_DIR = "output"

# which analysis block each network is drawn from
NETWORK_SOURCE = {
    "transitivity": "transitivity",
    "theme": "theme",
    "mood": "mood",
}


def _slug(text, limit=40):
    """Turn a sentence into a safe filename stem."""
    s = re.sub(r"[^\w\s-]", "", text).strip().lower()
    s = re.sub(r"[\s_-]+", "_", s)
    return s[:limit].rstrip("_") or "sentence"


def _selection_for(clause_block, network_key):
    """Rebuild a SelectionExpression from an analysed clause."""
    source = NETWORK_SOURCE[network_key]

    if source == "mood":
        if clause_block["mood"] is None:
            return None
        data = clause_block["mood"]["selection"]
    else:
        data = clause_block[source]["selection"]

    return SelectionExpression(
        rank=data["rank"],
        features=set(data["features"]),
        sub_selections=[
            SelectionExpression(rank=s["rank"], features=set(s["features"]))
            for s in data["sub_selections"]
        ],
    )


def _to_png(svg_path):
    """Convert an SVG to PNG if a converter is available. Returns path or None."""
    png_path = svg_path[:-4] + ".png"
    try:
        import cairosvg
        cairosvg.svg2png(url=svg_path, write_to=png_path, scale=2)
        return png_path
    except ImportError:
        pass
    try:
        from svglib.svglib import svg2rlg
        from reportlab.graphics import renderPM
        drawing = svg2rlg(svg_path)
        renderPM.drawToFile(drawing, png_path, fmt="PNG", dpi=144)
        return png_path
    except ImportError:
        return None


def draw(
    sentence,
    networks=("transitivity",),
    output_dir=OUTPUT_DIR,
    png=False,
    only_entered=True,
    quiet=False,
):
    """
    Analyse a sentence and draw a system network for each of its clauses.

    sentence     the text to analyse
    networks     which networks to draw: "transitivity", "theme", "mood"
    output_dir   where the files go (created if missing)
    png          also write a PNG (needs cairosvg or svglib installed)
    only_entered draw only the systems this clause actually entered
    quiet        suppress the printed summary

    Returns a list of the file paths written.
    """
    os.makedirs(output_dir, exist_ok=True)

    result = analyse_text(sentence)
    stem = _slug(sentence)
    written = []

    if not quiet:
        print(f"\n{sentence}")
        print(
            f"{result['summary']['clause_count']} clause(s), "
            f"{result['summary']['nexus_count']} nexus(es), "
            f"all valid: {result['summary']['all_selections_valid']}"
        )

    multi = len(result["clauses"]) > 1

    for clause in result["clauses"]:
        for network_key in networks:
            selection = _selection_for(clause, network_key)
            if selection is None:
                continue                      # non-finite clause has no mood

            title = clause["text"] if multi else sentence
            svg = render_network(
                NETWORKS[network_key],
                selection,
                only_entered=only_entered,
                title=f"{title}  —  {network_key.upper()}",
            )

            suffix = f"_{clause['clause_id']}" if multi else ""
            path = os.path.join(output_dir, f"{stem}{suffix}_{network_key}.svg")
            with open(path, "w", encoding="utf-8") as f:
                f.write(svg)
            written.append(path)

            if png:
                png_path = _to_png(path)
                if png_path:
                    written.append(png_path)
                elif not quiet:
                    print("  (PNG skipped — run: pip install cairosvg)")

            if not quiet:
                print(f"  {clause['clause_id']} [{clause['status']}] "
                      f"{network_key}: {path}")

    if not quiet and result["nexuses"]:
        for n in result["nexuses"]:
            print(f"  nexus {n['notation']['primary']} … "
                  f"{n['notation']['secondary']}  ({n['reason']})")

    return written


def draw_all(sentence, **kwargs):
    """Draw transitivity, theme and mood for a sentence."""
    return draw(sentence, networks=("transitivity", "theme", "mood"), **kwargs)


# ---------------------------------------------------------------------------
# Command line
# ---------------------------------------------------------------------------

def _main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Draw SFL system networks for a sentence."
    )
    parser.add_argument("sentence", help="the sentence to analyse")
    parser.add_argument(
        "-n", "--networks", nargs="+", default=["transitivity"],
        choices=["transitivity", "theme", "mood"],
        help="which networks to draw (default: transitivity)",
    )
    parser.add_argument("-a", "--all", action="store_true",
                        help="draw all three networks")
    parser.add_argument("-o", "--output", default=OUTPUT_DIR,
                        help="output directory (default: output)")
    parser.add_argument("--png", action="store_true",
                        help="also write PNG files")
    parser.add_argument("--full", action="store_true",
                        help="draw the whole network, not just entered systems")

    args = parser.parse_args()
    networks = ("transitivity", "theme", "mood") if args.all else tuple(args.networks)

    draw(
        args.sentence,
        networks=networks,
        output_dir=args.output,
        png=args.png,
        only_entered=not args.full,
    )


if __name__ == "__main__":
    _main()