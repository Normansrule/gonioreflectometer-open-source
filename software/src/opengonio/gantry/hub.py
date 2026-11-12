"""Client for the ESP32-S3 panel + sensor hub (firmware/hub/main.py).

Lines from the hub:  "BTN <HOME|START|STOP|LIGHT|NEXT|PAUSE>", "POWER <0|1>", "ENC a b c d", "SPEC #<id> f1..f8 clear nir",
                     "BATT <source> <V> <A> <W> <Wh used> <state>" (INA219, stage 17), "PONG ...", "ERR ..."
Lines to the hub:    "BAND <0-7>", "BAND OFF", "ENC?", "POWER?", "PING", "SHOW a|b|c" (OLED), "SPEC? <id>" (AS7341),
                     "BATT?", "SOURCE WALL|PACK|USBC [Wh]" (after a full charge)
Port: USB (laptop) or the Pi UART /dev/serial0 (standalone station).

One reader owns the line: every event that arrives while waiting for a sensor reply is kept in order and handed
out by poll(), never dropped. A STOP or POWER 0 that arrives during a sensor read also aborts that read
(SafetyInterrupt), so the caller stops the run at once.
"""
from __future__ import annotations

import time
from collections import deque
from dataclasses import dataclass, field

BUTTONS = ("HOME", "START", "STOP", "LIGHT", "NEXT", "PAUSE")
N_SPECTRAL = 10
MAX_LINE = 256


@dataclass
class HubEvent:
    kind: str           # BTN | POWER | ENC | PONG | SPEC | BATT | ERR
    value: str


class SafetyInterrupt(RuntimeError):
    """STOP pressed or motion power lost while the host was waiting on the hub; the event stays queued."""


def parse(line: str) -> HubEvent | None:
    if not isinstance(line, str):
        return None
    line = line.strip("\r\n")
    if len(line) > MAX_LINE or not line.isprintable():          # noise, binary garbage, unterminated junk
        return None
    parts = line.strip().split(maxsplit=1)
    if not parts or parts[0] not in ("BTN", "POWER", "ENC", "PONG", "SPEC", "BATT", "ERR"):
        return None
    ev = HubEvent(parts[0], parts[1] if len(parts) > 1 else "")
    if ev.kind == "BTN" and ev.value not in BUTTONS:
        return None
    if ev.kind == "POWER" and ev.value not in ("0", "1"):
        return None
    return ev


SOURCES = ("WALL", "PACK", "USBC")
BATT_STATES = ("OK", "LOW", "CRIT", "NONE")


def parse_battery(value: str) -> dict:
    """'PACK 23.10 0.412 9.5 1.20 OK' -> {source, volts, amps, watts, used_wh, state} (ValueError if malformed).
    state NONE: no INA219 fitted, the numbers are zeros."""
    parts = value.split()
    if len(parts) != 6 or parts[0] not in SOURCES or parts[5] not in BATT_STATES:
        raise ValueError(f"BATT needs '<source> V A W Wh state', got {value!r}")
    volts, amps, watts, used = (float(x) for x in parts[1:5])
    return {"source": parts[0], "volts": volts, "amps": amps, "watts": watts, "used_wh": used, "state": parts[5]}


def is_safety(ev: HubEvent) -> bool:
    return (ev.kind == "BTN" and ev.value == "STOP") or (ev.kind == "POWER" and ev.value == "0")


def parse_spectral(value: str, req: int | None) -> list[int]:
    """'#<id> v1 .. v10' -> 10 ints in 0..65535 (ValueError otherwise, or if the id doesn't match)."""
    parts = value.split()
    if parts and parts[0].startswith("#"):
        rid, parts = int(parts[0][1:]), parts[1:]
        if req is not None and rid != req:
            raise ValueError(f"SPEC reply #{rid} does not answer request #{req}")
    elif req is not None:
        raise ValueError("SPEC reply without a request id (update the hub firmware)")
    vals = [int(x) for x in parts]
    if len(vals) != N_SPECTRAL or not all(0 <= v <= 65535 for v in vals):
        raise ValueError(f"SPEC reply needs {N_SPECTRAL} values in 0..65535, got {parts}")
    return vals


class HubBase:
    """Shared logic; subclasses provide send() and _readline()."""

    def __init__(self):
        self.pending: deque[HubEvent] = deque()
        self._req = 0

    def send(self, line: str) -> None:  # pragma: no cover - abstract
        raise NotImplementedError

    def _readline(self) -> str:  # pragma: no cover - abstract
        raise NotImplementedError

    def _next(self) -> HubEvent | None:
        return parse(self._readline())

    def poll(self) -> HubEvent | None:
        if self.pending:
            return self.pending.popleft()
        return self._next()

    def band(self, n: int | None) -> None:
        self.send("BAND OFF" if n is None else f"BAND {int(n)}")

    def show(self, *lines: str) -> None:
        self.send("SHOW " + "|".join(str(x).replace("|", "/") for x in lines))

    def spectral(self, timeout_s: float = 3.0, clock=time.monotonic) -> list[int]:
        """One AS7341 reading: 8 bands + clear + NIR (raw counts). Other events are queued for poll();
        STOP / POWER 0 also raise SafetyInterrupt. Raises RuntimeError on timeout, ValueError on a bad reply."""
        self._req = (self._req + 1) % 10000
        req = self._req
        self.send(f"SPEC? {req}")
        end = clock() + timeout_s
        while clock() < end:
            ev = self._next()
            if ev is None:
                continue
            if ev.kind == "SPEC":
                try:
                    return parse_spectral(ev.value, req)
                except ValueError as exc:
                    if "does not answer" in str(exc):          # stale reply to an earlier request: skip it
                        continue
                    raise
            self.pending.append(ev)
            if is_safety(ev):
                raise SafetyInterrupt(f"{ev.kind} {ev.value} during a spectral read")
        raise RuntimeError("no SPEC reply: check the AS7341 wiring (design.md)")


class Hub(HubBase):  # pragma: no cover - needs hardware
    def __init__(self, port: str = "auto", baud: int = 115200):
        super().__init__()
        import serial
        from serial.tools import list_ports
        if port == "auto":
            hubs = [p.device for p in list_ports.comports() if p.vid == 0x303A]   # Espressif USB VID (ESP32-S3 "USB" port)
            if not hubs:
                raise RuntimeError("ESP32-S3 hub not found (use its USB connector, not UART); set hub.port in machine.yaml")
            port = hubs[0]
        self.s = serial.Serial(port, baud, timeout=0.1)

    def send(self, line: str) -> None:
        self.s.write((line + "\n").encode())

    def _readline(self) -> str:
        return self.s.readline(MAX_LINE + 2).decode(errors="replace")


class FakeHub(HubBase):
    """Test double: `queue` holds lines the hub will send; `sent` records lines sent to it."""

    def __init__(self, queue: list[str] | None = None, sent: list[str] | None = None):
        super().__init__()
        self.queue = list(queue or [])
        self.sent = sent if sent is not None else []

    def send(self, line: str) -> None:
        self.sent.append(line)

    def _readline(self) -> str:
        return self.queue.pop(0) if self.queue else ""
