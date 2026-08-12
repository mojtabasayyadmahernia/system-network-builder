from enum import Enum
from pydantic import BaseModel

from src.model import Network, SelectionExpression
from src.conditions import is_satisfied
from src.traversal import feature_index, entered_systems, chosen_in


class Rule(str, Enum):
    UNKNOWN_FEATURE    = "unknown_feature"
    RANK_MISMATCH      = "rank_mismatch"
    ENTRY_UNSATISFIED  = "entry_condition_unsatisfied"
    MUTUAL_EXCLUSIVITY = "mutual_exclusivity"
    INCOMPLETE         = "incomplete"


class ValidationError(BaseModel):
    rule: Rule
    system_id: str | None = None
    features: list[str] = []
    message: str


class ValidationResult(BaseModel):
    valid: bool
    errors: list[ValidationError] = []
    entered_systems: list[str] = []
    unchosen_systems: list[str] = []


def validate(
    network: Network,
    expr: SelectionExpression,
    parent_features: set[str] | None = None,
) -> ValidationResult:
    parent_features = parent_features or set()
    index = feature_index(network)
    selected = expr.features
    errors: list[ValidationError] = []

    # Rule 1 — every feature exists in this network
    unknown = {f for f in selected if f not in index}
    for f in sorted(unknown):
        errors.append(ValidationError(
            rule=Rule.UNKNOWN_FEATURE, features=[f],
            message=f"Feature {f!r} is not defined in network {network.name}.",
        ))
    known = selected - unknown

    # Entry conditions are evaluated against this expression's own features
    # PLUS whatever the parent expression selected. An element-rank system
    # like CIRCUMSTANCE_TYPE is entered by a clause-rank feature
    # (circumstantial-clause), so the sub-selection must see it.
    context = known | parent_features

    # Rule 2 — feature rank must match the expression's declared rank
    for f in sorted(known):
        system = index[f]
        if system.rank != expr.rank:
            errors.append(ValidationError(
                rule=Rule.RANK_MISMATCH, system_id=system.id, features=[f],
                message=(
                    f"Feature {f!r} is {system.rank}-rank but the expression "
                    f"declares {expr.rank}-rank."
                ),
            ))

    # Rule 3 — each selected feature's system must actually be entered
    unsatisfied_systems = set()
    for f in sorted(known):
        system = index[f]
        if not is_satisfied(system.entry, context):
            unsatisfied_systems.add(system.id)
            errors.append(ValidationError(
                rule=Rule.ENTRY_UNSATISFIED, system_id=system.id, features=[f],
                message=(
                    f"{f!r} was selected but its system {system.id} is not "
                    f"entered by the other selections."
                ),
            ))

    # Rule 4 — at most one term per system
    for system in network.systems:
        chosen = chosen_in(system, known)
        if len(chosen) > 1:
            errors.append(ValidationError(
                rule=Rule.MUTUAL_EXCLUSIVITY, system_id=system.id, features=chosen,
                message=(
                    f"System {system.id} is a choice between alternatives, but "
                    f"{len(chosen)} were selected: {', '.join(chosen)}."
                ),
            ))

    # Rule 5 — every entered system at THIS rank must have a term chosen
    entered = entered_systems(network, context)
    unchosen = []
    for system in entered:
        if system.rank != expr.rank:
            continue
        if system.id in unsatisfied_systems:
            continue
        if not chosen_in(system, known):
            unchosen.append(system.id)
            errors.append(ValidationError(
                rule=Rule.INCOMPLETE, system_id=system.id,
                message=f"System {system.id} is entered but no term was selected.",
            ))

    # Recurse into element-rank sub-selections, passing our context down
    for sub in expr.sub_selections:
        errors.extend(validate(network, sub, parent_features=context).errors)

    return ValidationResult(
        valid=not errors,
        errors=errors,
        entered_systems=[s.id for s in entered],
        unchosen_systems=unchosen,
    )