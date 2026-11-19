from collections.abc import Callable
from msmart.device import AirConditioner as MideaAC
from enums import Brand, FanSpeed, SwingMode, WorkMode
from schemas import AcCommand, AcStatus, MideaSession

_DOMAIN_TO_MIDEA_MODE: dict[WorkMode, MideaAC.OperationalMode] = {
    WorkMode.AUTO: MideaAC.OperationalMode.AUTO,
    WorkMode.COOL: MideaAC.OperationalMode.COOL,
    WorkMode.DRY: MideaAC.OperationalMode.DRY,
    WorkMode.HEAT: MideaAC.OperationalMode.HEAT,
    WorkMode.FAN: MideaAC.OperationalMode.FAN_ONLY,
}
_MIDEA_TO_DOMAIN_MODE: dict[MideaAC.OperationalMode, WorkMode] = {
    vendor: domain for domain, vendor in _DOMAIN_TO_MIDEA_MODE.items()
}

_DOMAIN_TO_MIDEA_FAN: dict[FanSpeed, MideaAC.FanSpeed] = {
    FanSpeed.AUTO: MideaAC.FanSpeed.AUTO,
    FanSpeed.LOW: MideaAC.FanSpeed.LOW,
    FanSpeed.MEDIUM: MideaAC.FanSpeed.MEDIUM,
    FanSpeed.HIGH: MideaAC.FanSpeed.HIGH,
}
_MIDEA_TO_DOMAIN_FAN: dict[MideaAC.FanSpeed, FanSpeed] = {
    vendor: domain for domain, vendor in _DOMAIN_TO_MIDEA_FAN.items()
}

_DOMAIN_TO_MIDEA_SWING: dict[SwingMode, MideaAC.SwingMode] = {
    SwingMode.OFF: MideaAC.SwingMode.OFF,
    SwingMode.VERTICAL: MideaAC.SwingMode.VERTICAL,
}


def _apply_power(dev: MideaAC, cmd: AcCommand) -> None:
    if cmd.power is not None:
        dev.power_state = cmd.power


def _apply_temp(dev: MideaAC, cmd: AcCommand) -> None:
    if cmd.targetTemp is not None:
        dev.target_temperature = float(cmd.targetTemp)


def _apply_mode(dev: MideaAC, cmd: AcCommand) -> None:
    if cmd.mode is not None:
        dev.operational_mode = _DOMAIN_TO_MIDEA_MODE[cmd.mode]


def _apply_fan(dev: MideaAC, cmd: AcCommand) -> None:
    if cmd.fanSpeed is not None:
        dev.fan_speed = _DOMAIN_TO_MIDEA_FAN[cmd.fanSpeed]


def _apply_swing(dev: MideaAC, cmd: AcCommand) -> None:
    if cmd.swing is not None:
        dev.swing_mode = _DOMAIN_TO_MIDEA_SWING[cmd.swing]


def _apply_eco(dev: MideaAC, cmd: AcCommand) -> None:
    if cmd.eco is not None:
        dev.eco_mode = cmd.eco


def _apply_sleep(dev: MideaAC, cmd: AcCommand) -> None:
    if cmd.sleep is not None:
        dev.sleep_mode = cmd.sleep


_COMMAND_APPLIERS: dict[str, Callable[[MideaAC, AcCommand], None]] = {
    "power": _apply_power,
    "targetTemp": _apply_temp,
    "mode": _apply_mode,
    "fanSpeed": _apply_fan,
    "swing": _apply_swing,
    "eco": _apply_eco,
    "sleep": _apply_sleep,
}


class MideaMapper:
    @staticmethod
    def to_status(device: MideaAC, session: MideaSession) -> AcStatus:
        swing_active = bool(getattr(device, "swing_vertical", False))
        indoor_temp = device.indoor_temperature
        return AcStatus(
            brand=Brand.MIDEA,
            deviceName=session.device_name,
            power=bool(device.power_state),
            targetTemp=int(device.target_temperature),
            ambientTemp=int(indoor_temp) if indoor_temp is not None else None,
            mode=_MIDEA_TO_DOMAIN_MODE.get(device.operational_mode, WorkMode.COOL),
            fanSpeed=_MIDEA_TO_DOMAIN_FAN.get(device.fan_speed, FanSpeed.AUTO),
            swing=SwingMode.VERTICAL if swing_active else SwingMode.OFF,
            eco=bool(getattr(device, "eco_mode", False)),
            sleep=bool(getattr(device, "sleep_mode", False)),
        )

    @staticmethod
    def apply_command(device: MideaAC, command: AcCommand) -> None:
        for field in command.model_dump(exclude_none=True):
            applier = _COMMAND_APPLIERS.get(field)
            if applier:
                applier(device, command)