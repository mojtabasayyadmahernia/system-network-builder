# SFL System Network Builder

A Python library that represents Systemic Functional Linguistics system networks as data, and validates analyses against them.

Given a set of grammatical features like `{material, effective, transformative}`, it answers: which systems does this enter, what still needs choosing, and is this a legal selection?

**Status:** Phase 1 of a larger project. This is the grammar engine only — it knows the networks and nothing about text. Automatic analysis of real sentences comes later. Nothing here imports spaCy.

Reference grammar: Halliday & Matthiessen (2014), *Introduction to Functional Grammar*, 4th edition.

---

## What a system network is

In SFL, grammar is modelled as sets of choices rather than a list of structures. A **system** is a choice between mutually exclusive options, with an **entry condition** saying when that choice arises. Choosing `material` opens further choices — creative or transformative — that don't exist for a `mental` clause.

Moving left to right through a network is increasing **delicacy**. Systems sharing an entry condition are **simultaneous**: both must be chosen from.

A complete analysis of a clause is a **selection expression** — the set of features chosen across every system the clause entered.

## What's encoded

| Network | Metafunction | Rank |
|---|---|---|
| TRANSITIVITY | experiential | clause |
| THEME | textual | clause |
| MOOD | interpersonal | clause |
| CLAUSE COMPLEX | logical | clause nexus |

MOOD is marked `display: false` — it exists because Theme markedness is defined relative to mood, but it isn't shown as a network in its own right yet.

## Modelling decisions

Each of these is a place where the encoding forced a choice the theory leaves open.

**Simultaneity is derived, not declared.** Two systems are simultaneous exactly when they share an entry condition, so the code computes it rather than storing a flag. One less thing to keep consistent by hand.

**Circumstances are element-rank.** "Yesterday she ran quickly" has two circumstances at once. A single clause-level feature can't hold two answers, so circumstance type is chosen once per circumstantial element. Selection expressions are therefore two-level: a clause-level set plus zero or more element-level sub-selections.

**Multiple Theme is derived.** The alternative — a THEME COMPLEXITY system choosing simple/multiple before selecting the parts — is circular. You know a Theme is multiple *because* you found a textual or interpersonal element. So the parts are selected and multiplicity is computed.

**Markedness is one system, not four.** Unmarked Theme means something different in each mood. That could be encoded as four mood-conditional systems, which would show the dependency in the diagram. Instead there's a single THEME SELECTION with the per-mood criteria stored as data on each term, so the information survives without the system count multiplying.

**Embedded clauses are excluded from nexuses.** Hypotaxis is a relation between two ranking clauses; embedding is a clause functioning as a constituent of a group. Both look like "a clause inside a clause," but only the first is a clause complex. Rank is a first-class property in the model so the validator can enforce this.

## Running it

```bash
pip install -r requirements.txt
pytest
```

Tests cover entry-condition evaluation, network traversal, all five validation rules, and a set of hand-written gold analyses.

## Validation rules

A selection expression is checked against five rules:

1. **Unknown feature** — the feature isn't defined in this network
2. **Rank mismatch** — a clause-rank feature in a nexus expression, or similar
3. **Entry unsatisfied** — `transformative` selected without `material`
4. **Mutual exclusivity** — both `attributive` and `identifying` selected
5. **Incomplete** — a system was entered but nothing chosen from it

Rule 5 is what makes this a *system* network rather than a set of labels: entering a system obliges a choice. `{material}` on its own is invalid, because AGENCY and CIRCUMSTANTIATION were entered and ignored.

Failures return the rule, the system, and the features involved — not just a boolean.

## Structure

| Path | Contents |
|---|---|
| `networks/*.json` | The four network definitions |
| `src/model.py` | Network, System, Term, Condition, SelectionExpression |
| `src/loader.py` | JSON to model objects |
| `src/conditions.py` | Entry-condition evaluation |
| `src/traversal.py` | Entered systems, available choices, delicacy, simultaneity |
| `src/validator.py` | The five rules |
| `src/notation.py` | IFG clause-complex notation (α, ×β, "2) |
| `tests/fixtures/gold_selections.json` | Hand-written analyses with expected results |

## Limitations

- **No nesting in clause complexes.** Nexuses are a flat list, so `1 ^ (2 ^ 3)` and `(1 ^ 2) ^ 3` are not distinguished.
- **No grammatical metaphor.** Nominalization concealing a process is out of scope.
- **Delicacy stops well short of IFG4.** The networks go two or three levels deep, not to the limits of the grammar. Adding more is a JSON edit, by design.
- **English only**, with declaratives as the primary case.