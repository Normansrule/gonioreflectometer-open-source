"""Motion-controller client for grbl-family firmware: grblHAL (BTT SKR Pico, USB-C) or FluidNC (ESP32 boards).

Common protocol (grblHAL core [R83], FluidNC docs [R20]-[R30]):
  line commands answer "ok" or "error:N";  realtime: "?" status, "!" hold, "~" resume, 0x18 reset
  status: <Idle|MPos:x,y,z,a|FS:0,0|Pn:XY>   (values in axis order, unlabelled)
  $H home all, $HX one axis;  M62/M63 P<n> digital outputs
Firmware differences are in DIALECTS (driver re-init, motor sleep/wake, machine position after homing).
"""
from __future__ import annotations

import re
import socket
import time
from dataclasses import dataclass, field
from typing import Protocol

AXIS_ORDER = "XYZABC"

DIALECTS = {
    # grblHAL: Trinamic plugin re-inits the TMC2209s with M122 I [R84]; $SLP = sleep (needs $62=1, leave with a reset) [R83];
    # homing with $22 "force set origin" puts the machine position at 0 on the switch [R83].
    "grblhal": {"reinit": "M122 I", "sleep": "$SLP", "wake": None, "origin_at_home": True, "usb_vid": 0x2E8A},
    # FluidNC: $MI re-init [R28]; $MD / $ME motors off / on; homing.mpos_mm puts the machine position at home_deg.
    "fluidnc": {"reinit": "$MI", "sleep": "$MD", "wake": "$ME", "origin_at_home": False, "usb_vid": 0x1A86},
}


def dialect(cfg) -> dict:
    """Controller dialect from machine.yaml controller.firmware (default grblhal)."""
    name = str(cfg.controller.get("firmware", "grblhal")).lower()
    if name not in DIALECTS:
        raise ValueError(f"controller.firmware must be one of {sorted(DIALECTS)}, not {name!r}")
    return DIALECTS[name]


def home_mpos(cfg) -> dict[str, float]:
    """Controller machine position right after homing each axis (keyed by controller axis letter)."""
    zero = dialect(cfg)["origin_at_home"]
    return {a.fluidnc_axis: (0.0 if zero else a.home_deg) for a in cfg.axes.values()}


def switch_edges(cfg, pulloff_deg: float | None = None) -> dict[str, tuple[float, float]]:
    """Where each home switch trips, in controller units: (position, direction of travel into it). Homing stops one
    pull-off away from it, on the travel side."""
    pull = float((getattr(cfg, "slip", None) or {}).get("pulloff_deg", 2.0)) if pulloff_deg is None else pulloff_deg
    homes = home_mpos(cfg)
    return {a.fluidnc_axis: (homes[a.fluidnc_axis] + way * pull, way)
            for a in cfg.axes.values() for way in [-1.0 if a.home_deg == a.min_deg else 1.0]}


STATUS_RE = re.compile(r"<([A-Za-z]+)(?::\d+)?\|MPos:([-\d.,]+)(?:\|.*?Pn:([A-Z]*))?")


class Transport(Protocol):
    def write(self, data: bytes) -> None: ...
    def readline(self, timeout: float) -> str: ...
    def close(self) -> None: ...


class SerialTransport:  # pragma: no cover - needs hardware
    """USB serial: the SKR Pico's USB-C (RP2040, USB VID 0x2E8A) or an ESP32 board's CH340 (0x1A86)."""

    def __init__(self, port: str = "auto", baud: int = 115200, usb_vid: int = 0x2E8A):
        import serial
        from serial.tools import list_ports
        if port == "auto":
            found = [p.device for p in list_ports.comports() if p.vid == usb_vid]
            if not found:
                raise RuntimeError(f"no controller with USB VID {usb_vid:#06x} found; set controller.port in machine.yaml")
            port = found[0]
        self.s = serial.Serial(port, baud, timeout=0.1)
        time.sleep(2.0)                      # ESP32 boards reset when the port opens; harmless wait on the RP2040
        self.s.reset_input_buffer()

    def write(self, data: bytes) -> None:
        self.s.write(data)

    def readline(self, timeout: float) -> str:
        self.s.timeout = timeout
        return self.s.readline().decode(errors="replace").strip()

    def close(self) -> None:
        self.s.close()


class TcpTransport:  # pragma: no cover - needs hardware
    """WiFi: FluidNC telnet server on port 23 [R24] (ESP32 boards only; the SKR Pico has no WiFi)."""

    def __init__(self, host: str = "fluidnc.local", port: int = 23):
        self.sock = socket.create_connection((host, port), timeout=5)
        self.buf = b""

    def write(self, data: bytes) -> None:
        self.sock.sendall(data)

    def readline(self, timeout: float) -> str:
        self.sock.settimeout(timeout)
        while b"\n" not in self.buf:
            try:
                chunk = self.sock.recv(1024)
            except socket.timeout:
                return ""
            if not chunk:
                return ""
            self.buf += chunk
        line, self.buf = self.buf.split(b"\n", 1)
        return line.decode(errors="replace").strip()

    def close(self) -> None:
        self.sock.close()


class FluidNCError(RuntimeError):
    pass


@dataclass
class Status:
    state: str
    mpos: dict[str, float]
    pins: str = ""


def parse_status(line: str) -> Status | None:
    m = STATUS_RE.search(line)
    if not m:
        return None
    vals = [float(v) for v in m.group(2).split(",")]
    return Status(m.group(1), dict(zip(AXIS_ORDER, vals)), m.group(3) or "")


class FluidNC:
    def __init__(self, transport: Transport, timeout_s: float = 120.0):
        self.t, self.timeout_s = transport, timeout_s

    def command(self, line: str) -> list[str]:
        """Send one line, return any text before 'ok'. Raises on 'error:'/'ALARM:'."""
        self.t.write((line.strip() + "\n").encode())
        out, deadline = [], time.monotonic() + self.timeout_s
        while time.monotonic() < deadline:
            resp = self.t.readline(0.5)
            if not resp:
                continue
            if resp == "ok":
                return out
            if resp.startswith(("error", "ALARM")):
                raise FluidNCError(f"{line!r} -> {resp}")
            out.append(resp)
        raise FluidNCError(f"timeout waiting for ok after {line!r}")

    def realtime(self, ch: bytes) -> None:
        self.t.write(ch)

    def status(self) -> Status:
        self.realtime(b"?")
        deadline = time.monotonic() + 2.0
        while time.monotonic() < deadline:
            s = parse_status(self.t.readline(0.3))
            if s:
                return s
        raise FluidNCError("no status report")

    def wait_idle(self, poll_s: float = 0.1) -> Status:
        deadline = time.monotonic() + self.timeout_s
        while time.monotonic() < deadline:
            s = self.status()
            if s.state == "Idle":
                return s
            if s.state in ("Alarm", "Door"):
                raise FluidNCError(f"controller in {s.state}")
            if s.state == "Hold":               # feed hold ('!'): wait as long as it takes
                deadline = time.monotonic() + self.timeout_s
            time.sleep(poll_s)
        raise FluidNCError("timeout waiting for Idle")

    # convenience ------------------------------------------------------------
    def hold(self) -> None:
        self.realtime(b"!")

    def resume(self) -> None:
        self.realtime(b"~")

    def reset(self) -> None:
        self.realtime(b"\x18")


@dataclass
class RecordingTransport:
    """Offline stand-in: answers 'ok', records every line and tracks the machine position like the controller
    (G53 G1 moves the axes, $H<axis> puts an axis at homes[axis]) so endpoint checks work in dry runs and tests.
    for_machine() sets homes from the configured firmware: 0 for grblHAL, home_deg for FluidNC.
    Slip (off unless set): `phys` is where each axis really is; every move adds creep[axis] degrees per degree travelled
    and any one-off jump[axis] (lost steps). `edges` = {axis: (position, direction)} of the home switches: the status
    report then carries Pn:<axes on their switch>, read from phys, as the real pins would."""
    lines: list[str] = field(default_factory=list)
    pending: list[str] = field(default_factory=list)
    mpos: dict[str, float] = field(default_factory=lambda: dict.fromkeys(AXIS_ORDER[:4], 0.0))
    homes: dict[str, float] = field(default_factory=dict)
    state: str = "Idle"
    phys: dict[str, float] = field(default_factory=dict)
    creep: dict[str, float] = field(default_factory=dict)
    jump: dict[str, float] = field(default_factory=dict)
    edges: dict[str, tuple[float, float]] = field(default_factory=dict)

    def where(self, axis: str) -> float:
        """Physical position of an axis (controller units): the count plus whatever slipped."""
        return self.phys.get(axis, self.mpos[axis])

    def write(self, data: bytes) -> None:
        txt = data.decode()
        if txt == "?":
            vals = ",".join(f"{self.mpos[a]:.4f}" for a in AXIS_ORDER[:4])
            pins = "".join(a for a, (at, way) in sorted(self.edges.items()) if (self.where(a) - at) * way >= -1e-9)
            self.pending.append(f"<{self.state}|MPos:{vals}|FS:0,0" + (f"|Pn:{pins}>" if pins else ">"))
            return
        if len(txt) == 1:                 # other realtime bytes
            self.lines.append(repr(txt))
            return
        line = txt.strip()
        if line.startswith("$H") and len(line) == 3 and line[2] in self.mpos:
            self.mpos[line[2]] = self.homes.get(line[2], self.mpos[line[2]])
            self.phys[line[2]] = self.mpos[line[2]]               # the switch is the truth: slip is gone
        elif line.startswith("G53 G1"):
            for k, v in re.findall(r"([XYZA])(-?[\d.]+)", line.split("F")[0]):
                step = float(v) - self.mpos[k]
                self.phys[k] = self.where(k) + step + self.creep.get(k, 0.0) * abs(step) + (self.jump.pop(k, 0.0) if step else 0.0)
                self.mpos[k] = float(v)
        elif line == "$I":
            self.pending.append("[VER:recording transport]")
        self.lines.append(line)
        self.pending.append("ok")

    def readline(self, timeout: float) -> str:
        return self.pending.pop(0) if self.pending else ""

    def close(self) -> None:
        pass

    @classmethod
    def for_machine(cls, cfg) -> "RecordingTransport":
        """Homes like the real controller of the configured firmware (home_mpos)."""
        t = cls()
        t.homes = home_mpos(cfg)
        t.edges = switch_edges(cfg)
        return t
