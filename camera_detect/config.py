# Camera
FRAME_WIDTH   = 640
FRAME_HEIGHT  = 480

# Side detection (startup, ~3 sec at 30 fps)
SIDE_DETECTION_FRAMES        = 90
SIDE_DETECTION_YAW_THRESHOLD = 3.0   # degrees; median > threshold → left-mounted

# Focus score weights (must sum to 1.0)
FOCUS_WEIGHT_YAW   = 0.50
FOCUS_WEIGHT_PITCH = 0.45
FOCUS_WEIGHT_ROLL  = 0.05

# Exponential moving average for score smoothing (lower = smoother / slower)
EMA_ALPHA = 0.10

# Focus state thresholds (applied to smoothed score)
SCORE_FOCUSED_THRESHOLD    = 0.55
SCORE_DISTRACTED_THRESHOLD = 0.25

# Consecutive frames before committing a state transition (~30 fps)
FRAMES_TO_FOCUSED    = 20   # ~0.7 sec
FRAMES_TO_DISTRACTED = 90   # ~3.0 sec
FRAMES_TO_BORDERLINE = 15   # ~0.5 sec

# Sustained face absence thresholds
NO_FACE_DISTRACTED_FRAMES = 90    # ~3 sec → force DISTRACTED
NO_FACE_LABEL_FRAMES      = 240   # ~8 sec → show NO FACE IN FRAME label

# Blink / EAR
EAR_BLINK_THRESHOLD          = 0.20
EAR_BLINK_CONSECUTIVE_FRAMES = 2

# Fatigue — baseline calibration
BASELINE_ACTIVE_SECONDS = 120   # 2 min of face-visible time to establish baseline
BASELINE_MIN_BPM        = 2.0   # if baseline comes out below this, extend calibration

# Fatigue — break detection (relative to personal baseline)
FATIGUE_MULTIPLIER     = 1.4    # bpm > baseline * 1.4 → fatigue signal
EYE_STRAIN_MULTIPLIER  = 0.45   # bpm < baseline * 0.45 → eye strain signal
BREAK_SUSTAINED_SECONDS = 180   # 3 min of sustained abnormal rate → BREAK NEEDED
BREAK_RESET_SECONDS     = 60    # 60 sec away from desk resets the break counter
