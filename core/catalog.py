"""
catalog.py

Loads the SHL catalog from a local JSON file
and builds normalized entries for retrieval.
"""

import json
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

CACHE_PATH = (
    Path(__file__).parent.parent
    / "data"
    / "catalog.json"
)

KEY_TO_TYPE: dict[str, str] = {
    "Knowledge & Skills": "K",
    "Personality & Behavior": "P",
    "Simulations": "S",
    "Ability & Aptitude": "A",
    "Competencies": "C",
    "Biodata & Situational Judgment": "B",
    "Assessment Exercises": "E",
    "Development & 360": "D",
}


def _derive_test_type(keys: list[str]) -> str:

    for k in keys:
        if k in KEY_TO_TYPE:
            return KEY_TO_TYPE[k]

    return "K"


def _build_text_blob(item: dict[str, Any]) -> str:

    parts = [
        item.get("name", ""),
        item.get("description", ""),
        "Job levels: "
        + ", ".join(item.get("job_levels", [])),
        "Test types: "
        + ", ".join(item.get("keys", [])),
        "Duration: "
        + item.get("duration", ""),
        "Languages: "
        + ", ".join(item.get("languages", [])),
        "Remote: "
        + item.get("remote", ""),
        "Adaptive: "
        + item.get("adaptive", ""),
    ]

    return " | ".join(
        p for p in parts if p.strip()
    )


def _normalise_raw(
    item: dict[str, Any]
) -> dict[str, Any]:

    entry = {
        "entity_id": item.get(
            "entity_id",
            "",
        ),

        "name": item.get(
            "name",
            "",
        ),

        "url": item.get(
            "link",
            "",
        ),

        "description": item.get(
            "description",
            "",
        ).strip(),

        "job_levels": item.get(
            "job_levels",
            [],
        ),

        "languages": item.get(
            "languages",
            [],
        ),

        "duration": item.get(
            "duration",
            "",
        ),

        "remote": item.get(
            "remote",
            "",
        ),

        "adaptive": item.get(
            "adaptive",
            "",
        ),

        "keys": item.get(
            "keys",
            [],
        ),

        "test_type": _derive_test_type(
            item.get("keys", [])
        ),
    }

    entry["text_blob"] = (
        _build_text_blob(entry)
    )

    return entry


def load_catalog() -> list[dict[str, Any]]:

    if not CACHE_PATH.exists():

        raise FileNotFoundError(
            f"Catalog file not found: "
            f"{CACHE_PATH}"
        )

    logger.info(
        "Loading catalog from %s",
        CACHE_PATH,
    )

    with open(
        CACHE_PATH,
        encoding="utf-8",
    ) as f:

        raw = json.load(f)

    catalog = []

    for item in raw:

        if item.get("status") != "ok":
            continue

        try:

            catalog.append(
                _normalise_raw(item)
            )

        except Exception as exc:

            logger.warning(
                "Skipping malformed item: %s",
                exc,
            )

    logger.info(
        "Loaded %d catalog entries",
        len(catalog),
    )

    if len(catalog) == 0:

        raise ValueError(
            "Catalog is empty."
        )

    return catalog