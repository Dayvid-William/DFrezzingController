from pydantic import BaseModel, Field
from enums import Brand, FanSpeed, SwingMode, WorkMode


class LoginRequest(BaseModel):
    brand: Brand
    email: str
    password: str


class AcStatus(BaseModel):
    brand: Brand
    deviceName: str
    power: bool
    targetTemp: int
    ambientTemp: int | None = None
    mode: WorkMode
    fanSpeed: FanSpeed
    swing: SwingMode | None = None
    eco: bool | None = None
    sleep: bool | None = None


class AcCommand(BaseModel):
    power: bool | None = None
    targetTemp: int | None = Field(default=None, ge=16, le=30)
    mode: WorkMode | None = None
    fanSpeed: FanSpeed | None = None
    swing: SwingMode | None = None
    eco: bool | None = None
    sleep: bool | None = None