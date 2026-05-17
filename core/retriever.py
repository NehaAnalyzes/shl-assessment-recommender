"""
retriever.py

Lightweight semantic retrieval using TF-IDF similarity.
"""

import logging
from typing import Any

from core.embeddings import search, load_index

logger = logging.getLogger(__name__)


def retrieve(
    query: str,
    top_k: int = 10,
) -> list[dict[str, Any]]:

    """
    Return top-K catalog entries
    relevant to the query.
    """

    if not query.strip():

        return []

    results = search(
        query=query,
        top_k=top_k,
    )

    logger.debug(
        "Retrieved %d results for query: %.80s",
        len(results),
        query,
    )

    return results


def retrieve_by_names(
    names: list[str],
) -> list[dict[str, Any]]:

    """
    Lookup assessments using
    known aliases.
    """

    _, _, meta = load_index()

    alias_map = {
        "opq": "Occupational Personality Questionnaire",
        "gsa": "Global Skills Assessment",
    }

    results = []

    for target in names:

        target = target.lower()

        canonical = alias_map.get(
            target,
            target,
        )

        for item in meta:

            item_name = item.get(
                "name",
                "",
            ).lower()

            if canonical.lower() in item_name:

                results.append(item)
                break

    return results