import cv2

import camera as cam_mod
import detector as det_mod
import side_detector
import pose
import focus as focus_mod
import fatigue as fatigue_mod
import display


def main():
    camera   = cam_mod.Camera()
    detector = det_mod.FaceDetector()

    # ── Startup: detect camera side (≈3 seconds, no user input needed) ──
    profile = side_detector.detect_side(camera, detector)
    print(f"[startup] Camera side: {profile.side.upper()}  "
          f"(expected yaw {profile.expected_yaw:+.0f}°)")

    # ── Init pipeline ────────────────────────────────────────────────────
    scorer  = focus_mod.FocusScorer(profile)
    tracker = fatigue_mod.FatigueTracker()

    # ── Main loop ────────────────────────────────────────────────────────
    try:
        print("[main] Running — press Q to quit.")
        while True:
            frame = camera.read()
            if frame is None:
                continue

            landmarks     = detector.detect(frame)
            face_detected = landmarks is not None
            pose_angles   = None  # (yaw, pitch, roll) or None

            if face_detected:
                result = pose.estimate(landmarks, frame.shape)
                if result is not None:
                    yaw, pitch, roll = result
                    pose_angles = (yaw, pitch, roll)
                    scorer.update(yaw, pitch, roll)
                # pose solve failed — hold last state, don't call no_face()
            else:
                scorer.no_face()

            ear, bpm, fatigue_state = tracker.update(landmarks)

            display.render(
                frame,
                focus_state           = scorer.state,
                focus_score           = scorer.score,
                ear                   = ear,
                blinks_per_min        = bpm,
                fatigue_state         = fatigue_state,
                camera_side           = profile.side,
                face_detected         = not scorer.show_no_face_label,
                pose_angles           = pose_angles,
                baseline_bpm          = tracker.baseline_bpm,
                calibration_progress  = tracker.calibration_progress,
                total_blinks          = tracker.total_blinks,
            )

            cv2.imshow("Focus Detector", frame)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    except Exception as e:
        import traceback
        print(f"\n[ERROR] {e}")
        traceback.print_exc()
    finally:
        camera.release()
        detector.close()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
