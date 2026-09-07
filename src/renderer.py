"""
System network renderer.

Draws a system network as SVG in the standard IFG notation:

  - left to right = increasing delicacy
  - square bracket = a choice between alternatives (disjunction)
  - brace          = simultaneous systems (conjunction)
  - the selected path is highlighted; unselected terms are greyed

Layout is computed here rather than in the browser, so the output is a
self-contained SVG string that can be dropped into Streamlit, an HTML
page, or saved to a file.
"""

from html import escape

from src.conditions import referenced_features
from src.traversal import feature_index, is_satisfied


# --- geometry --------------------------------------------------------------

ROW_HEIGHT = 30          # vertical space for one term
COL_WIDTH = 210          # horizontal space for one delicacy level
BRACKET_GAP = 14         # distance from entry point to the bracket
STUB = 12                # short line from bracket to term text
PAD_X = 20
PAD_Y = 20
SYSTEM_LABEL_DY = -10    # system name sits just above its bracket
SYSTEM_GAP = 26          # blank space below each system, for the next label

# --- colours ---------------------------------------------------------------

SELECTED = "#1f4e79"
UNSELECTED = "#9aa5b1"
LINE = "#5b6b7c"
LABEL = "#33475b"
BACKGROUND = "#ffffff"


# ---------------------------------------------------------------------------
# Structure
# ---------------------------------------------------------------------------

def systems_entered_by(network, feature_id, shown):
    """Systems whose entry condition mentions this feature."""
    return [
        s for s in shown
        if feature_id in referenced_features(s.entry)
    ]


def root_systems(network, shown):
    """Systems with no feature dependency — entered for every instance."""
    return [s for s in shown if not referenced_features(s.entry)]


def visible_systems(network, selected, only_entered=True):
    """
    Which systems to draw.

    By default only systems actually entered by this selection, so the
    diagram shows the choices that were live rather than the whole grammar.
    """
    if not only_entered:
        return list(network.systems)
    return [s for s in network.systems if is_satisfied(s.entry, selected)]


# ---------------------------------------------------------------------------
# Height calculation (bottom-up)
# ---------------------------------------------------------------------------

def group_height(network, systems, shown, cache):
    return sum(system_height(network, s, shown, cache) for s in systems)


def system_height(network, system, shown, cache):
    """Vertical space this system and everything to its right needs."""
    if system.id in cache:
        return cache[system.id]

    total = 0
    for term in system.terms:
        children = systems_entered_by(network, term.id, shown)
        if children:
            total += max(ROW_HEIGHT, group_height(network, children, shown, cache))
        else:
            total += ROW_HEIGHT

    total += SYSTEM_GAP          # room for the next system's label
    cache[system.id] = total
    return total


# ---------------------------------------------------------------------------
# Drawing
# ---------------------------------------------------------------------------

def _line(x1, y1, x2, y2, colour=LINE, width=1.2):
    return (
        f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
        f'stroke="{colour}" stroke-width="{width}" stroke-linecap="round"/>'
    )


def _text(x, y, content, colour=LABEL, size=13, weight="normal", anchor="start"):
    return (
        f'<text x="{x:.1f}" y="{y:.1f}" fill="{colour}" font-size="{size}" '
        f'font-weight="{weight}" text-anchor="{anchor}" '
        f'font-family="Segoe UI, Helvetica, Arial, sans-serif">'
        f'{escape(content)}</text>'
    )


def _bracket(x, y_top, y_bottom, colour=LINE):
    """A square bracket: vertical line with short stubs at each end."""
    return (
        f'<path d="M {x + 5:.1f},{y_top:.1f} L {x:.1f},{y_top:.1f} '
        f'L {x:.1f},{y_bottom:.1f} L {x + 5:.1f},{y_bottom:.1f}" '
        f'fill="none" stroke="{colour}" stroke-width="1.4" stroke-linejoin="round"/>'
    )


def _brace(x, y_top, y_bottom, colour=LINE):
    """A curly brace for simultaneous systems."""
    mid = (y_top + y_bottom) / 2
    return (
        f'<path d="M {x + 6:.1f},{y_top:.1f} '
        f'Q {x:.1f},{y_top:.1f} {x:.1f},{y_top + 8:.1f} '
        f'L {x:.1f},{mid - 6:.1f} Q {x:.1f},{mid:.1f} {x - 5:.1f},{mid:.1f} '
        f'Q {x:.1f},{mid:.1f} {x:.1f},{mid + 6:.1f} '
        f'L {x:.1f},{y_bottom - 8:.1f} Q {x:.1f},{y_bottom:.1f} '
        f'{x + 6:.1f},{y_bottom:.1f}" '
        f'fill="none" stroke="{colour}" stroke-width="1.4"/>'
    )


# ---------------------------------------------------------------------------
# Placement
# ---------------------------------------------------------------------------

def place_group(network, systems, shown, selected, x, y_top, cache, out):
    """
    Draw a group of systems hanging off the same entry point.

    More than one means they are simultaneous, so a brace is drawn.
    Returns the total height consumed.
    """
    total = group_height(network, systems, shown, cache)

    if len(systems) > 1:
        out.append(_brace(x - BRACKET_GAP + 4, y_top + 6,
                          y_top + total - SYSTEM_GAP - 6))

    y = y_top
    for system in systems:
        h = system_height(network, system, shown, cache)
        place_system(network, system, shown, selected, x, y, cache, out)
        y += h

    return total


def place_system(network, system, shown, selected, x, y_top, cache, out):
    """Draw one system: its label, its bracket, and its terms."""
    height = system_height(network, system, shown, cache)
    terms_height = height - SYSTEM_GAP
    y_bottom = y_top + terms_height

    entered = is_satisfied(system.entry, selected)
    bracket_colour = LINE if entered else UNSELECTED

    # entry line and bracket
    out.append(_line(x - BRACKET_GAP, y_top + terms_height / 2, x,
                     y_top + terms_height / 2, bracket_colour))
    out.append(_bracket(x, y_top + 6, y_bottom - 6, bracket_colour))

    # system name above the bracket
    out.append(_text(x + 2, y_top + SYSTEM_LABEL_DY, system.name,
                     colour=LABEL, size=10.5, weight="600"))

    # terms
    y = y_top
    for term in system.terms:
        children = systems_entered_by(network, term.id, shown)
        block = (
            max(ROW_HEIGHT, group_height(network, children, shown, cache))
            if children else ROW_HEIGHT
        )
        term_y = y + block / 2
        chosen = term.id in selected

        colour = SELECTED if chosen else UNSELECTED
        weight = "700" if chosen else "normal"

        out.append(_line(x, term_y, x + STUB, term_y, colour,
                         width=2.0 if chosen else 1.0))
        out.append(_text(x + STUB + 6, term_y + 4, term.name, colour, 13, weight))

        if children:
            label_width = 8 + len(term.name) * 7
            child_x = x + COL_WIDTH
            out.append(_line(x + STUB + label_width, term_y,
                             child_x - BRACKET_GAP, term_y,
                             LINE if chosen else UNSELECTED,
                             width=1.6 if chosen else 0.9))
            place_group(network, children, shown, selected, child_x, y, cache, out)

        y += block


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def _render_body(network, selected, only_entered=True, y_offset=0):
    """
    Draw one network's elements.

    Returns (elements, width, height) so several networks can be stacked
    into a single SVG.
    """
    shown = visible_systems(network, selected, only_entered)
    if not shown:
        return [], 360, ROW_HEIGHT

    cache = {}
    roots = root_systems(network, shown)
    if not roots:
        roots = shown[:1]

    out = []
    x0 = PAD_X + BRACKET_GAP
    height = place_group(network, roots, shown, selected, x0, y_offset, cache, out)

    max_delicacy = _max_depth(network, roots, shown)
    width = PAD_X * 2 + BRACKET_GAP + (max_delicacy + 1) * COL_WIDTH
    return out, width, height


def _features_of(selection):
    """Accept a SelectionExpression or a plain set of feature ids."""
    if hasattr(selection, "features"):
        selected = set(selection.features)
        for sub in getattr(selection, "sub_selections", []):
            selected |= set(sub.features)
        return selected
    return set(selection)


def _svg(elements, width, height):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width:.0f}" '
        f'height="{height:.0f}" viewBox="0 0 {width:.0f} {height:.0f}">'
        f'<rect width="100%" height="100%" fill="{BACKGROUND}"/>'
        + "".join(elements) + "</svg>"
    )


def render_network(network, selection, only_entered=True, title=None):
    """Render one network as an SVG string, with `selection` highlighted."""
    selected = _features_of(selection)

    y0 = PAD_Y + (44 if title else 14)
    elements, width, height = _render_body(network, selected, only_entered,
                                           y_offset=y0)
    if not elements:
        return _empty_svg("No systems entered by this selection.")

    header = []
    if title:
        header.append(_text(PAD_X, PAD_Y + 6, title, colour=SELECTED,
                            size=15, weight="700"))

    return _svg(header + elements, width, y0 + height + PAD_Y)


def render_combined(sections, title=None, only_entered=True):
    """
    Stack several networks into one SVG.

    `sections` is a list of (heading, network, selection) triples.
    Sections whose selection is None are skipped.
    """
    elements = []
    width = 0
    y = PAD_Y + (46 if title else 14)

    if title:
        elements.append(_text(PAD_X, PAD_Y + 8, title, colour=SELECTED,
                              size=16, weight="700"))

    for heading, network, selection in sections:
        if selection is None:
            continue
        selected = _features_of(selection)

        elements.append(_text(PAD_X, y, heading, colour=SELECTED,
                              size=12.5, weight="700"))
        elements.append(_line(PAD_X, y + 7, PAD_X + 240, y + 7,
                              colour="#d5dde5", width=1))
        y += 26

        section_elements, section_width, section_height = _render_body(
            network, selected, only_entered, y_offset=y
        )
        if not section_elements:
            elements.append(_text(PAD_X + 12, y + 14, "no systems entered",
                                  colour=UNSELECTED, size=12))
            y += 40
            continue

        elements.extend(section_elements)
        width = max(width, section_width)
        y += section_height + 24

    if not elements:
        return _empty_svg("Nothing to draw.")

    return _svg(elements, max(width, 420), y + PAD_Y)


def _max_depth(network, systems, shown, depth=0):
    best = depth
    for system in systems:
        for term in system.terms:
            children = systems_entered_by(network, term.id, shown)
            if children:
                best = max(best, _max_depth(network, children, shown, depth + 1))
    return best


def _empty_svg(message):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="420" height="60" '
        f'viewBox="0 0 420 60"><rect width="100%" height="100%" fill="{BACKGROUND}"/>'
        f'{_text(16, 34, message, colour=UNSELECTED)}</svg>'
    )


def render_to_file(network, selection, path, only_entered=True, title=None):
    """Write the SVG to disk."""
    svg = render_network(network, selection, only_entered, title)
    with open(path, "w", encoding="utf-8") as f:
        f.write(svg)
    return path


def render_text_summary(network, selection):
    """
    Plain-text fallback: the systems entered and the term chosen in each.
    Useful in a terminal, and as an accessible alternative to the diagram.
    """
    selected = (
        selection.features if hasattr(selection, "features") else set(selection)
    )
    index = feature_index(network)
    lines = []
    for system in network.systems:
        if not is_satisfied(system.entry, selected):
            continue
        chosen = [t.name for t in system.terms if t.id in selected]
        others = [t.name for t in system.terms if t.id not in selected]
        mark = chosen[0] if chosen else "(nothing chosen)"
        alt = f"   [not: {', '.join(others)}]" if others else ""
        lines.append(f"{system.name:28} {mark}{alt}")
    return "\n".join(lines)