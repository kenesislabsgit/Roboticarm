"""
Logger Module
Handles logging, event recording, and report generation
"""

import os
import cv2
import json
from datetime import datetime
from . import config


class SafetyLogger:
    """Logs events and generates reports"""

    def __init__(self, video_name):
        """
        Initialize logger

        Args:
            video_name: Name of video being processed
        """
        self.video_name = video_name
        self.log_entries = []

        # Create timestamp for this run
        self.run_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Setup log file paths
        self.log_file = os.path.join(
            config.LOGS_DIR,
            f"log_{self.run_timestamp}.txt"
        )

        self.json_file = os.path.join(
            config.LOGS_DIR,
            f"log_{self.run_timestamp}.json"
        )

        # Ensure output directories exist
        os.makedirs(config.LOGS_DIR, exist_ok=True)
        os.makedirs(config.FRAMES_DIR, exist_ok=True)

        # Write header
        self._write_header()

    def _write_header(self):
        """Write log file header"""
        with open(self.log_file, 'w', encoding='utf-8') as f:
            f.write("=" * 70 + "\n")
            f.write("SAFETY INTERLOCK SYSTEM - PROCESSING LOG\n")
            f.write("=" * 70 + "\n")
            f.write(f"Video: {self.video_name}\n")
            f.write(f"Run timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 70 + "\n\n")

        if config.CONSOLE_OUTPUT:
            print("\n" + "=" * 70)
            print("SAFETY INTERLOCK SYSTEM - PROCESSING LOG")
            print("=" * 70)
            print(f"Video: {self.video_name}")
            print(f"Run timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print("=" * 70 + "\n")

    def log_event(self, event, frame=None):
        """
        Log an event

        Args:
            event: Event dictionary from state machine
            frame: OpenCV frame to save (optional)
        """
        if not event:
            return

        self.log_entries.append(event)

        # Format message
        msg = self._format_event(event)

        # Write to file
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(msg + "\n")

        # Console output
        if config.CONSOLE_OUTPUT:
            print(msg)

        # Save frame if it's a trigger event
        if config.SAVE_TRIGGER_FRAMES and frame is not None:
            if event['type'] in ['STOP', 'RESUME']:
                self.save_frame(frame, event['frame'], event['type'])

    def _format_event(self, event):
        """Format event as readable string"""
        event_type = event['type']
        frame = event['frame']
        timestamp = event['timestamp']
        desc = event['description']

        # Add emoji based on type
        emoji = {
            'STOP': '🚨',
            'RESUME': '✅',
            'WARNING': '⚠️',
            'CLEAR': '🟢'
        }.get(event_type, '📍')

        msg = f"[Frame {frame:05d} | {timestamp:7.2f}s] {emoji} {event_type}: {desc}"

        # Add details if available
        if event.get('num_persons', 0) > 0:
            msg += f" | Persons: {event['num_persons']}"
            msg += f" | Confidence: {event['max_confidence']:.2f}"
            msg += f" | Overlap: {event['max_overlap']*100:.1f}%"

        return msg

    def log_frame_detection(self, frame_number, timestamp, detections, state):
        """
        Log per-frame detection details (if detailed logging enabled)

        Args:
            frame_number: Frame number
            timestamp: Timestamp in seconds
            detections: List of detections
            state: Current state
        """
        if not config.DETAILED_LOG:
            return

        if detections:
            msg = f"[Frame {frame_number:05d} | {timestamp:7.2f}s] State: {state} | Detected: {len(detections)} person(s)"
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(msg + "\n")

    def save_frame(self, frame, frame_number, label=""):
        """
        Save frame to disk

        Args:
            frame: OpenCV image
            frame_number: Frame number
            label: Optional label for filename
        """
        filename = f"frame_{frame_number:05d}"
        if label:
            filename += f"_{label}"
        filename += ".jpg"

        filepath = os.path.join(config.FRAMES_DIR, filename)
        cv2.imwrite(filepath, frame)

        if config.CONSOLE_OUTPUT:
            print(f"  💾 Saved: {filepath}")

    def generate_report(self, stats, video_info, zone_info, detector_info):
        """
        Generate final report

        Args:
            stats: Statistics from state machine
            video_info: Video metadata
            zone_info: Zone information
            detector_info: Detector information
        """
        report_lines = [
            "\n" + "=" * 70,
            "PROCESSING COMPLETE - FINAL REPORT",
            "=" * 70,
            "",
            "=== VIDEO INFORMATION ===",
            f"File: {video_info['filename']}",
            f"Resolution: {video_info['width']}x{video_info['height']}",
            f"FPS: {video_info['fps']}",
            f"Total Frames: {video_info['total_frames']}",
            f"Duration: {video_info['duration']:.2f} seconds",
            "",
            "=== DETECTION CONFIGURATION ===",
            f"Model: {detector_info['model']}",
            f"Device: {detector_info['device']}",
            f"Confidence Threshold: {detector_info['confidence_threshold']}",
            "",
            "=== DANGER ZONE ===",
            f"Points: {zone_info['num_points']}",
            f"Area: {zone_info['area']:.0f} pixels²",
            "",
            "=== DETECTION SUMMARY ===",
            f"Total Events: {len(stats['events'])}",
            f"STOP Triggers: {stats['stop_events']}",
            f"RESUME Events: {stats['resume_events']}",
            f"WARNING Events: {stats['warning_events']}",
            f"Total Danger Time: {stats['total_danger_time']:.2f} seconds",
            "",
            "=== EVENT LOG ===",
        ]

        # Add all events
        for event in stats['events']:
            if event:
                report_lines.append(self._format_event(event))

        report_lines.extend([
            "",
            "=== OUTPUT FILES ===",
            f"Log file: {self.log_file}",
            f"JSON data: {self.json_file}",
            f"Frames saved: {config.FRAMES_DIR}",
            "",
            "=" * 70,
        ])

        # Write to log file
        report = "\n".join(report_lines)
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(report + "\n")

        # Console output
        if config.CONSOLE_OUTPUT:
            print(report)

        # Save JSON report
        self._save_json_report(stats, video_info, zone_info, detector_info)

    def _save_json_report(self, stats, video_info, zone_info, detector_info):
        """Save structured JSON report"""
        data = {
            'run_info': {
                'timestamp': self.run_timestamp,
                'video': self.video_name,
            },
            'video_info': video_info,
            'detector_info': detector_info,
            'zone_info': zone_info,
            'statistics': {
                'trigger_count': stats['trigger_count'],
                'stop_events': stats['stop_events'],
                'resume_events': stats['resume_events'],
                'warning_events': stats['warning_events'],
                'total_danger_time': stats['total_danger_time'],
            },
            'events': stats['events']
        }

        with open(self.json_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        if config.CONSOLE_OUTPUT:
            print(f"\n📊 JSON report saved: {self.json_file}")
