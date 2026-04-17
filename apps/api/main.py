from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from apps.api.routes.chat import router as chat_router
from apps.api.routes.health import router as health_router
from apps.api.routes.sessions import router as sessions_router
from dayli.core.config import get_settings

settings = get_settings()
app = FastAPI(title="Dayli API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(health_router)
app.include_router(chat_router, prefix="/v1")
app.include_router(sessions_router, prefix="/v1")

_WEB_DIR = Path(__file__).parent.parent / "web"

@app.get("/", include_in_schema=False)
async def serve_ui() -> FileResponse:
    return FileResponse(_WEB_DIR / "index.html")

app.mount("/", StaticFiles(directory=_WEB_DIR), name="web")
