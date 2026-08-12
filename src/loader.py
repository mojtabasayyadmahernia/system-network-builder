"""Load network definitions from JSON files into model objects."""

import json
from pathlib import Path

from src.model import Network

# The networks folder sits next to src/, at the project root.
NETWORKS_DIR = Path(__file__).resolve().parent.parent / "networks"


def load_network(name: str) -> Network:
    """
    Load a network by filename stem.

        load_network("transitivity")  ->  reads networks/transitivity.json

    Raises FileNotFoundError with a helpful message if the file isn't there.
    """
    path = NETWORKS_DIR / f"{name}.json"

    if not path.exists():
        available = sorted(p.stem for p in NETWORKS_DIR.glob("*.json"))
        raise FileNotFoundError(
            f"No network file at {path}\n"
            f"Available networks: {available or '(none — networks/ is empty)'}"
        )

    data = json.loads(path.read_text(encoding="utf-8"))
    return Network(**data)


def load_all() -> dict[str, Network]:
    """Load every network in networks/. Handy in the notebook."""
    return {
        p.stem: load_network(p.stem)
        for p in sorted(NETWORKS_DIR.glob("*.json"))
    }