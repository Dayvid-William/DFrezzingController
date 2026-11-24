from collections.abc import Callable
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from adapters import BaseAcAdapter, HisenseAdapter, MideaAdapter
from config import SessionManager, get_logger, settings, setup_logging
from enums import Brand
from schemas import AcCommand, AcStatus, BaseSession, LoginRequest

setup_logging()
logger = get_logger("main")

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
        logger.info("Restaurando sessão salva (brand=%s)", saved.brand.value)
        adapter = _create_adapter(saved.brand)
        await adapter.restore(saved)
        return adapter

    if settings.cl_user and settings.cl_pass:
        logger.info("Login automático via variáveis de ambiente (Hisense)")
        adapter = _create_adapter(Brand.HISENSE)
        session = await adapter.login(settings.cl_user, settings.cl_pass)
        session_manager.save(session)
        return adapter

    logger.info("Nenhuma sessão encontrada — aguardando login via POST /auth/login")
    return None


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        app.state.adapter = await _bootstrap_adapter()
    except HTTPException:
        logger.warning("Bootstrap falhou (HTTPException) — API iniciada sem sessão")
        app.state.adapter = None
    except Exception:
        logger.exception("Erro inesperado durante bootstrap")
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


@app.exception_handler(Exception)
async def _unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Captura exceções não tratadas e retorna JSON limpo em vez de stacktrace."""
    logger.error(
        "%s %s — erro não tratado: %s",
        request.method,
        request.url.path,
        exc,
        exc_info=True,
    )
    return JSONResponse(
        status_code=500,
        content={"detail": "Erro interno do servidor."},
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
    logger.info("Login solicitado (brand=%s)", payload.brand.value)
    adapter = _create_adapter(payload.brand)
    session = await adapter.login(payload.email, payload.password)
    session_manager.save(session)
    app.state.adapter = adapter
    logger.info("Login realizado com sucesso (device=%s)", session.device_name)
    return {
        "ok": True,
        "brand": payload.brand,
        "deviceName": session.device_name,
    }


@app.post("/auth/logout")
async def auth_logout():
    session_manager.clear()
    app.state.adapter = None
    logger.info("Logout realizado")
    return {"ok": True}


@app.get("/ac/status", response_model=AcStatus)
async def get_ac_status():
    adapter = _require_adapter()
    return await adapter.get_status()


@app.post("/ac/command", response_model=AcStatus)
async def send_ac_command(payload: AcCommand):
    logger.info("Comando recebido: %s", payload.model_dump(exclude_none=True))
    adapter = _require_adapter()
    return await adapter.send_command(payload)