"""
Utility Functions
Helper functions for common operations
"""

import cv2
import numpy as np


def format_time(seconds):
    """
    Format seconds as HH:MM:SS.ms

    Args:
        seconds: Time in seconds

    Returns:
        Formatted string
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = seconds % 60

    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{secs:06.3f}"
    else:
        return f"{minutes:02d}:{secs:06.3f}"


def calculate_iou(box1, box2):
    """
    Calculate Intersection over Union for two bounding boxes

    Args:
        box1: [x1, y1, x2, y2]
        box2: [x1, y1, x2, y2]

    Returns:
        IoU value (0-1)
    """
    # Intersection area
    x1 = max(box1[0], box2[0])
    y1 = max(box1[1], box2[1])
    x2 = min(box1[2], box2[2])
    y2 = min(box1[3], box2[3])

    intersection = max(0, x2 - x1) * max(0, y2 - y1)

    # Union area
    area1 = (box1[2] - box1[0]) * (box1[3] - box1[1])
    area2 = (box2[2] - box2[0]) * (box2[3] - box2[1])
    union = area1 + area2 - intersection

    if union == 0:
        return 0.0

    return intersection / union


def resize_frame(frame, target_width=None, target_height=None):
    """
    Resize frame while maintaining aspect ratio

    Args:
        frame: OpenCV image
        target_width: Desired width (optional)
        target_height: Desired height (optional)

    Returns:
        Resized frame
    """
    height, width = frame.shape[:2]

    if target_width and not target_height:
        ratio = target_width / width
        target_height = int(height * ratio)
    elif target_height and not target_width:
        ratio = target_height / height
        target_width = int(width * ratio)

    return cv2.resize(frame, (target_width, target_height))


def draw_text_with_background(frame, text, position, font_scale=0.7, thickness=2,
                               text_color=(255, 255, 255), bg_color=(0, 0, 0)):
    """
    Draw text with background rectangle for better visibility

    Args:
        frame: OpenCV image
        text: Text to draw
        position: (x, y) tuple
        font_scale: Font size
        thickness: Text thickness
        text_color: RGB tuple
        bg_color: RGB tuple

    Returns:
        Frame with text
    """
    font = cv2.FONT_HERSHEY_SIMPLEX

    # Get text size
    (text_width, text_height), baseline = cv2.getTextSize(
        text, font, font_scale, thickness
    )

    x, y = position
    padding = 5

    # Draw background rectangle
    cv2.rectangle(
        frame,
        (x - padding, y - text_height - padding),
        (x + text_width + padding, y + baseline + padding),
        bg_color,
        -1
    )

    # Draw text
    cv2.putText(
        frame,
        text,
        (x, y),
        font,
        font_scale,
        text_color,
        thickness
    )

    return frame


def create_side_by_side(frame1, frame2, labels=None):
    """
    Create side-by-side comparison of two frames

    Args:
        frame1: First frame
        frame2: Second frame
        labels: Optional tuple of (label1, label2)

    Returns:
        Combined frame
    """
    # Ensure same height
    h1, w1 = frame1.shape[:2]
    h2, w2 = frame2.shape[:2]

    if h1 != h2:
        # Resize to match heights
        if h1 > h2:
            frame2 = cv2.resize(frame2, (int(w2 * h1 / h2), h1))
        else:
            frame1 = cv2.resize(frame1, (int(w1 * h2 / h1), h2))

    # Concatenate horizontally
    combined = np.hstack([frame1, frame2])

    # Add labels if provided
    if labels:
        combined = draw_text_with_background(combined, labels[0], (10, 30))
        combined = draw_text_with_background(
            combined,
            labels[1],
            (frame1.shape[1] + 10, 30)
        )

    return combined


def validate_video_file(video_path):
    """
    Validate video file can be opened and has required properties

    Args:
        video_path: Path to video file

    Returns:
        dict with video info or None if invalid
    """
    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        return None

    info = {
        'width': int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
        'height': int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
        'fps': cap.get(cv2.CAP_PROP_FPS),
        'total_frames': int(cap.get(cv2.CAP_PROP_FRAME_COUNT)),
        'duration': int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) / cap.get(cv2.CAP_PROP_FPS)
    }

    cap.release()

    # Basic validation
    if info['width'] < 640 or info['height'] < 480:
        print(f"⚠️  Warning: Low resolution {info['width']}x{info['height']}")

    if info['fps'] < 20:
        print(f"⚠️  Warning: Low FPS {info['fps']}")

    return info


def calculate_distance(point1, point2):
    """
    Calculate Euclidean distance between two points

    Args:
        point1: (x, y) tuple
        point2: (x, y) tuple

    Returns:
        Distance in pixels
    """
    return np.sqrt((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)
