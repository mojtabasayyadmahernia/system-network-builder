from src.segmenter import analyse
from src.loader import load_network
from src.model import SelectionExpression
from src.validator import validate

network = load_network("clause_complex")

SAMPLES = [
    "The lion caught the tourist because it was hungry.",
    "He came in and sat down.",
    "She said that he had left.",
    "She thought that he had left.",
    "John, who left early, was tired.",
    "He left when the rain stopped.",
    "She was tired but she kept working.",
]


def test_every_nexus_is_valid():
    """Every nexus we build must pass the Phase 1 validator."""
    for text in SAMPLES:
        clauses, nexuses = analyse(text)
        for nexus in nexuses:
            expr = SelectionExpression(rank="clause-nexus", features=nexus.features)
            result = validate(network, expr)
            assert result.valid, f"{text}\n{nexus.features}\n{result.errors}"


def test_embedded_clauses_never_in_nexuses():
    """An embedded clause must never appear in a nexus."""
    for text in SAMPLES + ["The man who left early was tired.",
                           "That he left surprised me."]:
        clauses, nexuses = analyse(text)
        embedded = {c.id for c in clauses if c.status == "embedded"}
        for nexus in nexuses:
            assert nexus.primary_clause_id not in embedded
            assert nexus.secondary_clause_id not in embedded


def test_causal_link_detected():
    clauses, nexuses = analyse("He left because he was tired.")
    assert len(nexuses) == 1
    assert "enh-causal" in nexuses[0].features
    assert "hypotaxis" in nexuses[0].features


def test_projection_detected():
    clauses, nexuses = analyse("She said that he had left.")
    assert len(nexuses) == 1
    assert "projection" in nexuses[0].features
    assert "locution" in nexuses[0].features


def test_idea_vs_locution():
    _, said = analyse("She said that he had left.")
    _, thought = analyse("She thought that he had left.")
    assert "locution" in said[0].features
    assert "idea" in thought[0].features


def test_defining_relative_makes_no_nexus():
    clauses, nexuses = analyse("The man who left early was tired.")
    assert len(nexuses) == 0


import json
from pathlib import Path
from src.segmenter import analyse

GOLD = json.loads(
    Path("tests/fixtures/gold_segmentation.json").read_text(encoding="utf-8")
)


def test_report_accuracy():
    """Not a pass/fail test — prints how well the segmenter is doing."""
    clause_count_right = 0
    status_right = 0
    status_total = 0
    nexus_count_right = 0

    for case in GOLD:
        clauses, nexuses = analyse(case["text"])

        if len(clauses) == len(case["clauses"]):
            clause_count_right += 1

        for actual, expected in zip(clauses, case["clauses"]):
            status_total += 1
            if actual.status == expected["status"]:
                status_right += 1

        if len(nexuses) == case["nexus_count"]:
            nexus_count_right += 1

    n = len(GOLD)
    print(f"\nClause count correct: {clause_count_right}/{n}")
    print(f"Status correct:       {status_right}/{status_total}")
    print(f"Nexus count correct:  {nexus_count_right}/{n}")