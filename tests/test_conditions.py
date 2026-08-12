import pytest
from src.model import Condition
from src.conditions import is_satisfied


def test_root_always_satisfied():
    assert is_satisfied(Condition(op="root"), set())


def test_feature_present():
    c = Condition(op="feature", value="material")
    assert is_satisfied(c, {"material", "effective"})
    assert not is_satisfied(c, {"mental"})


def test_and_requires_all():
    c = Condition(op="and", operands=[
        Condition(op="feature", value="mental"),
        Condition(op="feature", value="effective"),
    ])
    assert is_satisfied(c, {"mental", "effective"})
    assert not is_satisfied(c, {"mental"})


def test_unknown_op_raises():
    with pytest.raises(ValueError):
        is_satisfied(Condition(op="xor", value="x"), set())