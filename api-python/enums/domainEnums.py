from enum import StrEnum


class Brand(StrEnum):
    HISENSE = "hisense"
    MIDEA = "midea"


class WorkMode(StrEnum):
    AUTO = "auto"
    COOL = "cool"
    DRY = "dry"
    HEAT = "heat"
    FAN = "fan"


class FanSpeed(StrEnum):
    AUTO = "auto"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class SwingMode(StrEnum):
    OFF = "off"
    VERTICAL = "vertical"