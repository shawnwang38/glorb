import cv2
import numpy as np

# Six stable face landmarks used for solvePnP.
# Indices into the MediaPipe 468-landmark set.
_LM_IDX = [1, 152, 263, 33, 287, 57]

# Corresponding 3-D reference positions (mm, origin = nose tip).
_MODEL_PTS = np.array([
    [   0.0,    0.0,    0.0],   # nose tip       (1)
    [   0.0, -330.0,  -65.0],   # chin           (152)
    [-225.0,  170.0, -135.0],   # left eye outer (263)
    [ 225.0,  170.0, -135.0],   # right eye outer(33)
    [-150.0, -150.0, -125.0],   # left mouth     (287)
    [ 150.0, -150.0, -125.0],   # right mouth    (57)
], dtype=np.float64)

_DIST_COEFFS = np.zeros((4, 1))


def _camera_matrix(w, h):
    f = float(w)   # focal length approximation
    return np.array([[f, 0, w / 2.0],
                     [0, f, h / 2.0],
                     [0, 0, 1.0    ]], dtype=np.float64)


def estimate(landmarks, frame_shape):
    """
    Return (yaw, pitch, roll) in degrees, or None if solvePnP fails.

    Sign convention (from RQDecomp3x3 on the solvePnP rotation matrix):
      yaw   > 0  → face turned right in camera frame
      pitch > 0  → face tilted upward
      roll  > 0  → face tilted right (ear toward right shoulder)
    """
    h, w = frame_shape[:2]
    image_pts = np.array(
        [(landmarks[i][0], landmarks[i][1]) for i in _LM_IDX],
        dtype=np.float64,
    )
    ok, rvec, _ = cv2.solvePnP(
        _MODEL_PTS, image_pts, _camera_matrix(w, h), _DIST_COEFFS,
        flags=cv2.SOLVEPNP_ITERATIVE,
    )
    if not ok:
        return None
    rmat, _ = cv2.Rodrigues(rvec)
    angles, *_ = cv2.RQDecomp3x3(rmat)   # returns degrees
    pitch, yaw, roll = angles
    return yaw, pitch, roll
