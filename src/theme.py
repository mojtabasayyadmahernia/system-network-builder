"""
THEME analysis.

For each clause, works out:
  - its MOOD (declarative, interrogative, imperative)
  - where the Theme ends and the Rheme begins
  - what the Theme is made of (textual / interpersonal / topical)
"""

from src.segmenter import nlp, FINITE_TAGS


# ---------------------------------------------------------------------------
# Word lists
# ---------------------------------------------------------------------------

# Words that can start a question
WH_WORDS = {
    "who", "whom", "whose", "what", "which",
    "when", "where", "why", "how",
}

# Textual: small words that link back to the previous text
CONTINUATIVES = {
    "well", "oh", "now", "yes", "no", "anyway", "right", "okay", "ok", "so",
}

CONJUNCTIVE_ADJUNCTS = {
    "however", "therefore", "moreover", "nevertheless", "furthermore",
    "thus", "hence", "consequently", "meanwhile", "otherwise",
    "besides", "accordingly", "similarly", "conversely", "indeed",
}

# Interpersonal: words showing the speaker's attitude or judgement
MODAL_ADJUNCTS = {
    "probably", "certainly", "surely", "obviously", "clearly", "possibly",
    "perhaps", "maybe", "definitely", "presumably", "apparently",
    "frankly", "honestly", "unfortunately", "fortunately", "admittedly",
    "hopefully", "arguably", "supposedly", "evidently", "undoubtedly",
    "usually", "always", "often", "sometimes", "never",
}


# ---------------------------------------------------------------------------
# MOOD
# ---------------------------------------------------------------------------

def detect_mood(clause, doc):
    """
    Work out the mood of a clause.

    Returns (features, confidence, reason).
    Non-finite clauses have no mood, so they return an empty set.
    """
    if not clause.finite:
        return set(), 1.0, "non-finite clause — no mood"

    head = doc[clause.head_index]
    span = [doc[i] for i in clause.token_indices]

    # Find the Subject, if there is one
    subject = next(
        (t for t in head.children if t.dep_ in ("nsubj", "nsubjpass")),
        None,
    )

    # --- imperative: "let's ..." / "let me ..." ---
    if head.lemma_.lower() == "let":
        opening = " ".join(t.text.lower() for t in span[:3])
        if "'s" in opening or " us" in opening:
            return {"imperative", "suggestive"}, 0.9, "'let's' — suggestive imperative"
        return {"imperative", "oblative"}, 0.85, "'let me' — oblative imperative"

    # --- imperative: no Subject, base-form verb ("Catch it!") ---
    if subject is None and head.tag_ == "VB":
        return {"imperative", "jussive"}, 0.85, "no Subject, base-form verb"

    # --- WH-interrogative: starts with a wh-word ---
    first = next((t for t in span if not t.is_punct), None)
    if (
        first is not None
        and first.text.lower() in WH_WORDS
        and clause.dep_to_parent != "relcl"
    ):
        return (
            {"indicative", "interrogative", "wh-interrogative"},
            0.85,
            f"clause-initial '{first.text}'",
        )

    # --- polar interrogative: Finite comes before the Subject ---
    if subject is not None:
        finite_auxes = [
            t for t in span if t.pos_ == "AUX" and t.tag_ in FINITE_TAGS
        ]
        if finite_auxes and finite_auxes[0].i < subject.i:
            return (
                {"indicative", "interrogative", "polar"},
                0.85,
                "Finite before Subject",
            )

    # --- declarative: the default ---
    return {"indicative", "declarative"}, 0.9, "Subject before Finite"


# ---------------------------------------------------------------------------
# THEME
# ---------------------------------------------------------------------------

def find_theme(clause, doc, mood_features):
    """
    Split a clause into Theme and Rheme.

    Walks left to right, collecting textual and interpersonal elements,
    and stops at the first topical (experiential) element.
    """
    head = doc[clause.head_index]
    span = [doc[i] for i in clause.token_indices]
    clause_indices = set(clause.token_indices)

    subject = next(
        (t for t in head.children if t.dep_ in ("nsubj", "nsubjpass")),
        None,
    )

    textual = []
    interpersonal = []
    topical = []
    topical_head = None

    for token in span:
        if token.is_punct:
            continue

        word = token.text.lower()

        # --- textual? ---
        is_first = not textual and not interpersonal
        if (
            token.dep_ in ("cc", "mark")
            or word in CONJUNCTIVE_ADJUNCTS
            or (word in CONTINUATIVES and is_first)
        ):
            textual.append(token)
            continue

        # --- interpersonal? ---
        if word in MODAL_ADJUNCTS:
            interpersonal.append(token)
            continue

        # the Finite in a yes/no question is interpersonal Theme
        if (
            "polar" in mood_features
            and token.pos_ == "AUX"
            and (subject is None or token.i < subject.i)
        ):
            interpersonal.append(token)
            continue

        # --- topical: take the whole phrase, then stop ---
        topical_head = token
        while (
            topical_head.head != head
            and topical_head.head != topical_head
            and topical_head.head.i in clause_indices
        ):
            topical_head = topical_head.head

        topical = sorted(
            (t for t in topical_head.subtree if t.i in clause_indices),
            key=lambda t: t.i,
        )
        break

    theme = sorted(set(textual + interpersonal + topical), key=lambda t: t.i)
    theme_indices = {t.i for t in theme}
    rheme = [t for t in span if t.i not in theme_indices and not t.is_punct]

    return {
        "textual": textual,
        "interpersonal": interpersonal,
        "topical": topical,
        "topical_head": topical_head,
        "theme": theme,
        "rheme": rheme,
        "theme_text": " ".join(t.text for t in theme),
        "rheme_text": " ".join(t.text for t in rheme),
    }


def topical_type(topical_head):
    """
    What kind of thing is the topical Theme?

    participant   — a person or thing:      "The lion caught it"
    circumstance  — a time, place, manner:  "On Saturday they left"
    process       — an action:              "Catch the tourist!"
    """
    if topical_head is None:
        return None, 0.0, "no topical element found"

    if topical_head.pos_ in ("NOUN", "PROPN", "PRON"):
        return "topical-participant", 0.9, f"'{topical_head.text}' is a nominal"

    if topical_head.pos_ in ("VERB", "AUX"):
        return "topical-process", 0.9, f"'{topical_head.text}' is a verb"

    if topical_head.pos_ in ("ADP", "ADV") or topical_head.dep_ in (
        "prep", "advmod", "npadvmod"
    ):
        return "topical-circumstance", 0.85, f"'{topical_head.text}' is adverbial"

    return "topical-participant", 0.4, f"'{topical_head.text}' — defaulting to participant"
