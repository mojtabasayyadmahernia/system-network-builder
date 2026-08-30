from src.segmenter import nlp, segment
from src.theme import detect_mood


def mood_of(text):
    doc = nlp(text)
    clause = segment(text)[0]
    features, _, _ = detect_mood(clause, doc)
    return features


def test_declarative():
    assert "declarative" in mood_of("The lion caught the tourist.")


def test_polar_interrogative():
    assert "polar" in mood_of("Did the lion catch the tourist?")


def test_wh_interrogative():
    assert "wh-interrogative" in mood_of("Who caught the tourist?")


def test_jussive_imperative():
    assert "jussive" in mood_of("Catch the tourist!")


def test_suggestive_imperative():
    assert "suggestive" in mood_of("Let's catch the tourist.")


def test_relative_who_is_not_a_question():
    """'The man who left' must not be read as a wh-interrogative."""
    doc = nlp("The man who left early was tired.")
    clauses = segment("The man who left early was tired.")
    rel = [c for c in clauses if c.dep_to_parent == "relcl"][0]
    features, _, _ = detect_mood(rel, doc)
    assert "wh-interrogative" not in features


def test_non_finite_has_no_mood():
    doc = nlp("She wanted to leave.")
    clauses = segment("She wanted to leave.")
    non_finite = [c for c in clauses if not c.finite]
    if non_finite:
        features, _, _ = detect_mood(non_finite[0], doc)
        assert features == set()