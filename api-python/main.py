from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from connectlife.api import ConnectLifeApi
from config import settings

client = ConnectLifeApi(settings.cl_user, settings.cl_pass)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await client.login()
    await client.get_appliances()
    yield


app = FastAPI(title=settings.app_title, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


def _get_primary_device():
    if not client.appliances:
        raise HTTPException(status_code=404, detail="Nenhum aparelho encontrado na conta ConnectLife.")
    return client.appliances[0]


@app.get("/status")
async def get_status():
    await client.get_appliances()
    device = _get_primary_device()
    return {
        "name": device.device_nickname,
        "status": device.status_list,
    }


@app.post("/control")
async def control(payload: dict[str, int | str]):
    device = _get_primary_device()
    await client.update_appliance(device.puid, payload)
    return {"ok": True, "sent": payload}