from collections.abc import Awaitable, Callable
from typing import TypeVar
from fastapi import HTTPException
from msmart.cloud import CloudError, NetHomePlusCloud, SmartHomeCloud
from msmart.device import AirConditioner as MideaAC
from msmart.discover import Discover
from msmart.lan import AuthenticationError, Security
from adapters.baseAdapter import BaseAcAdapter
from config.session import SessionManager
from enums import MIDEA_AC_DEVICE_TYPE, MIDEA_PORT
from mappers import MideaMapper
from schemas import AcCommand, AcStatus, MideaSession

T = TypeVar("T")


class MideaAdapter(BaseAcAdapter[MideaSession]):
    def __init__(self, session_manager: SessionManager) -> None:
        self.session_manager = session_manager
        self.device: MideaAC | None = None
        self.session: MideaSession | None = None

    def _require_device(self) -> tuple[MideaAC, MideaSession]:
        if not self.device or not self.session:
            raise HTTPException(status_code=401, detail="Sessão Midea não inicializada.")
        return self.device, self.session

    async def _discover_ip(self, device_id: int) -> str:
        discovered = await Discover.discover(auto_connect=False)
        matched = next((d.ip for d in discovered if d.id == device_id and d.ip), None)
        if not matched:
            raise HTTPException(
                status_code=504,
                detail="Ar-condicionado Midea não encontrado na rede local (UDP).",
            )
        return matched

    async def _recover_dhcp_ip(self) -> None:
        _, current_session = self._require_device()
        new_ip = await self._discover_ip(current_session.device_id)
        updated_session = current_session.model_copy(update={"ip": new_ip})
        self.session_manager.save(updated_session)
        await self.restore(updated_session)

    async def _run_with_dhcp_recovery(self, operation: Callable[[MideaAC], Awaitable[T]]) -> T:
        device, _ = self._require_device()
        try:
            return await operation(device)
        except Exception:
            await self._recover_dhcp_ip()
            refreshed_device, _ = self._require_device()
            return await operation(refreshed_device)

    async def _get_cloud_client(self, email: str, password: str):
        for cloud_cls in [SmartHomeCloud, NetHomePlusCloud]:
            try:
                cloud = cloud_cls(account=email, password=password)
                await cloud.login()
                return cloud
            except CloudError:
                continue
        raise HTTPException(
            status_code=401,
            detail="Falha ao autenticar na nuvem Midea. Verifique seu e-mail e senha.",
        )

    async def _fetch_keys(self, cloud, device_id: int) -> tuple[str, str]:
        for endian in ["little", "big"]:
            udpid = Security.udpid(device_id.to_bytes(6, endian)).hex()
            try:
                token, key = await cloud.get_token(udpid, device_id)
                return token, key
            except CloudError:
                continue
        raise HTTPException(
            status_code=404,
            detail="Não foi possível obter token/chave de criptografia para o aparelho Midea.",
        )

    async def login(self, email: str, password: str) -> MideaSession:
        discovered = await Discover.discover(auto_connect=False)
        if not discovered:
            raise HTTPException(
                status_code=504,
                detail="Nenhum ar-condicionado Midea encontrado na rede local (UDP).",
            )

        target = next(
            (d for d in discovered if getattr(d, "type", None) == MIDEA_AC_DEVICE_TYPE),
            discovered[0],
        )

        cloud = await self._get_cloud_client(email, password)
        token, key = await self._fetch_keys(cloud, target.id)

        session = MideaSession(
            device_id=int(target.id),
            device_name=getattr(target, "name", None) or "Midea Split",
            ip=target.ip,
            token=token.hex() if isinstance(token, bytes) else str(token),
            key=key.hex() if isinstance(key, bytes) else str(key),
        )
        await self.restore(session)
        return session

    async def restore(self, session: MideaSession) -> None:
        self.session = session
        dev = MideaAC(ip=session.ip, port=MIDEA_PORT, device_id=session.device_id)
        try:
            await dev.authenticate(session.token, session.key)
        except AuthenticationError as e:
            raise HTTPException(
                status_code=401,
                detail=f"Falha na autenticação local LAN com o ar-condicionado Midea: {e}",
            )
        self.device = dev

    async def get_status(self) -> AcStatus:
        await self._run_with_dhcp_recovery(lambda dev: dev.refresh())
        device, session = self._require_device()
        return MideaMapper.to_status(device, session)

    async def send_command(self, command: AcCommand) -> AcStatus:
        async def _apply_and_send(dev: MideaAC) -> None:
            MideaMapper.apply_command(dev, command)
            await dev.apply()

        await self._run_with_dhcp_recovery(_apply_and_send)
        device, session = self._require_device()
        return MideaMapper.to_status(device, session)
