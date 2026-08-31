"""Tests for TRANSITIVITY analysis."""

from src.loader import load_network
from src.segmenter import nlp, segment
from src.transitivity import (
    analyse_transitivity, classify_process, find_circumstances,
    assess_agency, assign_participants,
)
from src.validator import validate

network = load_network("transitivity")


def first_clause(text):
    doc = nlp(text)
    return segment(text)[0], doc


def analysis_of(text):
    clause, doc = first_clause(text)
    return analyse_transitivity(clause, doc)


def features_of(text):
    return analysis_of(text)["selection"].features


def roles_of(text):
    return {p["role"] for p in analysis_of(text)["participants"]}


# --- Day 1: process type ---------------------------------------------------

def test_material_process():
    assert "material" in features_of("The lion caught the tourist.")


def test_mental_perceptive():
    f = features_of("Mary saw the bird.")
    assert "mental" in f and "perceptive" in f


def test_mental_cognitive():
    f = features_of("She knew the answer.")
    assert "mental" in f and "cognitive" in f


def test_mental_desiderative():
    f = features_of("He wanted a holiday.")
    assert "mental" in f and "desiderative" in f


def test_please_type_direction():
    f = features_of("The music pleased Mary.")
    assert "please-type" in f


def test_like_type_direction():
    f = features_of("Mary liked the music.")
    assert "like-type" in f


def test_relational_attributive():
    f = features_of("Sarah is happy.")
    assert "relational" in f and "attributive" in f


def test_relational_identifying():
    f = features_of("Sarah is the treasurer.")
    assert "relational" in f and "identifying" in f


def test_relational_possessive():
    f = features_of("Sarah has a car.")
    assert "relational" in f and "possessive" in f


def test_existential():
    assert "existential" in features_of("There was a storm.")


def test_verbal_process():
    assert "verbal" in features_of("She told the story.")


def test_behavioural_process():
    assert "behavioural" in features_of("He laughed.")


def test_creative_vs_transformative():
    assert "creative" in features_of("She wrote a poem.")
    assert "transformative" in features_of("She broke the vase.")


# --- Day 2: participants and agency ----------------------------------------

def test_actor_and_goal():
    assert roles_of("The lion caught the tourist.") == {"Actor", "Goal"}


def test_senser_and_phenomenon():
    assert roles_of("Mary saw the bird.") == {"Senser", "Phenomenon"}


def test_please_type_swaps_roles():
    """In 'The music pleased Mary', the Subject is the Phenomenon."""
    a = analysis_of("The music pleased Mary.")
    by_role = {p["role"]: p["text"] for p in a["participants"]}
    assert by_role["Phenomenon"] == "The music"
    assert by_role["Senser"] == "Mary"


def test_carrier_and_attribute():
    assert roles_of("Sarah is happy.") == {"Carrier", "Attribute"}


def test_token_and_value():
    assert roles_of("Sarah is the treasurer.") == {"Token", "Value"}


def test_sayer():
    assert "Sayer" in roles_of("She told the story.")


def test_existent():
    assert "Existent" in roles_of("There was a storm.")


def test_effective_with_object():
    assert "effective" in features_of("The lion caught the tourist.")


def test_middle_without_object():
    assert "middle" in features_of("The lion slept.")


# --- Day 3: circumstances --------------------------------------------------

def test_no_circumstance():
    assert "non-circumstantial-clause" in features_of("The lion caught the tourist.")


def test_location_circumstance():
    a = analysis_of("She ran in the park.")
    assert "circumstantial-clause" in a["selection"].features
    assert any(c["feature"] == "location" for c in a["circumstances"])


def test_manner_circumstance():
    a = analysis_of("She ran quickly.")
    assert any(c["feature"] == "manner" for c in a["circumstances"])


def test_two_circumstances_produce_two_sub_selections():
    """'Yesterday she ran quickly' has Location and Manner at once."""
    a = analysis_of("Yesterday she ran quickly.")
    assert len(a["circumstances"]) >= 2
    assert len(a["selection"].sub_selections) == len(a["circumstances"])


def test_negation_is_not_a_circumstance():
    a = analysis_of("She did not run.")
    texts = [c["text"].lower() for c in a["circumstances"]]
    assert "not" not in texts


# --- Day 4: validation against the Phase 1 network -------------------------

SAMPLES = [
    "The lion caught the tourist.",
    "Mary saw the bird.",
    "The music pleased Mary.",
    "Sarah is happy.",
    "Sarah is the treasurer.",
    "Sarah has a car.",
    "There was a storm.",
    "She told the story.",
    "He laughed.",
    "She wrote a poem.",
    "Yesterday she ran quickly.",
    "She ran in the park.",
]


def test_every_transitivity_selection_is_valid():
    """Every analysis must pass the Phase 1 validator."""
    for text in SAMPLES:
        a = analysis_of(text)
        result = validate(network, a["selection"])
        assert result.valid, f"{text}\n{sorted(a['selection'].features)}\n{result.errors}"


def test_evidence_recorded():
    for text in SAMPLES:
        a = analysis_of(text)
        assert a["evidence"], f"no evidence for: {text}"
        assert 0.0 <= a["confidence"] <= 1.0


def test_unknown_verb_gets_low_confidence():
    """A verb not in the lexicon should be flagged, not asserted."""
    a = analysis_of("She flumphed the widget.")
    assert a["confidence"] < 0.5