"""
Clause segmentation.

Takes a text and works out:
  - where the clauses are
  - whether each is a ranking clause or embedded in a phrase
  - how the ranking clauses relate to one another (nexuses)
"""

import spacy

from src.model import Clause, Nexus

nlp = spacy.load("en_core_web_sm")


# ---------------------------------------------------------------------------
# Word lists and constants
# ---------------------------------------------------------------------------

# Dependency labels that can head a clause
CLAUSE_HEAD_DEPS = {
    "ROOT",       # main clause
    "conj",       # coordinate clause: "he came in AND sat down"
    "advcl",      # adverbial clause: "BECAUSE it was hungry"
    "ccomp",      # clausal complement: "she said THAT HE LEFT"
    "xcomp",      # open complement: "she wanted TO LEAVE"
    "relcl",      # relative clause: "the man WHO LEFT"
    "acl",        # clausal noun modifier: "the decision TO LEAVE"
    "csubj",      # clausal subject: "THAT HE LEFT surprised me"
    "csubjpass",
    "parataxis",
}

# Tags for finite verb forms: past, present, 3rd-person singular, modal
FINITE_TAGS = {"VBD", "VBP", "VBZ", "MD"}

# Dependency labels that are ALWAYS embedded (constituents of a group)
EMBEDDED_DEPS = {"csubj", "csubjpass", "acl"}

# Verbs that project someone's WORDS (verbal processes)
VERBAL_PROJECTORS = {
    "say", "tell", "ask", "reply", "answer", "explain", "claim",
    "argue", "announce", "state", "remark", "suggest", "insist",
    "report", "declare", "mention", "add", "note", "observe",
}

# Verbs that project someone's THOUGHTS (mental processes)
MENTAL_PROJECTORS = {
    "think", "believe", "know", "realise", "realize", "suppose",
    "assume", "understand", "feel", "imagine", "doubt", "wonder",
    "hope", "wish", "expect", "fear", "decide", "remember", "forget",
}

PROJECTORS = VERBAL_PROJECTORS | MENTAL_PROJECTORS

# Conjunction -> (expansion type, subtype)
EXPANSION_MARKERS = {
    # extending — adding
    "and":      ("extending", "additive"),
    "nor":      ("extending", "additive"),
    "moreover": ("extending", "additive"),
    "but":      ("extending", "adversative"),
    "yet":      ("extending", "adversative"),
    "whereas":  ("extending", "adversative"),
    "or":       ("extending", "variation"),
    "instead":  ("extending", "variation"),
    "except":   ("extending", "variation"),

    # enhancing — time
    "when":   ("enhancing", "enh-temporal"),
    "while":  ("enhancing", "enh-temporal"),
    "after":  ("enhancing", "enh-temporal"),
    "before": ("enhancing", "enh-temporal"),
    "until":  ("enhancing", "enh-temporal"),
    "once":   ("enhancing", "enh-temporal"),

    # enhancing — place
    "where":    ("enhancing", "enh-spatial"),
    "wherever": ("enhancing", "enh-spatial"),

    # enhancing — manner
    "as": ("enhancing", "enh-manner"),

    # enhancing — cause, condition, concession
    "because":  ("enhancing", "enh-causal"),
    "so":       ("enhancing", "enh-causal"),
    "if":       ("enhancing", "enh-causal"),
    "unless":   ("enhancing", "enh-causal"),
    "although": ("enhancing", "enh-causal"),
    "though":   ("enhancing", "enh-causal"),
}

# 'since' is genuinely ambiguous — temporal ("since he arrived") or causal
# ("since he was tired"). Defaults to temporal, flagged low confidence.
AMBIGUOUS_MARKERS = {"since"}

QUOTE_CHARS = {'"', '\u201c', '\u201d', "'", '\u2019'}


# ---------------------------------------------------------------------------
# Finding clauses
# ---------------------------------------------------------------------------

def find_clause_heads(doc):
    """Return the tokens that head a clause, in sentence order."""
    heads = []
    for token in doc:
        if token.dep_ not in CLAUSE_HEAD_DEPS:
            continue
        # 'conj' also links coordinated nouns ("the lion AND the tiger").
        # Only a verb or auxiliary can head a clause.
        if token.pos_ not in ("VERB", "AUX"):
            continue
        heads.append(token)
    return sorted(heads, key=lambda t: t.i)


def assign_spans(doc, clause_heads):
    """
    Work out which tokens belong to which clause.

    Each token walks up the dependency tree until it reaches a clause head.
    That head owns it. This stops a main clause from swallowing the
    subordinate clauses inside it.
    """
    head_indices = {t.i for t in clause_heads}
    spans = {}

    for head in clause_heads:
        own_tokens = []
        for token in head.subtree:
            owner = token
            while owner.i not in head_indices and owner.head != owner:
                owner = owner.head
            if owner.i == head.i:
                own_tokens.append(token)
        spans[head.i] = sorted(own_tokens, key=lambda t: t.i)

    return spans


def is_finite(head, span):
    """
    A clause is finite if its verb carries tense or has a finite auxiliary.

    finite:      "she leaves", "she left", "she will leave", "she has left"
    non-finite:  "to leave", "leaving", "left" (as a participle)
    """
    if head.tag_ in FINITE_TAGS:
        return True
    return any(
        t.pos_ == "AUX" and t.tag_ in FINITE_TAGS and t.head == head
        for t in span
    )


# ---------------------------------------------------------------------------
# Ranking vs embedded
# ---------------------------------------------------------------------------

def is_non_defining_relative(head, doc):
    """
    Non-defining relatives are set off by commas:
        "John, who left early, was tired"   -> non-defining (ranking)
        "The man who left early was tired"  -> defining (embedded)

    Imperfect, because writers are inconsistent with commas.
    """
    indices = [t.i for t in head.subtree]
    start, end = min(indices), max(indices)

    before = doc[start - 1] if start > 0 else None
    after = doc[end + 1] if end + 1 < len(doc) else None

    comma_before = before is not None and before.text == ","
    closed_after = after is None or after.text in {",", ".", ";", "!", "?"}

    return comma_before and closed_after


def is_projected(head):
    """Is this clause introduced by a projecting verb?"""
    return head.head.lemma_.lower() in PROJECTORS


def is_quoted(doc, span):
    """Direct speech — quotation marks present."""
    return any(t.text in QUOTE_CHARS for t in span)


def classify_status(head, doc, span):
    """
    Decide whether a clause is ranking or embedded.

    Ranking clauses take part in clause complexes; embedded clauses are
    constituents of a group and do not.

    Returns (status, confidence, reason).
    """
    dep = head.dep_

    if dep in EMBEDDED_DEPS:
        return "embedded", 0.9, f"{dep} — clause functions as a constituent"

    if dep == "relcl":
        if is_non_defining_relative(head, doc):
            return "ranking", 0.6, "non-defining relative (comma-delimited)"
        return "embedded", 0.8, "defining relative — part of the nominal group"

    if dep == "ccomp":
        if is_projected(head):
            verb = head.head.lemma_
            return "ranking", 0.85, f"projected by '{verb}' — clause complex"
        return "embedded", 0.7, "ccomp not projected by a verbal/mental process"

    if dep == "xcomp":
        return "embedded", 0.4, "xcomp — treated as verbal group complex"

    return "ranking", 0.95, f"{dep} — independent or hypotactic clause"


# ---------------------------------------------------------------------------
# Segmentation
# ---------------------------------------------------------------------------

def segment(text: str) -> list[Clause]:
    """Split a text into clauses."""
    doc = nlp(text)
    heads = find_clause_heads(doc)
    spans = assign_spans(doc, heads)

    id_by_head = {h.i: f"c{n}" for n, h in enumerate(heads)}

    clauses = []
    for head in heads:
        span = spans[head.i]

        # the parent clause is the nearest clause head above this one
        parent_id = None
        walker = head.head
        while walker != walker.head:
            if walker.i in id_by_head:
                parent_id = id_by_head[walker.i]
                break
            walker = walker.head
        else:
            if walker.i in id_by_head and walker.i != head.i:
                parent_id = id_by_head[walker.i]

        status, confidence, reason = classify_status(head, doc, span)

        clauses.append(Clause(
            id=id_by_head[head.i],
            head_index=head.i,
            token_indices=[t.i for t in span],
            text=" ".join(t.text for t in span),
            status=status,
            status_confidence=confidence,
            status_reason=reason,
            finite=is_finite(head, span),
            dep_to_parent=head.dep_ if head.dep_ != "ROOT" else None,
            parent_clause_id=parent_id,
        ))

    return clauses


# ---------------------------------------------------------------------------
# Nexuses — the links between ranking clauses
# ---------------------------------------------------------------------------

def find_marker(head, span):
    """
    Find the conjunction that introduces this clause: because, and, when...
    Returns the word in lowercase, or None.
    """
    # 'mark' labels subordinating conjunctions: because, when, if, that
    for child in head.children:
        if child.dep_ == "mark":
            return child.text.lower()

    # 'cc' labels coordinating conjunctions: and, but, or
    for child in head.children:
        if child.dep_ == "cc":
            return child.text.lower()

    # fallback: clause starts with a conjunction
    if span and span[0].pos_ in ("SCONJ", "CCONJ"):
        return span[0].text.lower()

    return None


def infer_nexus_features(clause, head, doc, span):
    """
    Work out the taxis and logico-semantic features for the link between
    this clause and its parent.

    Returns (features, confidence, reason).
    """
    features = set()
    marker = find_marker(head, span)
    quoted = is_quoted(doc, span)

    # --- Question 1: equal or unequal status? ---
    if head.dep_ in ("conj", "parataxis") or quoted:
        features.add("parataxis")
    else:
        features.add("hypotaxis")

    # --- Question 2: what kind of link? ---

    # Projection: someone's words or thoughts
    if head.dep_ == "ccomp" and is_projected(head):
        features.add("projection")
        verb = head.head.lemma_.lower()
        features.add("locution" if verb in VERBAL_PROJECTORS else "idea")
        features.add("quoting" if quoted else "reporting")
        return features, 0.85, f"projected by '{verb}'"

    # Elaboration: non-defining relative clause
    if head.dep_ == "relcl":
        features.update({"expansion", "elaborating", "exposition"})
        return features, 0.6, "non-defining relative — elaborating"

    # Expansion: look up the conjunction
    features.add("expansion")

    if marker in EXPANSION_MARKERS:
        exp_type, subtype = EXPANSION_MARKERS[marker]
        features.update({exp_type, subtype})
        confidence = 0.5 if marker in AMBIGUOUS_MARKERS else 0.85
        return features, confidence, f"marker '{marker}'"

    # No marker found — fall back on the dependency label
    if head.dep_ == "conj":
        features.update({"extending", "additive"})
        return features, 0.5, "coordinated clause, no marker — assumed additive"

    features.update({"enhancing", "enh-temporal"})
    return features, 0.4, "no marker found — assumed temporal enhancement"


def build_nexuses(clauses, doc):
    """
    Build the links between ranking clauses.

    Embedded clauses are skipped — they are parts of phrases, not clauses
    in a complex.
    """
    ranking = [c for c in clauses if c.status == "ranking"]
    by_id = {c.id: c for c in ranking}
    nexuses = []

    for clause in ranking:
        if clause.parent_clause_id is None:
            continue                       # this is the main clause

        parent = by_id.get(clause.parent_clause_id)
        if parent is None:
            continue                       # parent was embedded — no nexus

        head = doc[clause.head_index]
        span = [doc[i] for i in clause.token_indices]
        features, confidence, reason = infer_nexus_features(clause, head, doc, span)

        # In parataxis the earlier clause is primary.
        # In hypotaxis the parent is primary, wherever it sits.
        if "parataxis" in features and clause.head_index < parent.head_index:
            primary, secondary = clause, parent
        else:
            primary, secondary = parent, clause

        nexuses.append(Nexus(
            id=f"nex_{primary.id}_{secondary.id}",
            primary_clause_id=primary.id,
            secondary_clause_id=secondary.id,
            features=features,
            confidence=confidence,
            reason=reason,
        ))

    return nexuses


def analyse(text):
    """Segment a text and build its nexuses. Returns (clauses, nexuses)."""
    doc = nlp(text)
    clauses = segment(text)
    nexuses = build_nexuses(clauses, doc)
    return clauses, nexuses