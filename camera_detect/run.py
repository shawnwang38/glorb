"""
Headless entrypoint for the glorb-detect detection pipeline.

Spawned by Electron (main.js) as a child_process. Responsibilities:
  - Enumerate cameras via `system_profiler SPCameraDataType -json` (macOS).
  - Reject built-in / FaceTime cameras; pick the first USB camera we can open.
  - If no USB camera is present, exit cleanly with code 0.
  - Run the focus + fatigue pipeline headlessly (no cv2.imshow / waitKey).
  - Emit edge-triggered line-delimited commands over /tmp/glorb-ipc.sock:
      drift\n     -> FOCUSED|BORDERLINE -> DISTRACTED
      refocus\n   -> DISTRACTED -> FOCUSED
      fatigue\n   -> NORMAL -> BREAK_NEEDED
  - Writes happen on state transitions only, never per-frame.
"""

import json
import os
import re
import socket
import subprocess
import sys
import time

import cv2

import camera as cam_mod
import detector as det_mod
import side_detector
import pose
import focus as focus_mod
import fatigue as fatigue_mod

SOCK_PATH = "/tmp/glorb-ipc.sock"


def find_usb_camera_index():
    """Return the first openable cv2 index that does NOT correspond to a
    built-in / FaceTime camera, or None if no USB camera is available."""
    try:
        result = subprocess.run(
            ["system_profiler", "SPCameraDataType", "-json"],
            capture_output=True,
            text=True,
            timeout=5,
        )
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired,
            FileNotFoundError) as e:
        sys.stderr.write(f"[glorb-detect] system_profiler failed: {e}\n")
        sys.stderr.flush()
        return None

    try:
        data = json.loads(result.stdout or "{}")
    except json.JSONDecodeError as e:
        sys.stderr.write(f"[glorb-detect] system_profiler JSON parse failed: {e}\n")
        sys.stderr.flush()
        return None

    cameras = data.get("SPCameraDataType", []) or []
    external = []
    for entry in cameras:
        name = entry.get("_name", "") if isinstance(entry, dict) else ""
        if not name:
            continue
        if re.search(r"facetime|built.?in", name, re.IGNORECASE):
            continue
        external.append(name)

    if not external:
        return None

    # Probe cv2 indices 1..4 (skip 0 — always built-in on macOS).
    for i in range(1, 5):
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            cap.release()
            return i
        cap.release()

    return None


def connect_socket(retries=10, delay=0.5):
    """Best-effort startup probe: try to connect to SOCK_PATH a few times so
    we log whether Electron's listener is up. Returns the socket on success
    (caller should close it) or None after exhausting retries."""
    for _ in range(retries):
        s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        try:
            s.connect(SOCK_PATH)
            s.setblocking(True)
            return s
        except (FileNotFoundError, ConnectionRefusedError):
            try:
                s.close()
            except OSError:
                pass
            time.sleep(delay)
            continue
        except OSError:
            try:
                s.close()
            except OSError:
                pass
            time.sleep(delay)
            continue

    sys.stderr.write(
        "[glorb-detect] could not connect to Electron socket; "
        "running detection without intervention\n"
    )
    sys.stderr.flush()
    return None


def emit(verb):
    """Open a fresh AF_UNIX connection and send `{verb}\n`. Electron closes
    after one line, so every emit opens a new socket. Failures are logged
    and swallowed — detection must keep running regardless."""
    s = None
    try:
        s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        s.settimeout(0.5)
        s.connect(SOCK_PATH)
        s.sendall((verb + "\n").encode())
        try:
            s.recv(64)  # best-effort: drain the ok\n reply
        except (socket.timeout, OSError):
            pass
    except (ConnectionError, FileNotFoundError, OSError) as e:
        sys.stderr.write(f"[glorb-detect] emit({verb}) failed: {e}\n")
        sys.stderr.flush()
    finally:
        if s is not None:
            try:
                s.close()
            except OSError:
                pass


def main():
    idx = find_usb_camera_index()
    if idx is None:
        sys.stderr.write("[glorb-detect] no USB camera, exiting\n")
        sys.stderr.flush()
        sys.exit(0)

    print(f"[glorb-detect] using camera index {idx}", flush=True)

    # Startup probe — result is only used for log visibility.
    probe = connect_socket()
    if probe is not None:
        try:
            probe.close()
        except OSError:
            pass
        print("[glorb-detect] connected to Electron socket", flush=True)

    camera = cam_mod.Camera(idx)
    detector = det_mod.FaceDetector()

    # side_detector.detect_side() internally uses cv2.imshow/waitKey/_draw_banner.
    # Monkey-patch cv2 so no window flashes during the ~3s calibration.
    # Save refs and restore after detect_side returns for hygiene; the main
    # loop itself does not use imshow/waitKey.
    _orig_imshow = cv2.imshow
    _orig_waitKey = cv2.waitKey
    try:
        cv2.imshow = lambda *a, **k: None
        cv2.waitKey = lambda *a, **k: 0
        profile = side_detector.detect_side(camera, detector)
    finally:
        cv2.imshow = _orig_imshow
        cv2.waitKey = _orig_waitKey

    scorer = focus_mod.FocusScorer(profile)
    tracker = fatigue_mod.FatigueTracker()

    prev_focus_state = scorer.state                # initial: BORDERLINE
    prev_fatigue_state = fatigue_mod.CALIBRATING   # initial: CALIBRATING

    try:
        while True:
            try:
                frame = camera.read()
                if frame is None:
                    continue

                landmarks = detector.detect(frame)
                if landmarks is not None:
                    result = pose.estimate(landmarks, frame.shape)
                    if result is not None:
                        yaw, pitch, roll = result
                        scorer.update(yaw, pitch, roll)
                    # pose solve failed -> hold last state, do NOT call no_face
                else:
                    scorer.no_face()

                _ear, _bpm, fatigue_state = tracker.update(landmarks)

                # Focus edge detection
                new_focus_state = scorer.state
                if (prev_focus_state in (focus_mod.FOCUSED, focus_mod.BORDERLINE)
                        and new_focus_state == focus_mod.DISTRACTED):
                    emit("drift")
                    print("[glorb-detect] drift", flush=True)
                elif (prev_focus_state == focus_mod.DISTRACTED
                        and new_focus_state == focus_mod.FOCUSED):
                    emit("refocus")
                    print("[glorb-detect] refocus", flush=True)
                prev_focus_state = new_focus_state

                # Fatigue edge detection
                if (prev_fatigue_state != fatigue_mod.BREAK_NEEDED
                        and fatigue_state == fatigue_mod.BREAK_NEEDED):
                    emit("fatigue")
                    print("[glorb-detect] fatigue", flush=True)
                prev_fatigue_state = fatigue_state

            except KeyboardInterrupt:
                break
            except Exception as e:
                sys.stderr.write(f"[glorb-detect] frame error: {e}\n")
                sys.stderr.flush()
                continue
    finally:
        try:
            camera.release()
        except Exception:
            pass
        try:
            detector.close()
        except Exception:
            pass


if __name__ == "__main__":
    main()
