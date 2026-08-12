"""Entry-condition evaluation for system networks."""

from src.model import Condition


def is_satisfied(cond: Condition, selected: set[str]) -> bool:
    """
    Does `selected` satisfy this entry condition?

    A 'root' condition is satisfied unconditionally — the system is entered
    for every instance of its rank.
    """
    if cond.op == "root":
        return True
    if cond.op == "feature":
        return cond.value in selected
    if cond.op == "and":
        return all(is_satisfied(o, selected) for o in cond.operands)
    if cond.op == "or":
        return any(is_satisfied(o, selected) for o in cond.operands)
    raise ValueError(f"Unknown condition op: {cond.op!r}")


def referenced_features(cond: Condition) -> set[str]:
    """Every feature id this condition depends on. Used for cycle detection."""
    if cond.op == "root":
        return set()
    if cond.op == "feature":
        return {cond.value}
    return set().union(*(referenced_features(o) for o in cond.operands))