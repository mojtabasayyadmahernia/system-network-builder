from src.segmenter import segment


def test_simple_sentence_one_clause():
    clauses = segment("The lion caught the tourist.")
    assert len(clauses) == 1
    assert clauses[0].finite is True


def test_two_clauses():
    clauses = segment("The lion caught the tourist because it was hungry.")
    assert len(clauses) == 2


def test_subordinate_not_swallowed():
    """The main clause must not contain the subordinate clause's words."""
    clauses = segment("The lion caught the tourist because it was hungry.")
    main = [c for c in clauses if c.dep_to_parent is None][0]
    assert "hungry" not in main.text


def test_parent_recorded():
    clauses = segment("The lion caught the tourist because it was hungry.")
    sub = [c for c in clauses if c.dep_to_parent == "advcl"][0]
    assert sub.parent_clause_id is not None


def test_non_finite_detected():
    clauses = segment("She wanted to leave.")
    non_finite = [c for c in clauses if not c.finite]
    assert len(non_finite) >= 1


def test_coordinated_nouns_are_not_clauses():
    """'The lion and the tiger left' is ONE clause, not two."""
    clauses = segment("The lion and the tiger left.")
    assert len(clauses) == 1