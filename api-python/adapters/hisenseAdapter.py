from connectlife.api import (
    ConnectLifeApi,
    LifeConnectAuthError,
    LifeConnectError,
    LifeConnectTermsNotAcceptedError,
)
from connectlife.appliance import ConnectLifeAppliance
from fastapi import HTTPException
from adapters.baseAdapter import BaseAcAdapter
from config.logging import get_logger
from mappers import HisenseMapper
from schemas import AcCommand, AcStatus, HisenseSession

logger = get_logger("adapter.hisense")


class HisenseAdapter(BaseAcAdapter[HisenseSession]):
    def __init__(self) -> None:
        self.client: ConnectLifeApi | None = None

    def _require_device(self) -> tuple[ConnectLifeApi, ConnectLifeAppliance]:
        if not self.client:
            raise HTTPException(status_code=401, detail="Sessão Hisense não inicializada.")
        if not self.client.appliances:
            raise HTTPException(status_code=404, detail="Nenhum aparelho Hisense encontrado.")
        return self.client, self.client.appliances[0]

    @staticmethod
    def _handle_connectlife_error(exc: Exception, context: str) -> HTTPException:
        if isinstance(exc, LifeConnectAuthError):
            logger.warning("Falha de autenticação Hisense (%s): %s", context, exc)
            return HTTPException(
                status_code=401,
                detail="Credenciais Hisense inválidas. Verifique seu e-mail e senha.",
            )
        if isinstance(exc, LifeConnectTermsNotAcceptedError):
            logger.warning("Termos ConnectLife não aceitos (%s): %s", context, exc)
            return HTTPException(
                status_code=403,
                detail="Termos de uso ConnectLife não aceitos na conta Hisense.",
            )
        logger.error("Erro na nuvem Hisense (%s): %s", context, exc)
        return HTTPException(
            status_code=502,
            detail="Erro de comunicação com a nuvem Hisense.",
        )

    async def login(self, email: str, password: str) -> HisenseSession:
        logger.info("Iniciando login Hisense")
        self.client = ConnectLifeApi(email, password)
        try:
            await self.client.login()
            await self.client.get_appliances()
        except LifeConnectError as exc:
            self.client = None
            raise self._handle_connectlife_error(exc, "login") from exc

        _, device = self._require_device()
        logger.info("Login Hisense OK — device=%s", device.device_nickname)

        return HisenseSession(
            email=email,
            password=password,
            device_id=device.puid,
            device_name=device.device_nickname,
        )

    async def restore(self, session: HisenseSession) -> None:
        await self.login(session.email, session.password)

    async def get_status(self) -> AcStatus:
        client, _ = self._require_device()
        try:
            await client.get_appliances()
        except LifeConnectError as exc:
            raise self._handle_connectlife_error(exc, "get_status") from exc
        _, refreshed = self._require_device()
        return HisenseMapper.to_status(refreshed.device_nickname, refreshed.status_list)

    async def send_command(self, command: AcCommand) -> AcStatus:
        client, device = self._require_device()
        payload = HisenseMapper.to_vendor_payload(command)

        if payload:
            try:
                await client.update_appliance(device.puid, payload)
            except LifeConnectError as exc:
                raise self._handle_connectlife_error(exc, "send_command") from exc

        return await self.get_status()