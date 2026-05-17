import logging
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)-8s %(name)s — %(message)s",
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):

    logger.info("=== SHL Recommender startup ===")

    from core.catalog import load_catalog
    from core.embeddings import (
        build_index,
        load_index,
        
    )

    catalog = load_catalog()

    build_index(catalog)

    load_index()

    logger.info("=== Startup complete ===")

    yield

    logger.info("=== SHL Recommender shutdown ===")


app = FastAPI(
    title="SHL Assessment Recommender",
    description="Conversational SHL assessment recommender",
    version="1.0.0",
    lifespan=lifespan,
)

from api.routes import router

app.include_router(router)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
    )