import os
from pathlib import Path
from pydantic import TypeAdapter, ValidationError
from schemas import SessionData

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
            return None
        try:
            raw_json = self.file_path.read_text(encoding="utf-8")
            return _SESSION_ADAPTER.validate_json(raw_json)
        except (ValidationError, OSError):
            self.clear()
            return None

    def save(self, data: SessionData) -> None:
        self.file_path.write_text(
            data.model_dump_json(indent=2),
            encoding="utf-8",
        )

    def clear(self) -> None:
        if self.file_path.exists():
            self.file_path.unlink()