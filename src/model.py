"""Data models for SFL system networks and clause analysis."""

from typing import Literal, Optional
from pydantic import BaseModel


Rank = Literal["clause", "clause-nexus", "group", "element"]


# ---------------------------------------------------------------------------
# Network definitions (Phase 1)
# ---------------------------------------------------------------------------

class Condition(BaseModel):
    """An entry condition: when does a system apply?"""
    op: Literal["root", "feature", "and", "or"]
    value: Optional[str] = None                    # for op == "feature"
    operands: Optional[list["Condition"]] = None   # for and/or


class Term(BaseModel):
    """One option within a system, e.g. 'material'."""
    id: str
    name: str
    gloss: Optional[str] = None
    realization: list[str] = []
    ifg_ref: Optional[str] = None
    markedness_criteria: Optional[dict[str, str]] = None
    notation: Optional[dict[str, str]] = None


class System(BaseModel):
    """A choice between mutually exclusive terms."""
    id: str
    name: str
    rank: Rank
    entry: Condition
    terms: list[Term]


class Network(BaseModel):
    """A whole system network, e.g. TRANSITIVITY."""
    name: str
    metafunction: Literal["experiential", "interpersonal", "textual", "logical"]
    rank: Rank
    source: str
    display: bool = True
    systems: list[System]


class SelectionExpression(BaseModel):
    """The set of features chosen for one clause, nexus, or element."""
    rank: Rank
    features: set[str]
    sub_selections: list["SelectionExpression"] = []


# ---------------------------------------------------------------------------
# Text analysis (Phase 2 onwards)
# ---------------------------------------------------------------------------

class Clause(BaseModel):
    """One clause found in a text."""
    id: str
    head_index: int
    token_indices: list[int]
    text: str
    status: Literal["ranking", "embedded"] = "ranking"
    status_confidence: float = 1.0
    status_reason: Optional[str] = None
    finite: bool
    dep_to_parent: Optional[str] = None
    parent_clause_id: Optional[str] = None


class Nexus(BaseModel):
    """The relationship between two ranking clauses."""
    id: str
    primary_clause_id: str
    secondary_clause_id: str
    features: set[str]
    confidence: float = 1.0
    reason: Optional[str] = None


# Pydantic needs this for the self-referencing classes above
Condition.model_rebuild()
SelectionExpression.model_rebuild()