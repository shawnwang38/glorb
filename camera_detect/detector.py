import cv2
import mediapipe as mp


class FaceDetector:
    def __init__(self):
        self._mesh = mp.solutions.face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=False,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5,
        )

    def detect(self, frame):
        """
        Return a list of 468 landmarks as (x_px, y_px, z_norm) tuples,
        or None when no face is detected.
        z_norm is MediaPipe's relative depth and is used only for EAR.
        """
        h, w = frame.shape[:2]
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = self._mesh.process(rgb)
        if not result.multi_face_landmarks:
            return None
        raw = result.multi_face_landmarks[0].landmark
        return [(int(p.x * w), int(p.y * h), p.z) for p in raw]

    def close(self):
        self._mesh.close()
