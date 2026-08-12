import json
from pathlib import Path
import pytest

from src.loader import load_network
from src.model import SelectionExpression
from src.validator import validate

FIXTURES = json.loads(
    Path("tests/fixtures/gold_selections.json").read_text(encoding="utf-8")
)

NETWORK_FILES = {
    "TRANSITIVITY": "transitivity",
    "THEME": "theme",
    "MOOD": "mood",
    "CLAUSE COMPLEX": "clause_complex",
}


@pytest.mark.parametrize("case", FIXTURES, ids=lambda c: c.get("clause", "?")[:40])
def test_gold_selection(case):
    network = load_network(NETWORK_FILES[case["network"]])

    subs = [
        SelectionExpression(rank=s["rank"], features=set(s["features"]))
        for s in case.get("sub_selections", [])
    ]
    expr = SelectionExpression(
        rank=case["rank"],
        features=set(case["features"]),
        sub_selections=subs,
    )

    result = validate(network, expr)
    assert result.valid == case["expect_valid"], result.errors

    if not case["expect_valid"]:
        assert case["expect_error"] in {e.rule.value for e in result.errors}