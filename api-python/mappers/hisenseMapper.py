from collections.abc import Callable
from enums import (
    Brand,
    FanSpeed,
    HisenseEco,
    HisenseFanSpeed,
    HisensePower,
    HisenseProperty,
    HisenseSleep,
    HisenseWorkMode,
    WorkMode,
)
from schemas import AcCommand, AcStatus

_HISENSE_TO_DOMAIN_MODE: dict[HisenseWorkMode, WorkMode] = {
    HisenseWorkMode.FAN: WorkMode.FAN,
    HisenseWorkMode.HEAT: WorkMode.HEAT,
    HisenseWorkMode.COOL: WorkMode.COOL,
    HisenseWorkMode.DRY: WorkMode.DRY,
    HisenseWorkMode.AUTO: WorkMode.AUTO,
}
_DOMAIN_TO_HISENSE_MODE: dict[WorkMode, HisenseWorkMode] = {
    domain: vendor for vendor, domain in _HISENSE_TO_DOMAIN_MODE.items()
}

_HISENSE_TO_DOMAIN_FAN: dict[HisenseFanSpeed, FanSpeed] = {
    HisenseFanSpeed.AUTO: FanSpeed.AUTO,
    HisenseFanSpeed.LOW: FanSpeed.LOW,
    HisenseFanSpeed.MEDIUM: FanSpeed.MEDIUM,
    HisenseFanSpeed.HIGH: FanSpeed.HIGH,
}
_DOMAIN_TO_HISENSE_FAN: dict[FanSpeed, HisenseFanSpeed] = {
    domain: vendor for vendor, domain in _HISENSE_TO_DOMAIN_FAN.items()
}


def _map_power(cmd: AcCommand) -> tuple[HisenseProperty, int]:
    vendor_power = HisensePower.ON if cmd.power else HisensePower.OFF
    return HisenseProperty.POWER, int(vendor_power)


def _map_temp(cmd: AcCommand) -> tuple[HisenseProperty, int]:
    return HisenseProperty.TARGET_TEMP, cmd.targetTemp if cmd.targetTemp is not None else 22


def _map_mode(cmd: AcCommand) -> tuple[HisenseProperty, int]:
    vendor_mode = _DOMAIN_TO_HISENSE_MODE[cmd.mode or WorkMode.COOL]
    return HisenseProperty.WORK_MODE, int(vendor_mode)


def _map_fan(cmd: AcCommand) -> tuple[HisenseProperty, int]:
    vendor_fan = _DOMAIN_TO_HISENSE_FAN[cmd.fanSpeed or FanSpeed.AUTO]
    return HisenseProperty.FAN_SPEED, int(vendor_fan)


def _map_eco(cmd: AcCommand) -> tuple[HisenseProperty, int]:
    vendor_eco = HisenseEco.ENABLED if cmd.eco else HisenseEco.DISABLED
    return HisenseProperty.ECO, int(vendor_eco)


def _map_sleep(cmd: AcCommand) -> tuple[HisenseProperty, int]:
    vendor_sleep = HisenseSleep.ENABLED if cmd.sleep else HisenseSleep.DISABLED
    return HisenseProperty.SLEEP, int(vendor_sleep)


_COMMAND_MAPPERS: dict[str, Callable[[AcCommand], tuple[HisenseProperty, int]]] = {
    "power": _map_power,
    "targetTemp": _map_temp,
    "mode": _map_mode,
    "fanSpeed": _map_fan,
    "eco": _map_eco,
    "sleep": _map_sleep,
}


class HisenseMapper:
    @staticmethod
    def _parse_work_mode(raw: str | int | None) -> WorkMode:
        try:
            vendor_enum = HisenseWorkMode(int(raw if raw is not None else HisenseWorkMode.COOL))
            return _HISENSE_TO_DOMAIN_MODE[vendor_enum]
        except ValueError:
            return WorkMode.COOL

    @staticmethod
    def _parse_fan_speed(raw: str | int | None) -> FanSpeed:
        try:
            vendor_enum = HisenseFanSpeed(int(raw if raw is not None else HisenseFanSpeed.AUTO))
            return _HISENSE_TO_DOMAIN_FAN[vendor_enum]
        except ValueError:
            return FanSpeed.AUTO

    @staticmethod
    def _parse_flag(raw: str | int | None, enabled_value: int) -> bool | None:
        if raw is None:
            return None
        try:
            return int(raw) == enabled_value
        except ValueError:
            return None

    @classmethod
    def to_status(cls, device_name: str, raw_status: dict[str, str]) -> AcStatus:
        raw_ambient = raw_status.get(HisenseProperty.AMBIENT_TEMP)
        return AcStatus(
            brand=Brand.HISENSE,
            deviceName=device_name,
            power=str(raw_status.get(HisenseProperty.POWER, "0")) == str(int(HisensePower.ON)),
            targetTemp=int(raw_status.get(HisenseProperty.TARGET_TEMP, 22)),
            ambientTemp=int(raw_ambient) if raw_ambient is not None else None,
            mode=cls._parse_work_mode(raw_status.get(HisenseProperty.WORK_MODE)),
            fanSpeed=cls._parse_fan_speed(raw_status.get(HisenseProperty.FAN_SPEED)),
            swing=None,
            eco=cls._parse_flag(raw_status.get(HisenseProperty.ECO), int(HisenseEco.ENABLED)),
            sleep=cls._parse_flag(raw_status.get(HisenseProperty.SLEEP), int(HisenseSleep.ENABLED)),
        )

    @staticmethod
    def to_vendor_payload(command: AcCommand) -> dict[str, int]:
        payload: dict[str, int] = {}
        for field in command.model_dump(exclude_none=True):
            mapper = _COMMAND_MAPPERS.get(field)
            if mapper:
                prop, encoded = mapper(command)
                payload[prop.value] = encoded
        return payload