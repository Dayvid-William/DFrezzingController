import os
from pathlib import Path
from pydantic import TypeAdapter, ValidationError
from config.logging import get_logger
from schemas import SessionData

logger = get_logger("session")

_SESSION_ADAPTER: TypeAdapter[SessionData] = TypeAdapter(SessionData)


class SessionManager:
    def __init__(self, base_dir: Path | None = None) -> None:
        if base_dir is None:
            base_dir = Path(os.getenv("APPDATA", Path.home())) / "ac-controller"
        try:
            base_dir.mkdir(parents=True, exist_ok=True)
        except OSError:
            # Fallback seguro para o diretório da aplicação caso APPDATA não tenha permissão
            base_dir = Path(__file__).resolve().parent.parent / ".session"
            base_dir.mkdir(parents=True, exist_ok=True)
        self.file_path = base_dir / "session.json"

    def load(self) -> SessionData | None:
        if not self.file_path.exists():
            logger.debug("Nenhum arquivo de sessão encontrado em %s", self.file_path)
            return None
        try:
            raw_json = self.file_path.read_text(encoding="utf-8")
            session = _SESSION_ADAPTER.validate_json(raw_json)
            logger.info("Sessão carregada (brand=%s)", session.brand.value)
            return session
        except (ValidationError, OSError) as exc:
            logger.warning("Sessão corrompida ou ilegível (%s) — removendo", exc)
            self.clear()
            return None

    def save(self, data: SessionData) -> None:
        self.file_path.write_text(
            data.model_dump_json(indent=2),
            encoding="utf-8",
        )
        logger.info("Sessão salva em %s", self.file_path)

    def clear(self) -> None:
        if self.file_path.exists():
            self.file_path.unlink()
            logger.info("Sessão removida")