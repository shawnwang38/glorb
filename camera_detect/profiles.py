from dataclasses import dataclass


@dataclass(frozen=True)
class CameraProfile:
    side: str
    expected_yaw: float
    expected_pitch: float
    expected_roll: float
    yaw_tolerance: float
    pitch_tolerance: float
    roll_tolerance: float


def build_profile(side, expected_yaw, expected_pitch, expected_roll):
    """
    Build a profile from the measured startup pose.
    Tolerances are fixed built-in values — only the expected pose is measured.
    """
    return CameraProfile(
        side=side,
        expected_yaw=expected_yaw,
        expected_pitch=expected_pitch,
        expected_roll=expected_roll,
        yaw_tolerance=25.0,   # score → 0 when yaw deviates >25° from expected
        pitch_tolerance=12.0, # tight — 16° shift (looking above screen) → DISTRACTED
        roll_tolerance=30.0,  # loose — roll varies with posture, low weight
    )


# Fallback used only when no face is detected during the startup window.
LEFT_CAMERA = CameraProfile(
    side="left",
    expected_yaw=20.0,
    expected_pitch=-15.0,
    expected_roll=-14.0,
    yaw_tolerance=25.0,
    pitch_tolerance=12.0,
    roll_tolerance=30.0,
)
