from src.loader import load_network
from src.traversal import (
    entered_systems, available_choices, simultaneous_groups, delicacy
)

transitivity = load_network("transitivity")


def by_id(system_id):
    return next(s for s in transitivity.systems if s.id == system_id)


def test_entered_systems_at_root():
    ids = {s.id for s in entered_systems(transitivity, set())}
    assert ids == {"PROCESS_TYPE", "AGENCY", "CIRCUMSTANTIATION"}


def test_material_opens_material_type():
    ids = {s.id for s in entered_systems(transitivity, {"material"})}
    assert "MATERIAL_TYPE" in ids
    assert "MENTAL_TYPE" not in ids


def test_available_choices_excludes_chosen():
    ids = {s.id for s in available_choices(transitivity, {"material", "effective"})}
    assert "PROCESS_TYPE" not in ids
    assert "MATERIAL_TYPE" in ids


def test_simultaneous_groups_found():
    groups = simultaneous_groups(transitivity)
    root_group = [g for g in groups if len(g) == 3][0]
    assert {s.id for s in root_group} == {"PROCESS_TYPE", "AGENCY", "CIRCUMSTANTIATION"}


def test_delicacy_levels():
    assert delicacy(transitivity, by_id("PROCESS_TYPE")) == 0
    assert delicacy(transitivity, by_id("MATERIAL_TYPE")) == 1