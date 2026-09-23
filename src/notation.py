"""
IFG clause-complex notation.

Taxis assigns the base symbol:
    parataxis  -> 1, 2, 3   (equal status)
    hypotaxis  -> a, B, y   (unequal status: alpha, beta, gamma)

Logico-semantic type prefixes the SECONDARY clause only:
    elaborating  =
    extending    +
    enhancing    x (multiplication sign)
    locution     "
    idea         '

So a hypotactic enhancing nexus gives:   alpha,  x-beta
A paratactic locution nexus gives:       1,      "2
"""

PARATACTIC_SYMBOLS = ["1", "2", "3", "4", "5"]
HYPOTACTIC_SYMBOLS = ["\u03b1", "\u03b2", "\u03b3", "\u03b4", "\u03b5"]

LOGICO_SEMANTIC_SYMBOLS = {
    "elaborating": "=",
    "extending": "+",
    "enhancing": "\u00d7",
    "locution": '"',
    "idea": "'",
}

ORDERING = "^"   # 'is followed by', used in realization statements


def taxis_symbol(features, position):
    """Base symbol for the clause at `position` (0 = primary) in a nexus."""
    if "parataxis" in features:
        return PARATACTIC_SYMBOLS[position]
    if "hypotaxis" in features:
        return HYPOTACTIC_SYMBOLS[position]
    raise ValueError("Nexus selection must include parataxis or hypotaxis")


def logico_semantic_symbol(features):
    """Prefix symbol from the logico-semantic selection."""
    for feature, symbol in LOGICO_SEMANTIC_SYMBOLS.items():
        if feature in features:
            return symbol
    raise ValueError("Nexus selection must include a logico-semantic type")


def nexus_notation(features):
    """
    Return (primary, secondary) notation for a nexus.

    >>> nexus_notation({"hypotaxis", "expansion", "enhancing"})
    ('\u03b1', '\u00d7\u03b2')
    >>> nexus_notation({"parataxis", "projection", "locution"})
    ('1', '"2')
    """
    primary = taxis_symbol(features, 0)
    secondary = taxis_symbol(features, 1)
    symbol = logico_semantic_symbol(features)
    return primary, f"{symbol}{secondary}"