"""Non-invasive functional validation for detected Apple hardware."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
import shutil
import subprocess
from typing import Iterable


@dataclass(frozen=True)
class TestResult:
    component: str
    check: str
    status: str
    evidence: str = ""
    command: str | None = None
    reason: str = ""

    def to_dict(self) -> dict:
        return asdict(self)


def _run(command: list[str], timeout: int = 5) -> tuple[int, str]:
    if not shutil.which(command[0]):
        return 127, ""
    try:
        p = subprocess.run(command, capture_output=True, text=True, timeout=timeout, check=False)
        return p.returncode, (p.stdout + p.stderr).strip()
    except (OSError, subprocess.TimeoutExpired):
        return 124, ""


def _exists(patterns: Iterable[str]) -> list[str]:
    found = []
    for pattern in patterns:
        found.extend(str(p) for p in Path("/").glob(pattern.lstrip("/")))
    return found


def _result(component: str, check: str, ok: bool, evidence: str, command: str | None = None) -> TestResult:
    return TestResult(component, check, "pass" if ok else "fail", evidence=evidence, command=command)


def _optional_command(component: str, check: str, command: list[str]) -> TestResult:
    rc, out = _run(command)
    if rc == 127:
        return TestResult(component, check, "skip", reason=f"{command[0]} is not installed", command=" ".join(command))
    if rc == 0:
        return _result(component, check, True, out[:1000] or "command completed", " ".join(command))
    return TestResult(component, check, "fail", out[:1000], " ".join(command), f"exit code {rc}")


def validate_component(component: str) -> list[TestResult]:
    c = component.lower()
    if c == "camera":
        nodes = _exists(["/dev/video*"])
        results = [_result(c, "v4l2-device", bool(nodes), ", ".join(nodes) or "no /dev/video* device")]
        if shutil.which("v4l2-ctl"):
            results.append(_optional_command(c, "v4l2-enumeration", ["v4l2-ctl", "--list-devices"]))
        else:
            results.append(TestResult(c, "v4l2-enumeration", "skip", reason="v4l2-ctl is not installed"))
        return results
    if c == "audio":
        card = Path("/proc/asound/cards").exists()
        results = [_result(c, "alsa-card", card, "/proc/asound/cards present" if card else "ALSA cards file absent")]
        results.append(_optional_command(c, "alsa-playback", ["aplay", "-l"]))
        return results
    if c == "wifi":
        interfaces = _exists(["/sys/class/net/*/wireless"])
        results = [_result(c, "wireless-interface", bool(interfaces), ", ".join(interfaces) or "no wireless sysfs interface")]
        results.append(_optional_command(c, "iw-dev", ["iw", "dev"]))
        return results
    if c == "bluetooth":
        bt = Path("/sys/class/bluetooth").exists() and bool(list(Path("/sys/class/bluetooth").glob("*")))
        return [_result(c, "bluetooth-controller", bt, "controller exposed by sysfs" if bt else "no controller in /sys/class/bluetooth")]
    if c == "graphics":
        drm = list(Path("/sys/class/drm").glob("card*")) if Path("/sys/class/drm").exists() else []
        dri = _exists(["/dev/dri/renderD*", "/dev/dri/card*"])
        return [
            _result(c, "drm-card", bool(drm), ", ".join(map(str, drm)) or "no DRM card"),
            _result(c, "dri-device", bool(dri), ", ".join(dri) or "no /dev/dri devices"),
            _optional_command(c, "opengl-info", ["glxinfo", "-B"]),
        ][-1] if False else [
            _result(c, "drm-card", bool(drm), ", ".join(map(str, drm)) or "no DRM card"),
            _result(c, "dri-device", bool(dri), ", ".join(dri) or "no /dev/dri devices"),
            _optional_command(c, "opengl-info", ["glxinfo", "-B"]),
        ]
    if c in {"keyboard", "trackpad"}:
        inputs = list(Path("/sys/class/input").glob("*")) if Path("/sys/class/input").exists() else []
        return [_result(c, "input-subsystem", bool(inputs), f"{len(inputs)} input entries" if inputs else "no input entries")]
    if c == "storage":
        blocks = list(Path("/sys/block").glob("*")) if Path("/sys/block").exists() else []
        return [_result(c, "block-device", bool(blocks), ", ".join(map(str, blocks)) or "no block devices")]
    if c == "thunderbolt":
        devices = list(Path("/sys/bus/thunderbolt/devices").glob("*")) if Path("/sys/bus/thunderbolt/devices").exists() else []
        return [_result(c, "thunderbolt-sysfs", bool(devices), ", ".join(map(str, devices)) or "no Thunderbolt devices")]
    if c in {"smc-thermal-fans", "thermal", "power"}:
        checks = []
        if c in {"smc-thermal-fans", "thermal"}:
            hwmon = list(Path("/sys/class/hwmon").glob("*")) if Path("/sys/class/hwmon").exists() else []
            thermal = list(Path("/sys/class/thermal").glob("*")) if Path("/sys/class/thermal").exists() else []
            smc = list(Path("/sys/devices/platform").glob("applesmc*")) if Path("/sys/devices/platform").exists() else []
            checks += [
                _result(c, "hwmon", bool(hwmon), f"{len(hwmon)} hwmon entries" if hwmon else "no hwmon entries"),
                _result(c, "thermal-zones", bool(thermal), f"{len(thermal)} thermal entries" if thermal else "no thermal entries"),
                _result(c, "applesmc", bool(smc), ", ".join(map(str, smc)) or "Apple SMC platform device not exposed"),
            ]
        if c == "power":
            cpufreq = list(Path("/sys/devices/system/cpu/cpufreq").glob("*")) if Path("/sys/devices/system/cpu/cpufreq").exists() else []
            checks.append(_result(c, "cpufreq", bool(cpufreq), f"{len(cpufreq)} cpufreq entries" if cpufreq else "no cpufreq policy entries"))
        return checks
    return [TestResult(c, "component-known", "unknown", reason="no validator registered")]


def validate(components: Iterable[str] | None = None) -> list[TestResult]:
    default = ("camera", "audio", "wifi", "bluetooth", "graphics", "keyboard", "trackpad",
               "storage", "thunderbolt", "smc-thermal-fans", "power")
    selected = tuple(components or default)
    results: list[TestResult] = []
    for component in selected:
        results.extend(validate_component(component))
    return results
