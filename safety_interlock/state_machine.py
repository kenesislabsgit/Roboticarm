"""
State Machine Module
Manages system states (CLEAR, WARNING, DANGER) and trigger logic
"""

from collections import deque
from enum import Enum
from . import config
import pygame
import os


class State(Enum):
    """System states"""
    CLEAR = "CLEAR"       # No person detected or outside zone
    WARNING = "WARNING"   # Person detected, approaching zone
    DANGER = "DANGER"     # Person inside danger zone


class SafetyStateMachine:
    """
    State machine for safety interlock system
    Handles state transitions and trigger events
    """

    def __init__(self):
        """Initialize state machine"""
        self.current_state = State.CLEAR
        self.previous_state = State.CLEAR

        # Temporal smoothing buffer
        self.state_history = deque(maxlen=config.TEMPORAL_SMOOTHING_FRAMES)

        # Event tracking
        self.events = []
        self.trigger_count = 0

        # Initialize alarm sound
        pygame.mixer.init()
        alarm_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'alarm.wav')
        if os.path.exists(alarm_path):
            self.alarm_sound = pygame.mixer.Sound(alarm_path)
        else:
            print(f"⚠️  Alarm file not found: {alarm_path}")
            self.alarm_sound = None

    def update(self, detections, zone_manager, frame_number, timestamp):
        """
        Update state based on current detections

        Args:
            detections: List of person detections with overlap info
            zone_manager: ZoneManager instance
            frame_number: Current frame number
            timestamp: Current timestamp in seconds

        Returns:
            dict: {
                'state': current State,
                'changed': bool (state transition occurred),
                'triggered': bool (stop trigger fired),
                'event': dict or None
            }
        """
        # Determine new state based on detections
        new_state = self._classify_state(detections, zone_manager)

        # Apply temporal smoothing
        self.state_history.append(new_state)
        smoothed_state = self._get_smoothed_state()

        # Check for state transition
        self.previous_state = self.current_state
        state_changed = self.current_state != smoothed_state

        # Handle transition
        event = None
        triggered = False

        if state_changed:
            event = self._on_state_transition(
                self.previous_state,
                smoothed_state,
                frame_number,
                timestamp,
                detections
            )

            if event and event['type'] == 'STOP':
                triggered = True
                self.trigger_count += 1
                if self.alarm_sound:
                    self.alarm_sound.play()

            self.events.append(event)

        self.current_state = smoothed_state

        return {
            'state': self.current_state,
            'changed': state_changed,
            'triggered': triggered,
            'event': event
        }

    def _classify_state(self, detections, zone_manager):
        """
        Classify system state based on detections

        Args:
            detections: List of detections with overlap calculated
            zone_manager: ZoneManager instance

        Returns:
            State enum
        """
        if not detections:
            return State.CLEAR

        # Check each person's overlap
        max_overlap = 0
        for detection in detections:
            bbox = detection['bbox']
            overlap = zone_manager.calculate_overlap(bbox)
            detection['overlap'] = overlap
            max_overlap = max(max_overlap, overlap)

        # Apply thresholds with hysteresis if enabled
        if config.ENABLE_HYSTERESIS and self.current_state == State.DANGER:
            # Already in DANGER, need to drop below exit threshold
            if max_overlap >= config.HYSTERESIS_EXIT:
                return State.DANGER
            elif max_overlap > config.WARNING_THRESHOLD:
                return State.WARNING
            else:
                return State.CLEAR
        else:
            # Not in DANGER or hysteresis disabled
            if max_overlap >= config.DANGER_THRESHOLD:
                return State.DANGER
            elif max_overlap > config.WARNING_THRESHOLD:
                return State.WARNING
            else:
                return State.CLEAR

    def _get_smoothed_state(self):
        """
        Apply temporal smoothing to prevent flickering

        Returns:
            Most common state in recent history
        """
        if not self.state_history:
            return self.current_state

        # Count occurrences
        state_counts = {}
        for state in self.state_history:
            state_counts[state] = state_counts.get(state, 0) + 1

        # Return most common, prioritizing DANGER in ties
        max_count = max(state_counts.values())
        candidates = [s for s, c in state_counts.items() if c == max_count]

        if State.DANGER in candidates:
            return State.DANGER
        elif State.WARNING in candidates:
            return State.WARNING
        else:
            return State.CLEAR

    def _on_state_transition(self, old_state, new_state, frame_number, timestamp, detections):
        """
        Handle state transition and generate event

        Args:
            old_state: Previous State
            new_state: New State
            frame_number: Frame number
            timestamp: Timestamp in seconds
            detections: Current detections

        Returns:
            dict: Event information
        """
        # Determine event type
        event_type = None
        description = None

        if old_state != State.DANGER and new_state == State.DANGER:
            event_type = "STOP"
            description = "Person entered danger zone"
        elif old_state == State.DANGER and new_state != State.DANGER:
            event_type = "RESUME"
            description = "Person left danger zone"
        elif old_state == State.CLEAR and new_state == State.WARNING:
            event_type = "WARNING"
            description = "Person approaching zone"
        elif old_state == State.WARNING and new_state == State.CLEAR:
            event_type = "CLEAR"
            description = "Person moved away"

        # Get max confidence and overlap
        max_confidence = max([d['confidence'] for d in detections]) if detections else 0
        max_overlap = max([d.get('overlap', 0) for d in detections]) if detections else 0

        event = {
            'type': event_type,
            'description': description,
            'frame': frame_number,
            'timestamp': timestamp,
            'old_state': old_state.value,
            'new_state': new_state.value,
            'num_persons': len(detections),
            'max_confidence': max_confidence,
            'max_overlap': max_overlap
        }

        return event

    def get_state_name(self):
        """Get current state as string"""
        return self.current_state.value

    def is_danger(self):
        """Check if in DANGER state"""
        return self.current_state == State.DANGER

    def get_statistics(self):
        """Get statistics about events"""
        stop_events = [e for e in self.events if e and e['type'] == 'STOP']
        resume_events = [e for e in self.events if e and e['type'] == 'RESUME']
        warning_events = [e for e in self.events if e and e['type'] == 'WARNING']

        # Calculate total danger time
        total_danger_time = 0
        if stop_events and resume_events:
            for stop_event in stop_events:
                # Find corresponding resume
                resume = next((r for r in resume_events if r['timestamp'] > stop_event['timestamp']), None)
                if resume:
                    total_danger_time += resume['timestamp'] - stop_event['timestamp']

        return {
            'trigger_count': self.trigger_count,
            'stop_events': len(stop_events),
            'resume_events': len(resume_events),
            'warning_events': len(warning_events),
            'total_danger_time': total_danger_time,
            'events': self.events
        }

    def reset(self):
        """Reset state machine"""
        self.current_state = State.CLEAR
        self.previous_state = State.CLEAR
        self.state_history.clear()
        self.events = []
        self.trigger_count = 0
