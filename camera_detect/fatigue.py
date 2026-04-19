import time
from collections import deque

import numpy as np

import config

_LEFT_EYE  = [362, 385, 387, 263, 373, 380]
_RIGHT_EYE = [33,  160, 158, 133, 153, 144]

CALIBRATING  = "CALIBRATING"
NORMAL       = "NORMAL"
BREAK_NEEDED = "BREAK NEEDED"


def _ear(landmarks, indices):
    pts = [np.array(landmarks[i][:2], dtype=np.float64) for i in indices]
    p1, p2, p3, p4, p5, p6 = pts
    return (np.linalg.norm(p2 - p6) + np.linalg.norm(p3 - p5)) / (
        2.0 * np.linalg.norm(p1 - p4)
    )


class FatigueTracker:
    """
    Two-phase fatigue tracker:

    Phase 1 — CALIBRATING (first BASELINE_ACTIVE_SECONDS of face-visible time):
        Counts blinks and accumulates active face time.
        Computes a personal baseline bpm when enough data is collected.

    Phase 2 — Monitoring:
        Compares rolling bpm against baseline.
        Builds an abnormality accumulator when rate is outside normal range.
        Issues BREAK_NEEDED after BREAK_SUSTAINED_SECONDS of sustained abnormality.
        Resets if user steps away for BREAK_RESET_SECONDS (they took a break).
    """

    def __init__(self):
        self._blink_times   = deque()   # timestamps of completed blinks (rolling 60 s)
        self._below_count   = 0         # consecutive low-EAR frames
        self._last_face_ts  = None
        self._face_lost_at  = None      # when face was last lost (for break reset)

        # Baseline
        self._baseline_bpm      = None
        self._baseline_blinks   = 0
        self._baseline_active_s = 0.0

        # Session total
        self._total_blinks = 0

        # Sustained abnormality accumulator
        self._abnormal_accum = 0.0
        self._last_tick_ts   = None     # last time accumulator was updated

    # ------------------------------------------------------------------
    # Public
    # ------------------------------------------------------------------

    def update(self, landmarks):
        """
        Call once per frame.
        Returns (ear: float|None, blinks_per_min: float, fatigue_state: str).
        """
        now = time.monotonic()

        if landmarks is None:
            self._handle_no_face(now)
            bpm = self._blinks_per_minute(now)
            return None, bpm, self._state()

        self._handle_face_present(landmarks, now)
        bpm = self._blinks_per_minute(now)
        self._tick_accumulator(bpm, now)

        ear = (_ear(landmarks, _LEFT_EYE) + _ear(landmarks, _RIGHT_EYE)) / 2.0
        return ear, bpm, self._state()

    @property
    def total_blinks(self):
        return self._total_blinks

    @property
    def baseline_bpm(self):
        return self._baseline_bpm

    @property
    def calibration_progress(self):
        """0.0 – 1.0 fraction through the baseline window."""
        return min(1.0, self._baseline_active_s / config.BASELINE_ACTIVE_SECONDS)

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _handle_no_face(self, now):
        self._below_count = 0

        if self._last_face_ts is not None:
            self._face_lost_at = now   # mark when face disappeared

        self._last_face_ts = None
        self._last_tick_ts = None      # pause accumulator while face is gone

        # Reset break counter if user has been away long enough
        if (self._face_lost_at is not None
                and now - self._face_lost_at >= config.BREAK_RESET_SECONDS):
            if self._abnormal_accum > 0:
                self._abnormal_accum = 0.0
                print("[fatigue] Break detected — abnormality counter reset.")

    def _handle_face_present(self, landmarks, now):
        self._face_lost_at = None   # face is back

        # Accumulate active face time
        if self._last_face_ts is not None:
            dt = now - self._last_face_ts
            if self._baseline_bpm is None:
                self._baseline_active_s += dt

        self._last_face_ts = now

        # Blink detection
        ear = (_ear(landmarks, _LEFT_EYE) + _ear(landmarks, _RIGHT_EYE)) / 2.0
        if ear < config.EAR_BLINK_THRESHOLD:
            self._below_count += 1
        else:
            if self._below_count >= config.EAR_BLINK_CONSECUTIVE_FRAMES:
                self._blink_times.append(now)
                self._total_blinks += 1
                if self._baseline_bpm is None:
                    self._baseline_blinks += 1
            self._below_count = 0

        # Complete baseline when enough active time collected
        if (self._baseline_bpm is None
                and self._baseline_active_s >= config.BASELINE_ACTIVE_SECONDS):
            candidate = (self._baseline_blinks / self._baseline_active_s) * 60.0
            if candidate >= config.BASELINE_MIN_BPM:
                self._baseline_bpm = candidate
                print(f"[fatigue] Baseline established: {self._baseline_bpm:.1f} bpm  "
                      f"| fatigue >{self._baseline_bpm * config.FATIGUE_MULTIPLIER:.1f}  "
                      f"| eye-strain <{self._baseline_bpm * config.EYE_STRAIN_MULTIPLIER:.1f}")
            else:
                # Too few blinks — extend the window and keep counting
                self._baseline_active_s = 0.0
                self._baseline_blinks   = 0

    def _tick_accumulator(self, bpm, now):
        """Build or decay the abnormality accumulator each frame."""
        if self._baseline_bpm is None or self._last_tick_ts is None:
            self._last_tick_ts = now
            return

        dt = now - self._last_tick_ts
        self._last_tick_ts = now

        high = self._baseline_bpm * config.FATIGUE_MULTIPLIER
        low  = self._baseline_bpm * config.EYE_STRAIN_MULTIPLIER

        is_abnormal = bpm > high or (0 < bpm < low)

        if is_abnormal:
            self._abnormal_accum = min(
                self._abnormal_accum + dt,
                config.BREAK_SUSTAINED_SECONDS * 2,  # cap to avoid runaway buildup
            )
        else:
            self._abnormal_accum = max(0.0, self._abnormal_accum - dt)

    def _state(self):
        if self._baseline_bpm is None:
            return CALIBRATING
        if self._abnormal_accum >= config.BREAK_SUSTAINED_SECONDS:
            return BREAK_NEEDED
        return NORMAL

    def _blinks_per_minute(self, now):
        cutoff = now - 60.0
        while self._blink_times and self._blink_times[0] < cutoff:
            self._blink_times.popleft()
        return float(len(self._blink_times))
