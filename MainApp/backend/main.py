import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.config import (
    ALLOWED_ORIGINS,
    APP_DESCRIPTION,
    APP_TITLE,
    APP_VERSION,
    SPACY_MODEL_PRIMARY,
    SPACY_MODEL_SECONDARY,
)

#from api.routes import router

logger = logging.getLogger("ats_resume_scorer")


@asynccontextmanager
async def lifespan(app: FastAPI):

    logger.info("Starting ATS Resume Analyzer API...")

    import spacy

    try:
        logger.info(f"Loading spaCy model: {SPACY_MODEL_PRIMARY}")

        app.state.nlp = spacy.load(SPACY_MODEL_PRIMARY)

        logger.info(
            f"Successfully loaded {SPACY_MODEL_PRIMARY}"
        )

    except OSError:

        logger.warning(
            f"{SPACY_MODEL_PRIMARY} not found. Falling back to {SPACY_MODEL_SECONDARY}"
        )

        app.state.nlp = spacy.load(SPACY_MODEL_SECONDARY)

        logger.info(
            f"Successfully loaded fallback model {SPACY_MODEL_SECONDARY}"
        )

    # SentenceTransformer will be loaded only when needed
    app.state.embedder = None

    logger.info("SentenceTransformer lazy loading enabled")
    logger.info("API startup completed.")

    yield

    logger.info("Shutting down ATS Resume Analyzer API...")


app = FastAPI(
    title=APP_TITLE,
    description=APP_DESCRIPTION,
    version=APP_VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#app.include_router(router)


@app.get("/")
async def root():

    return {
        "name": "ATS Resume Analyzer API",
        "version": APP_VERSION,
        "endpoints": {
            "POST /api/v1/analyze-resume": "Analyze a resume",
            "GET /api/v1/history": "Get user history",
            "DELETE /api/v1/history/{id}": "Delete a history entry",
            "GET /api/v1/health": "Health check",
            "POST /api/v1/generate-pdf": "Generate PDF report from data",
        },
    }


if __name__ == "__main__":

    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )