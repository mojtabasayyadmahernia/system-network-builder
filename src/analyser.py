"""
Integration layer.

Ties segmentation, MOOD, THEME and TRANSITIVITY together into one
analysis per clause, and one result object per text.

Everything returned here is JSON-serialisable, so it can go straight
into an API response.
"""

from src.loader import load_network
from src.model import SelectionExpression
from src.segmenter import nlp, segment, build_nexuses
from src.theme import analyse_theme
from src.transitivity import analyse_transitivity
from src.validator import validate

try:
    from src.notation import nexus_notation
except ImportError:                                    # notation.py not present
    def nexus_notation(features):
        return ("?", "?")


# Networks are loaded once and reused
NETWORKS = {
    "transitivity": load_network("transitivity"),
    "theme": load_network("theme"),
    "mood": load_network("mood"),
    "clause_complex": load_network("clause_complex"),
}


def _selection_to_dict(selection: SelectionExpression, network_key: str):
    """Serialise a selection expression and validate it in one step."""
    network = NETWORKS[network_key]
    result = validate(network, selection)
    return {
        "rank": selection.rank,
        "features": sorted(selection.features),
        "sub_selections": [
            {"rank": s.rank, "features": sorted(s.features)}
            for s in selection.sub_selections
        ],
        "valid": result.valid,
        "errors": [
            {"rule": e.rule.value, "system": e.system_id, "message": e.message}
            for e in result.errors
        ],
    }


def analyse_clause(clause, doc):
    """
    Full analysis of one clause: mood, theme, transitivity.

    Returns a JSON-serialisable dict.
    """
    theme = analyse_theme(clause, doc)
    transitivity = analyse_transitivity(clause, doc)

    mood_block = None
    if theme["mood_features"]:
        mood_block = {
            "features": sorted(theme["mood_features"]),
            "reason": theme["mood_reason"],
            "selection": _selection_to_dict(theme["mood_selection"], "mood"),
        }

    return {
        "clause_id": clause.id,
        "text": clause.text,
        "status": clause.status,
        "status_reason": clause.status_reason,
        "status_confidence": clause.status_confidence,
        "finite": clause.finite,
        "parent_clause_id": clause.parent_clause_id,

        "mood": mood_block,

        "theme": {
            "theme_text": theme["theme_text"],
            "rheme_text": theme["rheme_text"],
            "textual": [t.text for t in theme["parts"]["textual"]],
            "interpersonal": [t.text for t in theme["parts"]["interpersonal"]],
            "topical": [t.text for t in theme["parts"]["topical"]],
            "is_multiple": theme["is_multiple"],
            "confidence": theme["confidence"],
            "evidence": theme["evidence"],
            "selection": _selection_to_dict(theme["selection"], "theme"),
        },

        "transitivity": {
            "process": transitivity["process"],
            "process_lemma": transitivity["process_lemma"],
            "participants": transitivity["participants"],
            "circumstances": transitivity["circumstances"],
            "confidence": transitivity["confidence"],
            "evidence": transitivity["evidence"],
            "selection": _selection_to_dict(transitivity["selection"], "transitivity"),
        },

        # the lowest confidence anywhere in this clause's analysis
        "confidence": min(theme["confidence"], transitivity["confidence"]),
    }


def analyse_nexus(nexus):
    """Serialise a nexus, with its IFG notation and validation result."""
    selection = SelectionExpression(rank="clause-nexus", features=nexus.features)
    try:
        primary_symbol, secondary_symbol = nexus_notation(nexus.features)
    except ValueError:
        primary_symbol, secondary_symbol = "?", "?"

    return {
        "id": nexus.id,
        "primary_clause_id": nexus.primary_clause_id,
        "secondary_clause_id": nexus.secondary_clause_id,
        "notation": {"primary": primary_symbol, "secondary": secondary_symbol},
        "confidence": nexus.confidence,
        "reason": nexus.reason,
        "selection": _selection_to_dict(selection, "clause_complex"),
    }


def analyse_text(text: str):
    """
    Analyse a whole text.

    Returns:
        {
          "text": ...,
          "clauses": [ ... ],
          "nexuses": [ ... ],
          "summary": { counts and lowest confidence }
        }
    """
    doc = nlp(text)
    clauses = segment(text)
    nexuses = build_nexuses(clauses, doc)

    clause_blocks = [analyse_clause(c, doc) for c in clauses]
    nexus_blocks = [analyse_nexus(n) for n in nexuses]

    all_valid = all(
        b["theme"]["selection"]["valid"]
        and b["transitivity"]["selection"]["valid"]
        for b in clause_blocks
    ) and all(n["selection"]["valid"] for n in nexus_blocks)

    confidences = [b["confidence"] for b in clause_blocks]

    return {
        "text": text,
        "clauses": clause_blocks,
        "nexuses": nexus_blocks,
        "summary": {
            "clause_count": len(clause_blocks),
            "ranking_clauses": sum(1 for b in clause_blocks if b["status"] == "ranking"),
            "embedded_clauses": sum(1 for b in clause_blocks if b["status"] == "embedded"),
            "nexus_count": len(nexus_blocks),
            "all_selections_valid": all_valid,
            "lowest_confidence": min(confidences) if confidences else None,
        },
    }