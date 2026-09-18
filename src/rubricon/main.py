"""FastAPI application entrypoint."""

from fastapi import FastAPI
from rubricon import __version__

app = FastAPI(
    title="Rubricon",
    description="Score support conversations against a versioned rubric",
    version=__version__,
)


@app.get("/health", tags=["ops"])
def health() -> dict[str,str]:
    """Liveness probe: is this process alive and able to answer?
    
    Deliberately has no dependencies - no database, no external calls.
    """
    return{"status": "ok", "version": __version__}