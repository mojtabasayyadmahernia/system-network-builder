"""Querying the network graph."""

from src.model import Network, System
from src.conditions import is_satisfied, referenced_features


def feature_index(network: Network) -> dict[str, System]:
    """feature id -> the system it belongs to. Reverse index."""
    index = {}
    for system in network.systems:
        for term in system.terms:
            if term.id in index:
                raise ValueError(
                    f"Duplicate feature id {term.id!r} in "
                    f"{index[term.id].id} and {system.id}"
                )
            index[term.id] = system
    return index


def entered_systems(network: Network, selected: set[str]) -> list[System]:
    """Systems whose entry condition is satisfied by `selected`."""
    return [s for s in network.systems if is_satisfied(s.entry, selected)]


def chosen_in(system: System, selected: set[str]) -> list[str]:
    """Which terms of this system appear in `selected`. Should be 0 or 1."""
    return [t.id for t in system.terms if t.id in selected]


def available_choices(network: Network, selected: set[str]) -> list[System]:
    """Entered systems with nothing chosen yet — what still needs deciding."""
    return [
        s for s in entered_systems(network, selected)
        if not chosen_in(s, selected)
    ]


def simultaneous_groups(network: Network) -> list[list[System]]:
    """
    Systems sharing an entry condition are simultaneous (rendered with a brace).
    Derived, never declared.
    """
    groups: dict[str, list[System]] = {}
    for system in network.systems:
        key = system.entry.model_dump_json()
        groups.setdefault(key, []).append(system)
    return [g for g in groups.values() if len(g) > 1]


def check_acyclic(network: Network) -> None:
    """Raise if the system dependency graph contains a cycle."""
    index = feature_index(network)
    visiting, done = set(), set()

    def visit(system: System, path: list[str]):
        if system.id in done:
            return
        if system.id in visiting:
            raise ValueError(f"Cycle in network: {' -> '.join(path + [system.id])}")
        visiting.add(system.id)
        for feat in referenced_features(system.entry):
            parent = index.get(feat)
            if parent is None:
                raise ValueError(
                    f"System {system.id} entry references unknown feature {feat!r}"
                )
            visit(parent, path + [system.id])
        visiting.discard(system.id)
        done.add(system.id)

    for system in network.systems:
        visit(system, [])


def delicacy(network: Network, system: System) -> int:
    """
    Longest path from root to this system. Column position in the diagram.
    Root-entered systems are delicacy 0.
    """
    check_acyclic(network)
    index = feature_index(network)

    def depth(s: System) -> int:
        feats = referenced_features(s.entry)
        if not feats:
            return 0
        return 1 + max(depth(index[f]) for f in feats)

    return depth(system)