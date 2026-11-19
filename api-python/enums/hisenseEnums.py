from enum import IntEnum, StrEnum


class HisenseProperty(StrEnum):
    POWER = "t_power"
    TARGET_TEMP = "t_temp"
    TEMP_TYPE = "t_temp_type"
    WORK_MODE = "t_work_mode"
    FAN_SPEED = "t_fan_speed"
    ECO = "t_eco"
    SLEEP = "t_sleep"
    AMBIENT_TEMP = "f_temp_in"


class HisensePower(IntEnum):
    OFF = 0
    ON = 1


class HisenseTempType(IntEnum):
    CELSIUS = 0
    FAHRENHEIT = 1


class HisenseWorkMode(IntEnum):
    FAN = 0
    HEAT = 1
    COOL = 2
    DRY = 3
    AUTO = 4


class HisenseFanSpeed(IntEnum):
    AUTO = 0
    LOW = 2
    MEDIUM = 3
    HIGH = 4


class HisenseEco(IntEnum):
    DISABLED = 0
    ENABLED = 1


class HisenseSleep(IntEnum):
    DISABLED = 0
    ENABLED = 1