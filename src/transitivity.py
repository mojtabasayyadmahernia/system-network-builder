"""
TRANSITIVITY analysis (IFG4 Ch. 5).

For each clause, works out:
  - the process type (material, mental, relational, verbal, behavioural, existential)
  - the participants and their roles (Actor, Goal, Senser, Carrier, ...)
  - the circumstances and their types (Extent, Location, Manner, Cause)
  - agency (middle or effective)
  - the full TRANSITIVITY selection expression, ready for validation
"""

from src.model import SelectionExpression
from src.segmenter import nlp
from src.verb_lexicon import (
    MATERIAL_VERBS, CREATIVE_VERBS,
    MENTAL_PERCEPTIVE, MENTAL_COGNITIVE, MENTAL_DESIDERATIVE,
    MENTAL_EMOTIVE, MENTAL_PLEASE_TYPE, MENTAL_VERBS,
    COPULAR_VERBS, RELATIONAL_POSSESSIVE, RELATIONAL_CIRCUMSTANTIAL,
    IDENTIFYING_VERBS, RELATIONAL_VERBS,
    VERBAL_VERBS, VERBAL_TARGETING_VERBS, ALL_VERBAL_VERBS,
    BEHAVIOURAL_VERBS,
    LOCATION_PREPS, EXTENT_PREPS, MANNER_PREPS, CAUSE_PREPS,
    TIME_ADVERBS, FREQUENCY_ADVERBS, PLACE_ADVERBS,
    ambiguity_penalty, is_known, lookup,
)

SUBJECT_DEPS = {"nsubj", "nsubjpass"}
OBJECT_DEPS = {"dobj", "obj", "attr", "acomp", "oprd"}
CIRCUMSTANCE_DEPS = {"prep", "advmod", "npadvmod"}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _child(head, deps):
    """First child of `head` whose dependency label is in `deps`."""
    return next((t for t in head.children if t.dep_ in deps), None)

def _children(head, deps):
    return [t for t in head.children if t.dep_ in deps]

def _phrase(token):
    """The full text of a token's phrase."""
    if token is None:
        return None
    return " ".join(t.text for t in sorted(token.subtree, key=lambda x: x.i))

def _has_expletive_there(head):
    return any(
        t.dep_ == "expl" and t.text.lower() == "there" for t in head.children
    )

def _is_definite(token):
    """Does this nominal look definite? Used for identifying vs attributive."""
    if token is None:
        return False
    if token.pos_ == "PROPN":
        return True
    det = _child(token, {"det", "poss"})
    if det is not None and det.text.lower() in ("the", "this", "that", "these", "those"):
        return True
    if _child(token, {"poss"}) is not None:
        return True
    return False


# ---------------------------------------------------------------------------
# Process type
# ---------------------------------------------------------------------------

def classify_process(clause, doc):
    """
    Work out the process type of a clause.

    Checked in order of how reliable the evidence is: syntactic patterns
    first (existential 'there', copular complements), then the lexicon.
    A verb that could belong to several process types has its confidence
    reduced, so the uncertainty is visible rather than hidden.

    Returns (features, confidence, reason).
    """
    features, confidence, reason = _classify_process_raw(clause, doc)

    lemma = doc[clause.head_index].lemma_.lower()
    penalty = ambiguity_penalty(lemma)
    if penalty:
        others = sorted(set(lookup(lemma)) - features)
        if others:
            reason += f"; '{lemma}' can also be {'/'.join(others)}"
        confidence = max(0.2, confidence - penalty)

    return features, confidence, reason


def _classify_process_raw(clause, doc):
    """The ordered tests, before any ambiguity adjustment."""
    head = doc[clause.head_index]
    lemma = head.lemma_.lower()

    # --- existential: "There was a storm" ---
    if lemma == "be" and _has_expletive_there(head):
        return {"existential"}, 0.95, "expletive 'there' with 'be'"

    # --- relational: a copular verb with a Complement ---
    complement = _child(head, {"attr", "acomp", "oprd"})
    if lemma in COPULAR_VERBS and complement is not None:
        return {"relational"}, 0.9, f"copular '{head.text}' with Complement '{complement.text}'"

    # --- relational: possessive or circumstantial ---
    if lemma in RELATIONAL_POSSESSIVE:
        return {"relational"}, 0.75, f"'{lemma}' is a possessive relational verb"
    if lemma in RELATIONAL_CIRCUMSTANTIAL:
        return {"relational"}, 0.75, f"'{lemma}' is a circumstantial relational verb"
    if lemma in IDENTIFYING_VERBS:
        return {"relational"}, 0.8, f"'{lemma}' identifies"

    # --- verbal ---
    if lemma in ALL_VERBAL_VERBS:
        return {"verbal"}, 0.85, f"'{lemma}' is a verbal process"

    # --- mental ---
    if lemma in MENTAL_VERBS:
        # 'look', 'watch', 'listen' are behavioural when they take a
        # prepositional phrase: "she looked at him"
        if lemma in BEHAVIOURAL_VERBS and _child(head, {"prep"}) is not None:
            return {"behavioural"}, 0.7, f"'{lemma}' with a preposition — behavioural"
        return {"mental"}, 0.85, f"'{lemma}' is a mental process"

    # --- behavioural ---
    if lemma in BEHAVIOURAL_VERBS:
        return {"behavioural"}, 0.8, f"'{lemma}' is a behavioural process"

    # --- material ---
    if lemma in MATERIAL_VERBS:
        return {"material"}, 0.85, f"'{lemma}' is a material process"

    # --- fallback ---
    if lemma == "be":
        return {"relational"}, 0.6, "'be' with no Complement found — assumed relational"

    return {"material"}, 0.3, f"'{lemma}' not in the lexicon — defaulted to material"


def material_subtype(clause, doc):
    """creative (the Goal comes into being) or transformative (it pre-exists)."""
    head = doc[clause.head_index]
    lemma = head.lemma_.lower()
    if lemma in CREATIVE_VERBS:
        return "creative", 0.8, f"'{lemma}' brings its Goal into existence"
    return "transformative", 0.7, f"'{lemma}' acts on a pre-existing Goal"


def mental_subtype(clause, doc):
    """perceptive / cognitive / desiderative / emotive, plus directionality."""
    head = doc[clause.head_index]
    lemma = head.lemma_.lower()

    if lemma in MENTAL_PERCEPTIVE:
        kind, conf = "perceptive", 0.85
    elif lemma in MENTAL_COGNITIVE:
        kind, conf = "cognitive", 0.85
    elif lemma in MENTAL_DESIDERATIVE:
        kind, conf = "desiderative", 0.85
    elif lemma in MENTAL_PLEASE_TYPE:
        kind, conf = "emotive", 0.8
    elif lemma in MENTAL_EMOTIVE:
        kind, conf = "emotive", 0.85
    else:
        kind, conf = "cognitive", 0.3

    if lemma in MENTAL_PLEASE_TYPE:
        direction = "please-type"
        d_reason = f"'{lemma}' puts the Phenomenon in Subject position"
    else:
        direction = "like-type"
        d_reason = f"'{lemma}' puts the Senser in Subject position"

    return {kind, direction}, conf, f"'{lemma}' is {kind}; {d_reason}"


def relational_subtype(clause, doc):
    """
    Two simultaneous choices:
      MODE — attributive or identifying
      TYPE — intensive, possessive, or circumstantial
    """
    head = doc[clause.head_index]
    lemma = head.lemma_.lower()
    features = set()
    reasons = []

    # --- MODE ---
    complement = _child(head, {"attr", "oprd"})
    adjectival = _child(head, {"acomp"})

    if adjectival is not None:
        features.add("attributive")
        reasons.append(f"adjectival Complement '{adjectival.text}' — attributive")
        mode_conf = 0.85
    elif lemma in IDENTIFYING_VERBS:
        features.add("identifying")
        reasons.append(f"'{lemma}' identifies")
        mode_conf = 0.8
    elif complement is not None and _is_definite(complement):
        features.add("identifying")
        reasons.append(f"definite Complement '{complement.text}' — identifying")
        mode_conf = 0.75
    else:
        features.add("attributive")
        reasons.append("indefinite or absent Complement — attributive")
        mode_conf = 0.6

    # --- TYPE ---
    if lemma in RELATIONAL_POSSESSIVE:
        features.add("possessive")
        reasons.append(f"'{lemma}' is possessive")
        type_conf = 0.8
    elif lemma in RELATIONAL_CIRCUMSTANTIAL:
        features.add("circumstantial")
        reasons.append(f"'{lemma}' is circumstantial")
        type_conf = 0.8
    elif _child(head, {"prep"}) is not None and lemma == "be" and adjectival is None and complement is None:
        features.add("circumstantial")
        reasons.append("'be' with a prepositional Complement — circumstantial")
        type_conf = 0.7
    else:
        features.add("intensive")
        reasons.append("intensive")
        type_conf = 0.8

    return features, min(mode_conf, type_conf), "; ".join(reasons)


def verbal_subtype(clause, doc):
    """targeting (someone talked about) or non-targeting."""
    head = doc[clause.head_index]
    lemma = head.lemma_.lower()
    if lemma in VERBAL_TARGETING_VERBS:
        return "targeting", 0.8, f"'{lemma}' takes a Target"
    return "non-targeting", 0.8, f"'{lemma}' has no Target"


# ---------------------------------------------------------------------------
# Participants
# ---------------------------------------------------------------------------

PARTICIPANT_ROLES = {
    "material":    {"subject": "Actor",   "object": "Goal"},
    "mental":      {"subject": "Senser",  "object": "Phenomenon"},
    "verbal":      {"subject": "Sayer",   "object": "Verbiage"},
    "behavioural": {"subject": "Behaver", "object": "Behaviour"},
    "existential": {"subject": "Existent", "object": "Existent"},
}


def assign_participants(clause, doc, process_features):
    """
    Map the clause's Subject and Object onto SFL participant roles.

    Returns a list of dicts: role, text, and the evidence for it.
    """
    head = doc[clause.head_index]
    participants = []

    subject = _child(head, SUBJECT_DEPS)
    obj = _child(head, {"dobj", "obj"})
    attr = _child(head, {"attr", "acomp", "oprd"})
    dative = _child(head, {"dative", "iobj"})

    # --- existential ---
    if "existential" in process_features:
        existent = attr or obj or subject
        if existent is not None:
            participants.append({
                "role": "Existent",
                "text": _phrase(existent),
                "why": "the thing whose existence is asserted",
            })
        return participants

    # --- relational ---
    if "relational" in process_features:
        if "identifying" in process_features:
            sub_role, comp_role = "Token", "Value"
        else:
            sub_role, comp_role = "Carrier", "Attribute"

        if subject is not None:
            participants.append({
                "role": sub_role, "text": _phrase(subject),
                "why": f"Subject of a relational clause",
            })
        complement = attr or obj
        if complement is not None:
            participants.append({
                "role": comp_role, "text": _phrase(complement),
                "why": "Complement of a relational clause",
            })
        return participants

    # --- mental, with directionality ---
    if "mental" in process_features:
        if "please-type" in process_features:
            sub_role, obj_role = "Phenomenon", "Senser"
            why = "please-type: Phenomenon is Subject"
        else:
            sub_role, obj_role = "Senser", "Phenomenon"
            why = "like-type: Senser is Subject"

        if subject is not None:
            participants.append({"role": sub_role, "text": _phrase(subject), "why": why})
        target = obj or _child(head, {"ccomp", "xcomp"})
        if target is not None:
            participants.append({
                "role": obj_role, "text": _phrase(target),
                "why": "what is sensed",
            })
        return participants

    # --- verbal ---
    if "verbal" in process_features:
        if subject is not None:
            participants.append({
                "role": "Sayer", "text": _phrase(subject), "why": "the one speaking",
            })
        if dative is not None:
            participants.append({
                "role": "Receiver", "text": _phrase(dative), "why": "the one spoken to",
            })
        if obj is not None:
            role = "Target" if "targeting" in process_features else "Verbiage"
            participants.append({
                "role": role, "text": _phrase(obj),
                "why": "what is said" if role == "Verbiage" else "who is spoken about",
            })
        return participants

    # --- material and behavioural ---
    ptype = "material" if "material" in process_features else "behavioural"
    roles = PARTICIPANT_ROLES[ptype]

    if subject is not None:
        participants.append({
            "role": roles["subject"], "text": _phrase(subject),
            "why": f"Subject of a {ptype} clause",
        })
    if obj is not None:
        participants.append({
            "role": roles["object"], "text": _phrase(obj),
            "why": f"Object of a {ptype} clause",
        })
    if dative is not None:
        participants.append({
            "role": "Recipient", "text": _phrase(dative),
            "why": "indirect object — the one who receives",
        })

    return participants


def assess_agency(clause, doc, process_features):
    """
    Middle or effective (the ergative perspective).

    Effective clauses have an external Agent bringing the process about;
    middle clauses do not. Approximated here by the presence of a second
    participant.
    """
    head = doc[clause.head_index]

    if "existential" in process_features:
        return "middle", 0.9, "existential clauses are middle"

    if "relational" in process_features:
        return "middle", 0.85, "relational clauses are typically middle"

    obj = _child(head, {"dobj", "obj"})
    if obj is not None:
        return "effective", 0.85, f"Object '{obj.text}' — a second participant"

    agent_by = None
    for prep in _children(head, {"agent"}):
        agent_by = prep
    if agent_by is not None:
        return "effective", 0.85, "passive with an explicit Agent"

    return "middle", 0.8, "only one participant"


# ---------------------------------------------------------------------------
# Circumstances
# ---------------------------------------------------------------------------

def classify_circumstance(token, doc):
    """
    Which of the frequent four is this circumstance?
    Returns (feature, confidence, reason).
    """
    word = token.text.lower()

    # prepositional phrase — classify by the preposition
    if token.dep_ == "prep" or token.pos_ == "ADP":
        if word in CAUSE_PREPS and word not in ("for",):
            return "cause", 0.8, f"preposition '{word}' — Cause"
        if word in EXTENT_PREPS:
            return "extent", 0.75, f"preposition '{word}' — Extent"
        if word in LOCATION_PREPS:
            return "location", 0.8, f"preposition '{word}' — Location"
        if word in MANNER_PREPS:
            return "manner", 0.75, f"preposition '{word}' — Manner"
        if word == "for":
            return "extent", 0.5, "'for' — Extent or Cause; defaulted to Extent"
        return "location", 0.4, f"preposition '{word}' — defaulted to Location"

    # adverb
    if word in TIME_ADVERBS or word in PLACE_ADVERBS:
        return "location", 0.85, f"'{word}' is a time or place adverb"
    if word in FREQUENCY_ADVERBS:
        return "extent", 0.8, f"'{word}' is a frequency adverb"
    if word.endswith("ly"):
        return "manner", 0.75, f"'{word}' is a manner adverb"

    # bare noun phrase adverbial: "last week", "every day"
    if token.dep_ == "npadvmod":
        return "location", 0.6, f"'{_phrase(token)}' — nominal adverbial, assumed temporal"

    return "manner", 0.3, f"'{word}' — defaulted to Manner"


def find_circumstances(clause, doc):
    """
    Find the circumstantial elements of a clause.

    Returns a list of dicts: type feature, text, confidence, reason.
    """
    head = doc[clause.head_index]
    clause_indices = set(clause.token_indices)
    found = []

    for child in head.children:
        if child.i not in clause_indices:
            continue
        if child.dep_ not in CIRCUMSTANCE_DEPS:
            continue
        # negation is interpersonal, not a circumstance
        if child.dep_ == "advmod" and child.text.lower() in ("not", "n't"):
            continue

        feature, confidence, reason = classify_circumstance(child, doc)
        found.append({
            "feature": feature,
            "text": _phrase(child),
            "confidence": confidence,
            "why": reason,
        })

    return found


# ---------------------------------------------------------------------------
# Putting it together
# ---------------------------------------------------------------------------

def analyse_transitivity(clause, doc):
    """
    Full TRANSITIVITY analysis of one clause.

    Returns a dict with the process, participants, circumstances, the
    selection expression, evidence, and an overall confidence.
    """
    head = doc[clause.head_index]
    features = set()
    evidence = []
    confidences = []

    # --- process type ---
    proc_features, proc_conf, proc_reason = classify_process(clause, doc)
    features |= proc_features
    evidence.append(proc_reason)
    confidences.append(proc_conf)

    # --- subtypes, depending on the process ---
    if "material" in features:
        sub, conf, reason = material_subtype(clause, doc)
        features.add(sub)
        evidence.append(reason)
        confidences.append(conf)

    elif "mental" in features:
        subs, conf, reason = mental_subtype(clause, doc)
        features |= subs
        evidence.append(reason)
        confidences.append(conf)

    elif "relational" in features:
        subs, conf, reason = relational_subtype(clause, doc)
        features |= subs
        evidence.append(reason)
        confidences.append(conf)

    elif "verbal" in features:
        sub, conf, reason = verbal_subtype(clause, doc)
        features.add(sub)
        evidence.append(reason)
        confidences.append(conf)

    # --- agency ---
    agency, ag_conf, ag_reason = assess_agency(clause, doc, features)
    features.add(agency)
    evidence.append(ag_reason)
    confidences.append(ag_conf)

    # --- circumstances ---
    circumstances = find_circumstances(clause, doc)
    if circumstances:
        features.add("circumstantial-clause")
        for c in circumstances:
            evidence.append(f"circumstance '{c['text']}': {c['why']}")
            confidences.append(c["confidence"])
    else:
        features.add("non-circumstantial-clause")

    # --- participants ---
    participants = assign_participants(clause, doc, features)

    # --- element-rank sub-selections, one per circumstance ---
    sub_selections = [
        SelectionExpression(rank="element", features={c["feature"]})
        for c in circumstances
    ]

    selection = SelectionExpression(
        rank="clause",
        features=features,
        sub_selections=sub_selections,
    )

    return {
        "clause_id": clause.id,
        "clause_text": clause.text,
        "process": head.text,
        "process_lemma": head.lemma_.lower(),
        "participants": participants,
        "circumstances": circumstances,
        "selection": selection,
        "evidence": evidence,
        "confidence": min(confidences) if confidences else 0.0,
    }


def analyse_text_transitivity(text):
    """Analyse the transitivity of every clause in a text."""
    from src.segmenter import segment

    doc = nlp(text)
    return [analyse_transitivity(clause, doc) for clause in segment(text)]