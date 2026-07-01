"""Entry point for running the Spark platform."""
import uvicorn
from src.api.app import app


def main() -> None:
    """Start the FastAPI server."""
    uvicorn.run(
        "src.api.app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )


if __name__ == "__main__":
    main()