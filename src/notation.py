"""
IFG clause-complex notation.

Taxis assigns the base symbol:
    parataxis  → 1, 2, 3 (equal status)
    hypotaxis  → α, β, γ (unequal status)

Logico-semantic type prefixes the SECONDARY clause only:
    elaborating  =
    extending    +
    enhancing    ×
    locution     "
    idea         '

So a hypotactic enhancing nexus gives:  α  ×β
A paratactic locution nexus gives:      1  "2
"""

PARATACTIC_SYMBOLS = ["1", "2", "3", "4", "5"]
HYPOTACTIC_SYMBOLS = ["α", "β", "γ", "δ", "ε"]

LOGICO_SEMANTIC_SYMBOLS = {
    "elaborating": "=",
    "extending":   "+",
    "enhancing":   "×",
    "locution":    '"',
    "idea":        "'",
}

ORDERING = "^"   # 'is followed by', used in realization statements


def taxis_symbol(features: set[str], position: int) -> str:
    """Base symbol for a clause at `position` (0 = primary) in a nexus."""
    if "parataxis" in features:
        return PARATACTIC_SYMBOLS[position]
    if "hypotaxis" in features:
        return HYPOTACTIC_SYMBOLS[position]
    raise ValueError("Nexus selection must include parataxis or hypotaxis")


def logico_semantic_symbol(features: set[str]) -> str:
    """Prefix symbol from the logico-semantic selection."""
    for feature, symbol in LOGICO_SEMANTIC_SYMBOLS.items():
        if feature in features:
            return symbol
    raise ValueError("Nexus selection must include a logico-semantic type")


def nexus_notation(features: set[str]) -> tuple[str, str]:
    """
    Return (primary, secondary) notation for a nexus.

    >>> nexus_notation({"hypotaxis", "expansion", "enhancing"})
    ('α', '×β')
    >>> nexus_notation({"parataxis", "projection", "locution"})
    ('1', '"2')
    """
    primary = taxis_symbol(features, 0)
    secondary = taxis_symbol(features, 1)
    symbol = logico_semantic_symbol(features)
    return primary, f"{symbol}{secondary}"