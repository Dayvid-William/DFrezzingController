from typing import Annotated, Literal
from pydantic import BaseModel, Field
from enums import Brand


class BaseSession(BaseModel):
    brand: Brand
    device_name: str


class HisenseSession(BaseSession):
    brand: Literal[Brand.HISENSE] = Brand.HISENSE
    email: str
    password: str
    device_id: str


class MideaSession(BaseSession):
    brand: Literal[Brand.MIDEA] = Brand.MIDEA
    device_id: int
    ip: str
    token: str
    key: str


SessionData = Annotated[
    HisenseSession | MideaSession,
    Field(discriminator="brand"),
]