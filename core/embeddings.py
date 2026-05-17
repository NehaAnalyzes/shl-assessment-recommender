"""
embeddings.py

Lightweight TF-IDF retrieval system.
No GPU, torch, or transformers required.
"""

import logging
import pickle
from pathlib import Path
from typing import Any

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

logger = logging.getLogger(__name__)

VECTORIZER_PATH = (
    Path(__file__).parent.parent
    / "data"
    / "tfidf_vectorizer.pkl"
)

MATRIX_PATH = (
    Path(__file__).parent.parent
    / "data"
    / "tfidf_matrix.pkl"
)

META_PATH = (
    Path(__file__).parent.parent
    / "data"
    / "catalog_meta.pkl"
)

_vectorizer = None
_matrix = None
_meta = None


def build_index(
    catalog: list[dict[str, Any]],
    force: bool = False,
):

    if (
        not force
        and VECTORIZER_PATH.exists()
        and MATRIX_PATH.exists()
        and META_PATH.exists()
    ):

        logger.info(
            "TF-IDF index already exists."
        )

        return

    if not catalog:
        raise ValueError("Catalog empty.")

    blobs = [
        item["text_blob"]
        for item in catalog
    ]

    logger.info(
        "Building TF-IDF matrix..."
    )

    vectorizer = TfidfVectorizer(
        stop_words="english",
        max_features=5000,
    )

    matrix = vectorizer.fit_transform(
        blobs
    )

    VECTORIZER_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with open(
        VECTORIZER_PATH,
        "wb",
    ) as f:

        pickle.dump(vectorizer, f)

    with open(
        MATRIX_PATH,
        "wb",
    ) as f:

        pickle.dump(matrix, f)

    with open(
        META_PATH,
        "wb",
    ) as f:

        pickle.dump(catalog, f)

    logger.info(
        "TF-IDF index built successfully."
    )


def load_index():

    global _vectorizer, _matrix, _meta

    if (
        _vectorizer is not None
        and _matrix is not None
        and _meta is not None
    ):

        return (
            _vectorizer,
            _matrix,
            _meta,
        )

    with open(
        VECTORIZER_PATH,
        "rb",
    ) as f:

        _vectorizer = pickle.load(f)

    with open(
        MATRIX_PATH,
        "rb",
    ) as f:

        _matrix = pickle.load(f)

    with open(
        META_PATH,
        "rb",
    ) as f:

        _meta = pickle.load(f)

    logger.info(
        "TF-IDF index loaded."
    )

    return (
        _vectorizer,
        _matrix,
        _meta,
    )


def search(
    query: str,
    top_k: int = 10,
):

    vectorizer, matrix, meta = load_index()

    query_vec = vectorizer.transform(
        [query]
    )

    similarities = cosine_similarity(
        query_vec,
        matrix,
    )[0]

    top_indices = np.argsort(
        similarities
    )[::-1][:top_k]

    results = []

    for idx in top_indices:

        item = meta[idx].copy()

        item["score"] = float(
            similarities[idx]
        )

        results.append(item)

    return results