"""
build_catalog.py

Builds embeddings + vector index from local SHL catalog.

Expected file:
    data/catalog.json

Usage:
    python build_catalog.py

Force rebuild:
    python build_catalog.py --force
"""

import logging
import sys
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

# ─────────────────────────────────────────────
# Logging
# ─────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────
# Paths
# ─────────────────────────────────────────────

BASE_DIR = Path(__file__).parent

DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

# Make root importable
sys.path.insert(0, str(BASE_DIR))

# ─────────────────────────────────────────────
# Imports
# ─────────────────────────────────────────────

from core.catalog import (
    load_catalog,
    CACHE_PATH,
)

from core.embeddings import (
    build_index,
)

# ─────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────

if __name__ == "__main__":

    logger.info(
        "=== SHL Catalog Build Started ==="
    )

    force = "--force" in sys.argv

    # ─────────────────────────────────────────
    # Validate catalog exists
    # ─────────────────────────────────────────

    if not CACHE_PATH.exists():

        logger.error(
            "Missing catalog file:"
        )

        logger.error(
            str(CACHE_PATH)
        )

        logger.error(
            "Place the SHL dataset JSON at:"
        )

        logger.error(
            "data/catalog.json"
        )

        sys.exit(1)

    # ─────────────────────────────────────────
    # Load catalog
    # ─────────────────────────────────────────

    try:

        catalog = load_catalog()

    except Exception as exc:

        logger.exception(
            "Failed to load catalog: %s",
            exc,
        )

        sys.exit(1)

    # ─────────────────────────────────────────
    # Validation
    # ─────────────────────────────────────────

    if not catalog:

        logger.error(
            "Catalog is empty."
        )

        sys.exit(1)

    logger.info(
        "Catalog size: %d entries",
        len(catalog),
    )

    # ─────────────────────────────────────────
    # Build vector index
    # ─────────────────────────────────────────

    try:

        logger.info(
            "Building vector index..."
        )

        build_index(
            catalog,
            force=force,
        )

    except Exception as exc:

        logger.exception(
            "Embedding/index build failed: %s",
            exc,
        )

        sys.exit(1)

    # ─────────────────────────────────────────
    # Done
    # ─────────────────────────────────────────

    logger.info(
        "=== Build complete ==="
    )

    logger.info(
        "Vector index ready."
    )

    logger.info(
        "data/ is ready for deployment."
    )