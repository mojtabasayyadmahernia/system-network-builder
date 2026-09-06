"""
THEME analysis.

For each clause, works out:
  - its MOOD (declarative, interrogative, imperative)
  - where the Theme ends and the Rheme begins
  - what the Theme is made of (textual / interpersonal / topical)
  - whether the Theme is marked or unmarked for its mood
  - the full THEME selection expression, ready for validation
"""

from src.model import SelectionExpression
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

# Dependency labels that mark an adverbial / circumstantial element
CIRCUMSTANTIAL_DEPS = {"prep", "advmod", "npadvmod", "advcl"}


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
# Finding the Theme
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

    if topical_head.pos_ in ("ADP", "ADV") or topical_head.dep_ in CIRCUMSTANTIAL_DEPS:
        return "topical-circumstance", 0.85, f"'{topical_head.text}' is adverbial"

    return "topical-participant", 0.4, f"'{topical_head.text}' — defaulting to participant"


# ---------------------------------------------------------------------------
# Markedness
# ---------------------------------------------------------------------------

def is_circumstantial(token):
    """Is this token the head of an adverbial or prepositional phrase?"""
    return token.pos_ in ("ADP", "ADV") or token.dep_ in CIRCUMSTANTIAL_DEPS


def assess_markedness(clause, doc, mood_features, parts):
    """
    Is the Theme the ordinary starting point for this mood, or has the
    writer fronted something unusual?

    Unmarked Theme by mood:
        declarative           Subject
        polar interrogative   Finite + Subject
        WH-interrogative      the WH-element
        imperative (jussive)  the Predicator
        imperative (let's)    'let's'

    Returns (features, confidence, reason).
    """
    head = doc[clause.head_index]
    topical = parts["topical"]
    topical_head = parts["topical_head"]

    if topical_head is None:
        return {"unmarked-theme"}, 0.2, "no topical element found — defaulted to unmarked"

    topical_indices = {t.i for t in topical}
    subject = next(
        (t for t in head.children if t.dep_ in ("nsubj", "nsubjpass")),
        None,
    )
    subject_in_theme = subject is not None and subject.i in topical_indices

    def marked_kind(reason_prefix):
        if is_circumstantial(topical_head):
            return (
                {"marked-theme", "marked-adjunct"},
                0.85,
                f"{reason_prefix}: Adjunct '{topical_head.text}' fronted",
            )
        return (
            {"marked-theme", "marked-complement"},
            0.7,
            f"{reason_prefix}: Complement '{topical_head.text}' fronted",
        )

    # --- imperative ---
    if "imperative" in mood_features:
        if topical_head.i == head.i or head.lemma_.lower() == "let":
            return (
                {"unmarked-theme"},
                0.85,
                "Predicator as Theme — unmarked for imperative",
            )
        return marked_kind("marked for imperative")

    # --- WH-interrogative ---
    if "wh-interrogative" in mood_features:
        if topical and topical[0].text.lower() in WH_WORDS:
            return (
                {"unmarked-theme"},
                0.85,
                "WH-element as Theme — unmarked for WH-interrogative",
            )
        return marked_kind("marked for WH-interrogative")

    # --- polar interrogative ---
    if "polar" in mood_features:
        if subject_in_theme:
            return (
                {"unmarked-theme"},
                0.85,
                "Finite + Subject as Theme — unmarked for polar interrogative",
            )
        return marked_kind("marked for polar interrogative")

    # --- declarative (and non-finite, which has no mood of its own) ---
    if subject_in_theme:
        confidence = 0.9 if mood_features else 0.5
        return (
            {"unmarked-theme"},
            confidence,
            "Subject as Theme — unmarked for declarative",
        )

    return marked_kind("marked for declarative")


def detect_predication(clause, doc):
    """
    Theme predication — the it-cleft:
        "It was the lion that caught the tourist"

    Pattern: 'it' + a form of 'be' + Complement + relative clause.

    Returns (features, confidence, reason).
    """
    head = doc[clause.head_index]

    if head.lemma_.lower() != "be":
        return {"non-predicated"}, 0.9, "main verb is not 'be'"

    subject = next(
        (t for t in head.children if t.dep_ in ("nsubj", "expl")),
        None,
    )
    if subject is None or subject.text.lower() != "it":
        return {"non-predicated"}, 0.9, "no expletive 'it'"

    for child in head.children:
        if child.dep_ in ("attr", "acomp", "dobj"):
            if any(g.dep_ == "relcl" for g in child.children):
                return (
                    {"predicated"},
                    0.8,
                    "it-cleft: 'it' + be + Complement + relative clause",
                )

    return {"non-predicated"}, 0.85, "'it' + be but no relative clause"


# ---------------------------------------------------------------------------
# Element types (element rank)
# ---------------------------------------------------------------------------

def textual_type(token):
    """continuative / structural / conjunctive"""
    word = token.text.lower()
    if word in CONJUNCTIVE_ADJUNCTS:
        return "conjunctive"
    if token.dep_ in ("cc", "mark"):
        return "structural"
    if word in CONTINUATIVES:
        return "continuative"
    return "structural"


def interpersonal_type(token):
    """vocative / modal Adjunct / Finite / WH-element"""
    word = token.text.lower()
    if word in WH_WORDS:
        return "int-wh"
    if token.pos_ == "AUX":
        return "int-finite"
    if token.dep_ == "vocative":
        return "int-vocative"
    return "int-modal-adjunct"


def is_multiple_theme(features):
    """
    Multiple Theme is DERIVED, not selected: a Theme is multiple exactly
    when it contains a textual or interpersonal element as well as the
    obligatory topical one.
    """
    return "textual-present" in features or "interpersonal-present" in features


# ---------------------------------------------------------------------------
# Putting it together
# ---------------------------------------------------------------------------

def build_mood_selection(mood_features):
    """MOOD features as a selection expression (empty for non-finite clauses)."""
    return SelectionExpression(rank="clause", features=set(mood_features))


def analyse_theme(clause, doc):
    """
    Full THEME analysis of one clause.

    Returns a dict with the Theme/Rheme split, the selection expression,
    the evidence for each choice, and an overall confidence.
    """
    mood_features, mood_conf, mood_reason = detect_mood(clause, doc)
    parts = find_theme(clause, doc, mood_features)

    features = set()
    evidence = []
    confidences = []

    # --- markedness ---
    mk_features, mk_conf, mk_reason = assess_markedness(
        clause, doc, mood_features, parts
    )
    features |= mk_features
    evidence.append(mk_reason)
    confidences.append(mk_conf)

    # --- topical Theme type ---
    tt, tt_conf, tt_reason = topical_type(parts["topical_head"])
    if tt is not None:
        features.add(tt)
        evidence.append(tt_reason)
        confidences.append(tt_conf)

    # --- textual Theme present or absent ---
    if parts["textual"]:
        features.add("textual-present")
        words = " ".join(t.text for t in parts["textual"])
        evidence.append(f"textual Theme: {words}")
    else:
        features.add("textual-absent")

    # --- interpersonal Theme present or absent ---
    if parts["interpersonal"]:
        features.add("interpersonal-present")
        words = " ".join(t.text for t in parts["interpersonal"])
        evidence.append(f"interpersonal Theme: {words}")
    else:
        features.add("interpersonal-absent")

    # --- Theme predication ---
    pr_features, pr_conf, pr_reason = detect_predication(clause, doc)
    features |= pr_features
    if "predicated" in pr_features:
        evidence.append(pr_reason)
        confidences.append(pr_conf)

    # --- element-rank sub-selections, one per Theme element ---
    sub_selections = []
    for token in parts["textual"]:
        sub_selections.append(
            SelectionExpression(rank="element", features={textual_type(token)})
        )
    for token in parts["interpersonal"]:
        sub_selections.append(
            SelectionExpression(rank="element", features={interpersonal_type(token)})
        )

    selection = SelectionExpression(
        rank="clause",
        features=features,
        sub_selections=sub_selections,
    )

    return {
        "clause_id": clause.id,
        "clause_text": clause.text,
        "mood_features": mood_features,
        "mood_reason": mood_reason,
        "mood_selection": build_mood_selection(mood_features),
        "theme_text": parts["theme_text"],
        "rheme_text": parts["rheme_text"],
        "parts": parts,
        "selection": selection,
        "is_multiple": is_multiple_theme(features),
        "evidence": evidence,
        "confidence": min(confidences) if confidences else 0.0,
    }


def analyse_text_themes(text):
    """Analyse the Theme of every clause in a text."""
    from src.segmenter import segment

    doc = nlp(text)
    return [analyse_theme(clause, doc) for clause in segment(text)]