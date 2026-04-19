import cv2
import config


class Camera:
    def __init__(self, index: int):
        self.cap = cv2.VideoCapture(index)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH,  config.FRAME_WIDTH)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, config.FRAME_HEIGHT)
        if not self.cap.isOpened():
            raise RuntimeError(f"Could not open camera at index {index}.")

    def read(self):
        """Return the next BGR frame, or None on failure."""
        ok, frame = self.cap.read()
        return frame if ok else None

    def release(self):
        self.cap.release()
