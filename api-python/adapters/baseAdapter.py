from abc import ABC, abstractmethod
from typing import Generic, TypeVar
from schemas import AcCommand, AcStatus, BaseSession

SessionT = TypeVar("SessionT", bound=BaseSession)


class BaseAcAdapter(ABC, Generic[SessionT]):
    @abstractmethod
    async def login(self, email: str, password: str) -> SessionT:
        """Autentica na nuvem da marca e retorna a sessão tipada para persistência."""

    @abstractmethod
    async def restore(self, session: SessionT) -> None:
        """Restaura a sessão ativa a partir dos dados persistidos."""

    @abstractmethod
    async def get_status(self) -> AcStatus:
        """Consulta e retorna o estado normalizado do aparelho."""

    @abstractmethod
    async def send_command(self, command: AcCommand) -> AcStatus:
        """Aplica alterações parciais e retorna o estado atualizado."""