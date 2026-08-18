"""Clause segmentation"""

import spacy

nlp = spacy.load("en_core_web_sm")

# Dependency labels that can head a clause.
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
            # climb until we hit a clause head (or the top of the tree)
            while owner.i not in head_indices and owner.head != owner:
                owner = owner.head
            if owner.i == head.i:
                own_tokens.append(token)
        spans[head.i] = sorted(own_tokens, key=lambda t: t.i)

    return spans
# Tags for finite verb forms: past, present, 3rd-person singular, modal
FINITE_TAGS = {"VBD", "VBP", "VBZ", "MD"}


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

from src.model import Clause


def segment(text: str) -> list[Clause]:
    """Split a text into clauses."""
    doc = nlp(text)
    heads = find_clause_heads(doc)
    spans = assign_spans(doc, heads)

    # head token index -> clause id, so we can record parents
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

        clauses.append(Clause(
            id=id_by_head[head.i],
            head_index=head.i,
            token_indices=[t.i for t in span],
            text=" ".join(t.text for t in span),
            finite=is_finite(head, span),
            dep_to_parent=head.dep_ if head.dep_ != "ROOT" else None,
            parent_clause_id=parent_id,
        ))

    return clauses