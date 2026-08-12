from src.loader import load_network
from src.model import SelectionExpression
from src.validator import validate, Rule

transitivity = load_network("transitivity")


def check(features, rank="clause"):
    return validate(transitivity, SelectionExpression(rank=rank, features=set(features)))


def test_valid_material_clause():
    r = check(["material", "transformative", "effective", "non-circumstantial-clause"])
    assert r.valid, r.errors


def test_unknown_feature():
    r = check(["material", "not-a-real-feature", "effective", "non-circumstantial-clause"])
    assert not r.valid
    assert Rule.UNKNOWN_FEATURE in {e.rule for e in r.errors}


def test_entry_unsatisfied():
    # 'transformative' needs 'material'
    r = check(["transformative", "effective", "non-circumstantial-clause"])
    assert not r.valid
    assert Rule.ENTRY_UNSATISFIED in {e.rule for e in r.errors}


def test_mutual_exclusivity():
    r = check(["relational", "attributive", "identifying", "intensive",
               "middle", "non-circumstantial-clause"])
    assert not r.valid
    assert Rule.MUTUAL_EXCLUSIVITY in {e.rule for e in r.errors}


def test_incomplete():
    r = check(["material"])
    assert not r.valid
    assert Rule.INCOMPLETE in {e.rule for e in r.errors}