import cv2
import numpy as np

import config
import pose
import profiles

# When filtering frames for pitch/roll measurement, only use frames where yaw
# is within this many degrees of the median yaw.  This excludes frames where
# the user was glancing around during the startup window.
_YAW_FILTER_DEGREES  = 8.0
_MIN_FILTER_FRACTION = 0.3
_WARMUP_FRAMES       = 30   # discard ~1 sec of frames while camera exposure stabilizes


def detect_side(camera, detector):
    """
    Collect SIDE_DETECTION_FRAMES frames while the user sits naturally.

    Yaw:        median of all samples — stable enough to use directly.
    Pitch/Roll: median of yaw-filtered samples only (frames where the user
                was already looking at the screen), so outlier head positions
                during startup don't corrupt the expected focused pitch.

    Returns a CameraProfile built from the measured pose.
    Prints all measured values to terminal for verification.
    """
    # Let the camera exposure and white balance stabilize before sampling.
    for _ in range(_WARMUP_FRAMES):
        frame = camera.read()
        if frame is not None:
            _draw_banner(frame, 0, config.SIDE_DETECTION_FRAMES)
            cv2.imshow("Focus Detector", frame)
            cv2.waitKey(1)

    yaw_samples   = []
    pitch_samples = []
    roll_samples  = []

    for frame_idx in range(config.SIDE_DETECTION_FRAMES):
        frame = camera.read()
        if frame is None:
            continue

        _draw_banner(frame, frame_idx, config.SIDE_DETECTION_FRAMES)
        cv2.imshow("Focus Detector", frame)
        cv2.waitKey(1)

        landmarks = detector.detect(frame)
        if landmarks is None:
            continue

        result = pose.estimate(landmarks, frame.shape)
        if result is not None:
            yaw, pitch, roll = result
            yaw_samples.append(yaw)
            pitch_samples.append(pitch)
            roll_samples.append(roll)

    if not yaw_samples:
        print("[startup] No face detected during setup window. Using default profile.")
        return profiles.LEFT_CAMERA

    yaw_arr   = np.array(yaw_samples)
    pitch_arr = np.array(pitch_samples)
    roll_arr  = np.array(roll_samples)

    median_yaw = float(np.median(yaw_arr))

    # Filter pitch/roll to frames where yaw was already near the focused position.
    # These are the frames where the user was genuinely looking at the screen.
    focused_mask = np.abs(yaw_arr - median_yaw) <= _YAW_FILTER_DEGREES
    if focused_mask.sum() >= max(3, len(yaw_arr) * _MIN_FILTER_FRACTION):
        median_pitch = float(np.median(pitch_arr[focused_mask]))
        median_roll  = float(np.median(roll_arr[focused_mask]))
        n_filtered   = focused_mask.sum()
    else:
        # Not enough focused frames — use all samples
        median_pitch = float(np.median(pitch_arr))
        median_roll  = float(np.median(roll_arr))
        n_filtered   = len(yaw_arr)

    side = "left" if median_yaw > 0 else "right"

    print(f"[startup] Camera side : {side.upper()}")
    print(f"[startup] Expected pose (from {n_filtered} focused frames) — "
          f"yaw: {median_yaw:+.1f}°  pitch: {median_pitch:+.1f}°  roll: {median_roll:+.1f}°")

    return profiles.build_profile(side, median_yaw, median_pitch, median_roll)


def _draw_banner(frame, frame_idx, total):
    h, w = frame.shape[:2]
    pct = frame_idx / total

    overlay = frame.copy()
    cv2.rectangle(overlay, (0, 0), (w, h), (0, 0, 0), -1)
    cv2.addWeighted(overlay, 0.45, frame, 0.55, 0, frame)

    cv2.putText(
        frame, "Detecting camera position...",
        (w // 2 - 205, h // 2 - 24),
        cv2.FONT_HERSHEY_SIMPLEX, 0.75, (255, 255, 255), 2, cv2.LINE_AA,
    )
    cv2.putText(
        frame, "Sit naturally and look at your screen.",
        (w // 2 - 185, h // 2 + 4),
        cv2.FONT_HERSHEY_SIMPLEX, 0.55, (200, 200, 200), 1, cv2.LINE_AA,
    )

    bar_x, bar_y, bar_h = 50, h // 2 + 28, 14
    bar_w = w - 100
    cv2.rectangle(frame, (bar_x, bar_y), (bar_x + bar_w, bar_y + bar_h), (60, 60, 60), -1)
    cv2.rectangle(frame, (bar_x, bar_y), (bar_x + int(bar_w * pct), bar_y + bar_h), (0, 210, 100), -1)
