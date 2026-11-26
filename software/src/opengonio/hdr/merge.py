"""HDR from an exposure bracket of 8-bit UVC frames.

UVC cameras give gamma-encoded JPEG/YUYV, not RAW, so the response curve is recovered
first (Debevec & Malik 1997 [R5]) with OpenCV [R49], then frames are merged to linear radiance.
"""
from __future__ import annotations

import numpy as np


def exposure_ladder(base_ms: float, stops: int = 5, step_ev: float = 2.0) -> list[float]:
    return [base_ms * 2 ** (k * step_ev) for k in range(-(stops // 2), stops - stops // 2)]


def recover_response(frames: list[np.ndarray], exposures_ms: list[float]) -> np.ndarray:
    import cv2
    times = np.array(exposures_ms, dtype=np.float32) / 1000.0
    return cv2.createCalibrateDebevec().process(frames, times)


def merge(frames: list[np.ndarray], exposures_ms: list[float], response: np.ndarray) -> np.ndarray:
    import cv2
    times = np.array(exposures_ms, dtype=np.float32) / 1000.0
    return cv2.createMergeDebevec().process(frames, times, response)
