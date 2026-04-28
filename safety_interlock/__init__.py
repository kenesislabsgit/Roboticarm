"""
Safety Interlock System
AI-based human detection for robotic cell safety
"""

__version__ = "1.0.0"
__author__ = "WEG Safety Team"

from .detector import PersonDetector
from .zone_manager import ZoneManager
from .state_machine import SafetyStateMachine
from .video_processor import VideoProcessor
from .logger import SafetyLogger

__all__ = [
    'PersonDetector',
    'ZoneManager',
    'SafetyStateMachine',
    'VideoProcessor',
    'SafetyLogger'
]
