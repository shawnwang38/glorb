import cv2

from focus import FOCUSED, BORDERLINE, DISTRACTED
from fatigue import CALIBRATING, NORMAL, BREAK_NEEDED

NO_FACE_LABEL = "NO FACE IN FRAME"

_FOCUS_COLOR = {
    FOCUSED:       (80,  200,  80),   # green
    BORDERLINE:    (0,   165, 255),   # orange
    DISTRACTED:    (60,   60, 220),   # red
    NO_FACE_LABEL: (180, 180,   0),   # yellow
}

_FATIGUE_COLOR = {
    CALIBRATING:  (120, 120, 120),   # grey — still measuring
    NORMAL:       (150, 150, 150),   # grey
    BREAK_NEEDED: (60,   60, 220),   # red
}


def render(frame, focus_state, focus_score, ear, blinks_per_min,
           fatigue_state, camera_side, face_detected, pose_angles=None,
           baseline_bpm=None, calibration_progress=0.0, total_blinks=0):
    h, w = frame.shape[:2]

    display_label = focus_state if face_detected else NO_FACE_LABEL
    f_color = _FOCUS_COLOR.get(display_label, (200, 200, 200))
    t_color = _FATIGUE_COLOR.get(fatigue_state, (150, 150, 150))

    # ── Top bar ──────────────────────────────────────────────────────────
    _fill_rect(frame, 0, 0, w, 52, alpha=0.55)

    # Camera side (top-left)
    cv2.putText(
        frame, f"cam: {camera_side}",
        (10, 34), cv2.FONT_HERSHEY_SIMPLEX, 0.50,
        (160, 160, 160), 1, cv2.LINE_AA,
    )

    # Focus / no-face label (centered)
    label_x = w // 2 - _text_width(display_label, 0.80) // 2
    cv2.putText(
        frame, display_label,
        (label_x, 34), cv2.FONT_HERSHEY_SIMPLEX, 0.80,
        f_color, 2, cv2.LINE_AA,
    )

    # Score bar (top-right) — only shown when face is present
    if face_detected:
        _score_bar(frame, w - 165, 14, 140, 22, focus_score, f_color)

    # ── Debug row (pose angles + score) ──────────────────────────────────
    _fill_rect(frame, 0, 52, w, 22, alpha=0.40)
    if pose_angles is not None:
        yaw, pitch, roll = pose_angles
        cv2.putText(
            frame,
            f"yaw:{yaw:+.1f}°  pitch:{pitch:+.1f}°  roll:{roll:+.1f}°  score:{focus_score:.2f}  blinks:{total_blinks}",
            (10, 68), cv2.FONT_HERSHEY_SIMPLEX, 0.42,
            (140, 220, 255), 1, cv2.LINE_AA,
        )

    # ── Bottom bar ───────────────────────────────────────────────────────
    _fill_rect(frame, 0, h - 42, w, 42, alpha=0.55)

    # Fatigue state (bottom-left)
    if fatigue_state == CALIBRATING:
        cal_pct = int(calibration_progress * 100)
        label = f"CALIBRATING {cal_pct}%"
    else:
        label = fatigue_state
    cv2.putText(
        frame, label,
        (10, h - 14), cv2.FONT_HERSHEY_SIMPLEX, 0.52,
        t_color, 1, cv2.LINE_AA,
    )

    # EAR value (bottom-center)
    if ear is not None:
        cv2.putText(
            frame, f"EAR {ear:.2f}",
            (w // 2 - 30, h - 14), cv2.FONT_HERSHEY_SIMPLEX, 0.45,
            (120, 120, 120), 1, cv2.LINE_AA,
        )

    # Blink rate + baseline (bottom-right)
    if baseline_bpm is not None:
        bpm_str = f"{blinks_per_min:.0f} bl/min  base:{baseline_bpm:.0f}"
    else:
        bpm_str = f"{blinks_per_min:.0f} bl/min"
    cv2.putText(
        frame, bpm_str,
        (w - _text_width(bpm_str, 0.45) - 10, h - 14),
        cv2.FONT_HERSHEY_SIMPLEX, 0.45,
        (160, 160, 160), 1, cv2.LINE_AA,
    )


# ── Helpers ──────────────────────────────────────────────────────────────

def _fill_rect(frame, x, y, w, h, alpha):
    roi = frame[y:y + h, x:x + w]
    black = roi.copy()
    black[:] = (20, 20, 20)
    cv2.addWeighted(black, alpha, roi, 1.0 - alpha, 0, roi)


def _score_bar(frame, x, y, w, h, score, color):
    cv2.rectangle(frame, (x, y), (x + w, y + h), (55, 55, 55), -1)
    fill = int(w * max(0.0, min(1.0, score)))
    if fill > 0:
        cv2.rectangle(frame, (x, y), (x + fill, y + h), color, -1)
    cv2.putText(
        frame, f"{score:.2f}",
        (x + w + 5, y + h - 2), cv2.FONT_HERSHEY_SIMPLEX, 0.40,
        (160, 160, 160), 1, cv2.LINE_AA,
    )


def _text_width(text, scale):
    (tw, _), _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, scale, 1)
    return tw
