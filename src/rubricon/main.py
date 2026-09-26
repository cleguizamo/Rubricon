"""FastAPI application entrypoint."""

import logging

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from rubricon import __version__
from rubricon.db.session import get_session

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Rubricon",
    description="Score support conversations against a versioned rubric",
    version=__version__,
)


@app.get("/health", tags=["ops"])
def health() -> dict[str, str]:
    """Liveness probe: is this process alive and able to answer?

    Deliberately has no dependencies - no database, no external calls.
    """
    return {"status": "ok", "version": __version__}

@app.get("/readyz", tags=["ops"])
def readyz(db: Session =
        Depends(get_session)) -> dict[str, str]:
    """Readiness probe: is this process ready to serve requests?

    This endpoint has a dependency on the database,
    so it will fail if the database is not reachable.
    """
    try:
        db.execute(text("SELECT 1"))
    except SQLAlchemyError as e:
        logger.exception("Database not reachable")
        raise HTTPException(status_code=503, detail="Database not reachable") from e
    return {"status": "ready"}
