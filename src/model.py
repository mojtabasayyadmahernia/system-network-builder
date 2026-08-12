from typing import Literal, Optional, Union
from pydantic import BaseModel

Rank = Literal["clause", "clause-nexus", "group", "element"]

class Condition(BaseModel):
    op: Literal["root", "feature", "and", "or"]
    value: Optional[str] = None            # for op == "feature"
    operands: Optional[list["Condition"]] = None  # for and/or

class Term(BaseModel):
    id: str
    name: str
    gloss: Optional[str] = None
    realization: list[str] = []            # IFG realization statements, e.g. "+Actor"
    ifg_ref: Optional[str] = None          # section reference, e.g. "5.2"

class System(BaseModel):
    id: str
    name: str
    rank: Rank
    entry: Condition
    terms: list[Term]

class Network(BaseModel):
    name: str
    metafunction: Literal["experiential", "interpersonal", "textual", "logical"]
    rank: Rank
    source: str
    display: bool = True
    systems: list[System]

class SelectionExpression(BaseModel):
    rank: Rank
    features: set[str]
    # element-level sub-selections, e.g. one per circumstance
    sub_selections: list["SelectionExpression"] = []

class Nexus(BaseModel):
    id: str
    primary_clause_id: str
    secondary_clause_id: str
    selection: SelectionExpression   # rank must be "clause-nexus"

    def notation_for(self, role: Literal["primary", "secondary"]) -> str:
        """IFG notation for one clause in this nexus, e.g. 'α' or '×β'."""
        ...
        
