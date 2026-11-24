from connectlife.api import ConnectLifeApi
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

    async def login(self, email: str, password: str) -> HisenseSession:
        logger.info("Iniciando login Hisense")
        self.client = ConnectLifeApi(email, password)
        await self.client.login()
        await self.client.get_appliances()
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
        await client.get_appliances()
        _, refreshed = self._require_device()
        return HisenseMapper.to_status(refreshed.device_nickname, refreshed.status_list)

    async def send_command(self, command: AcCommand) -> AcStatus:
        client, device = self._require_device()
        payload = HisenseMapper.to_vendor_payload(command)

        if payload:
            await client.update_appliance(device.puid, payload)

        return await self.get_status()