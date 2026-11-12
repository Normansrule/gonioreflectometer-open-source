"""Stage 17 battery kit: the hub's battery thresholds (firmware/hub/main.py) and the BATT line on the laptop side."""
import ast
from pathlib import Path

import pytest

from opengonio.gantry.hub import parse, parse_battery

ROOT = Path(__file__).resolve().parents[2]


def firmware_fn(name):
    """Run one pure function out of the MicroPython hub firmware (the rest needs the board)."""
    tree = ast.parse((ROOT / "firmware/hub/main.py").read_text(encoding="utf-8"))
    node = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == name)
    ns = {}
    exec(compile(ast.Module([node], []), "main.py", "exec"), ns)
    return ns[name]


def test_battery_thresholds():
    state = firmware_fn("battery_state")
    assert state(25.2, "PACK", 0, 0) == "OK" and state(21.5, "PACK", 0, 0) == "LOW" and state(20.3, "PACK", 0, 0) == "CRIT"
    assert state(20.0, "USBC", 10, 74) == "OK" and state(20.0, "USBC", 66, 74) == "LOW" and state(20.0, "USBC", 71, 74) == "CRIT"
    assert state(17.9, "USBC", 0, 74) == "CRIT"                   # the bank gave up holding 20 V
    assert state(20.0, "USBC", 500, 0) == "OK"                    # capacity never set: no guess
    assert state(24.0, "WALL", 999, 0) == "OK" and state(21.0, "WALL", 0, 0) == "LOW"


def test_batt_line_parsed_and_checked():
    ev = parse("BATT PACK 23.10 0.412 9.5 1.20 OK")
    assert ev.kind == "BATT"
    b = parse_battery(ev.value)
    assert b["source"] == "PACK" and b["volts"] == pytest.approx(23.1) and b["state"] == "OK"
    for bad in ("PACK 23.1 0.4 9.5 OK", "MAINS 24 0 0 0 OK", "PACK 23 0 0 0 FINE"):
        with pytest.raises(ValueError):
            parse_battery(bad)
