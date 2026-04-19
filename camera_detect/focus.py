import config

FOCUSED    = "FOCUSED"
BORDERLINE = "BORDERLINE"
DISTRACTED = "DISTRACTED"

_FRAMES_REQUIRED = {
    FOCUSED:    config.FRAMES_TO_FOCUSED,
    DISTRACTED: config.FRAMES_TO_DISTRACTED,
    BORDERLINE: config.FRAMES_TO_BORDERLINE,
}


class FocusScorer:
    """
    Per-frame focus scoring and state machine.

    Call update(yaw, pitch, roll) when a face is detected.
    Call no_face() when no face is in frame.
    Both return (smoothed_score: float 0–1, state: str).
    """

    def __init__(self, profile):
        self._profile        = profile
        self._smoothed       = 0.5
        self._state          = BORDERLINE
        self._candidate      = BORDERLINE
        self._candidate_count = 0
        self._no_face_count  = 0

    # ------------------------------------------------------------------
    # Public
    # ------------------------------------------------------------------

    def update(self, yaw, pitch, roll):
        """Face detected this frame — score and advance state machine."""
        self._no_face_count = 0
        raw = self._raw_score(yaw, pitch, roll)
        self._smoothed = (
            config.EMA_ALPHA * raw + (1.0 - config.EMA_ALPHA) * self._smoothed
        )
        self._tick_state_machine(self._smoothed)
        return self._smoothed, self._state

    def no_face(self):
        """
        No face detected this frame.
        Hold current score; force DISTRACTED after sustained absence.
        """
        self._no_face_count += 1
        if self._no_face_count >= config.NO_FACE_DISTRACTED_FRAMES:
            # Bypass the gradual state machine — absence IS distraction
            self._state           = DISTRACTED
            self._candidate       = DISTRACTED
            self._candidate_count = 0
        return self._smoothed, self._state

    @property
    def score(self):
        return self._smoothed

    @property
    def state(self):
        return self._state

    @property
    def show_no_face_label(self):
        """True only after a long absence — user likely left the frame entirely."""
        return self._no_face_count >= config.NO_FACE_LABEL_FRAMES

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _raw_score(self, yaw, pitch, roll):
        p = self._profile
        yaw_err   = abs(yaw   - p.expected_yaw)   / p.yaw_tolerance
        pitch_err = abs(pitch - p.expected_pitch)  / p.pitch_tolerance
        roll_err  = abs(roll  - p.expected_roll)   / p.roll_tolerance
        weighted_distance = (
            config.FOCUS_WEIGHT_YAW   * yaw_err
            + config.FOCUS_WEIGHT_PITCH * pitch_err
            + config.FOCUS_WEIGHT_ROLL  * roll_err
        )
        return max(0.0, 1.0 - weighted_distance)

    def _tick_state_machine(self, score):
        if score >= config.SCORE_FOCUSED_THRESHOLD:
            target = FOCUSED
        elif score <= config.SCORE_DISTRACTED_THRESHOLD:
            target = DISTRACTED
        else:
            target = BORDERLINE

        # Already in target — stable, reset pending transition
        if target == self._state:
            self._candidate       = target
            self._candidate_count = 0
            return

        # Accumulate consecutive frames pointing at the same new state
        if target == self._candidate:
            self._candidate_count += 1
        else:
            self._candidate       = target
            self._candidate_count = 1

        if self._candidate_count >= _FRAMES_REQUIRED[target]:
            self._state           = target
            self._candidate_count = 0
