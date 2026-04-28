"""
Configuration settings for Safety Interlock System
All thresholds, paths, and parameters in one place for easy modification
"""

# ===== DETECTION SETTINGS =====
YOLO_MODEL = "yolov8n.pt"  # n=nano (fast), s=small, m=medium, l=large
CONFIDENCE_THRESHOLD = 0.7  # Minimum confidence to consider detection valid (0-1)
CONFIDENCE_THRESHOLD_BOUNDARY = 0.6  # Lower threshold near zone boundary

# ===== ZONE OVERLAP SETTINGS =====
DANGER_THRESHOLD = 0.50  # Person overlap % to trigger DANGER state
WARNING_THRESHOLD = 0.0   # Any overlap triggers WARNING
HYSTERESIS_EXIT = 0.40    # Must drop below this to exit DANGER (prevents jitter)

# ===== STATE MACHINE SETTINGS =====
TEMPORAL_SMOOTHING_FRAMES = 3  # Number of frames for smoothing (anti-flicker)
ENABLE_HYSTERESIS = True       # Use different enter/exit thresholds

# ===== VIDEO PROCESSING =====
SKIP_FRAMES = 0  # Process every Nth frame (0=all frames, 1=every other, etc)
DISPLAY_PREVIEW = True  # Show annotated video during processing
SAVE_ANNOTATED_VIDEO = True  # Save video with bounding boxes/zones

# ===== OUTPUT SETTINGS =====
OUTPUT_DIR = "output"
LOGS_DIR = "output/logs"
FRAMES_DIR = "output/frames"
SAVE_TRIGGER_FRAMES = True  # Save screenshot at each trigger event
SAVE_ALL_DETECTIONS = False  # Save every frame with person detected (lots of images!)

# ===== LOGGING =====
LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR
CONSOLE_OUTPUT = True  # Print to console during processing
DETAILED_LOG = True  # Include per-frame detection details in log

# ===== ZONE DEFINITION =====
# Zone can be defined interactively (user clicks) or hardcoded here
# Format: [(x1, y1), (x2, y2), (x3, y3), (x4, y4)]
# Leave None for interactive mode
PREDEFINED_ZONE = None

# Example hardcoded zone (uncomment to use):
# PREDEFINED_ZONE = [
#     (100, 200),   # top-left
#     (1800, 200),  # top-right
#     (1800, 900),  # bottom-right
#     (100, 900)    # bottom-left
# ]

# ===== PERFORMANCE =====
USE_GPU = True  # Use CUDA if available
BATCH_SIZE = 1  # Frames to process at once (higher=faster but more memory)

# ===== VISUALIZATION =====
BBOX_COLOR_CLEAR = (0, 255, 0)      # Green - person outside zone
BBOX_COLOR_WARNING = (0, 255, 255)  # Yellow - person approaching
BBOX_COLOR_DANGER = (0, 0, 255)     # Red - person in danger zone
ZONE_COLOR = (255, 255, 0)          # Cyan - zone boundary
ZONE_THICKNESS = 3
BBOX_THICKNESS = 2
TEXT_COLOR = (255, 255, 255)
TEXT_SCALE = 1.0
TEXT_THICKNESS = 2

# ===== ALERT SETTINGS (for future hardware integration) =====
ENABLE_ALERTS = False  # Enable external alert system
ALERT_METHOD = "serial"  # serial, tcp, http, gpio
ALERT_PORT = "COM3"  # For serial communication
ALERT_COMMAND_STOP = "STOP\n"
ALERT_COMMAND_RESUME = "RESUME\n"
