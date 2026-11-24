from collections.abc import Callable
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from adapters import BaseAcAdapter, HisenseAdapter, MideaAdapter
from config import SessionManager, settings
from enums import Brand
from schemas import AcCommand, AcStatus, BaseSession, LoginRequest

session_manager = SessionManager()

ADAPTER_FACTORIES: dict[Brand, Callable[[], BaseAcAdapter[BaseSession]]] = {
    Brand.HISENSE: HisenseAdapter,  # type: ignore[dict-item]
    Brand.MIDEA: lambda: MideaAdapter(session_manager),  # type: ignore[dict-item]
}


def _create_adapter(brand: Brand) -> BaseAcAdapter[BaseSession]:
    return ADAPTER_FACTORIES[brand]()


async def _bootstrap_adapter() -> BaseAcAdapter[BaseSession] | None:
    saved = session_manager.load()
    if saved:
        adapter = _create_adapter(saved.brand)
        await adapter.restore(saved)
        return adapter

    if settings.cl_user and settings.cl_pass:
        adapter = _create_adapter(Brand.HISENSE)
        session = await adapter.login(settings.cl_user, settings.cl_pass)
        session_manager.save(session)
        return adapter

    return None


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        app.state.adapter = await _bootstrap_adapter()
    except Exception:
        app.state.adapter = None
    yield


app = FastAPI(title=settings.app_title, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
    allow_credentials=[True]
)


def _require_adapter() -> BaseAcAdapter[BaseSession]:
    if app.state.adapter is None:
        raise HTTPException(
            status_code=401,
            detail="Nenhum aparelho pareado. Realize o login em POST /auth/login.",
        )
    return app.state.adapter


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "mode": "local",
        "hasSession": app.state.adapter is not None,
    }


@app.post("/auth/login")
async def auth_login(payload: LoginRequest):
    adapter = _create_adapter(payload.brand)
    session = await adapter.login(payload.email, payload.password)
    session_manager.save(session)
    app.state.adapter = adapter
    return {
        "ok": True,
        "brand": payload.brand,
        "deviceName": session.device_name,
    }


@app.post("/auth/logout")
async def auth_logout():
    session_manager.clear()
    app.state.adapter = None
    return {"ok": True}


@app.get("/ac/status", response_model=AcStatus)
async def get_ac_status():
    adapter = _require_adapter()
    return await adapter.get_status()


@app.post("/ac/command", response_model=AcStatus)
async def send_ac_command(payload: AcCommand):
    adapter = _require_adapter()
    return await adapter.send_command(payload)