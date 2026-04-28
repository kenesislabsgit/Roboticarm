"""
Video Processor Module
Main processing loop - orchestrates all components
"""

import cv2
import os
import numpy as np
from datetime import datetime
from . import config
from .detector import PersonDetector
from .zone_manager import ZoneManager
from .state_machine import SafetyStateMachine
from .logger import SafetyLogger

backend_server = None
try:
    import backend_server
except ImportError:
    backend_server = None


class VideoProcessor:
    """Main video processing orchestrator"""

    def __init__(self, video_path, zone_coords=None):
        """
        Initialize video processor

        Args:
            video_path: Path to video file
            zone_coords: Predefined zone coordinates (optional)
        """
        self.video_path = video_path
        self.video_name = os.path.basename(video_path)

        # Load video
        self.cap = cv2.VideoCapture(video_path)
        if not self.cap.isOpened():
            raise ValueError(f"Could not open video: {video_path}")

        # Get video properties
        self.fps = self.cap.get(cv2.CAP_PROP_FPS)
        self.total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.duration = self.total_frames / self.fps

        print(f"\n📹 Video loaded: {self.video_name}")
        print(f"   Resolution: {self.width}x{self.height}")
        print(f"   FPS: {self.fps:.2f}")
        print(f"   Frames: {self.total_frames}")
        print(f"   Duration: {self.duration:.2f}s")

        # Initialize components
        print("\n🔧 Initializing components...")
        self.detector = PersonDetector()
        self.zone_manager = ZoneManager(zone_coords)
        self.state_machine = SafetyStateMachine()
        self.logger = SafetyLogger(self.video_name)

        # Video writer for annotated output
        self.video_writer = None
        if config.SAVE_ANNOTATED_VIDEO:
            self._setup_video_writer()

        # Processing state
        self.frame_number = 0
        self.frames_processed = 0

    def _setup_video_writer(self):
        """Setup video writer for annotated output"""
        output_path = os.path.join(
            config.OUTPUT_DIR,
            f"annotated_{self.video_name}"
        )

        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        self.video_writer = cv2.VideoWriter(
            output_path,
            fourcc,
            self.fps,
            (self.width, self.height)
        )

        print(f"   Annotated video will be saved to: {output_path}")

    def define_zone(self, force_redefine=False):
        """
        Define danger zone interactively or load from config

        Args:
            force_redefine: If True, ignore saved zone and redefine interactively
        """
        if self.zone_manager.zone_coords is not None:
            print(f"✅ Using predefined zone with {len(self.zone_manager.zone_coords)} points")
            return

        # Check if saved zone exists (unless force redefine)
        zone_file = os.path.join(config.OUTPUT_DIR, "zone_definition.json")

        if not force_redefine and os.path.exists(zone_file):
            print(f"📂 Found saved zone definition: {zone_file}")
            try:
                self.zone_manager.load_zone(zone_file)
                print(f"✅ Loaded saved zone with {len(self.zone_manager.zone_coords)} points")
                return
            except Exception as e:
                print(f"⚠️  Could not load saved zone: {e}")
                print("   Will define zone interactively...")
        elif force_redefine:
            print("🔄 Force redefine zone requested")

        # Read first frame for interactive definition
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
        ret, frame = self.cap.read()

        if not ret:
            raise ValueError("Could not read first frame")

        # Interactive zone definition
        zone_coords = self.zone_manager.define_zone_interactive(frame)

        if zone_coords is None:
            raise ValueError("Zone definition cancelled")

        # Save zone for future use
        self.zone_manager.save_zone(zone_file)

    def process(self):
        """
        Main processing loop
        Processes entire video frame by frame
        """
        print("\n🚀 Starting video processing...\n")

        # Reset to start
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
        self.frame_number = 0

        while True:
            # Read frame
            ret, frame = self.cap.read()
            if not ret:
                break

            self.frame_number += 1
            timestamp = self.frame_number / self.fps

            # Skip frames if configured
            if config.SKIP_FRAMES > 0 and self.frame_number % (config.SKIP_FRAMES + 1) != 0:
                continue

            self.frames_processed += 1

            # Process frame
            self._process_frame(frame, self.frame_number, timestamp)

            # Show progress
            if self.frame_number % 30 == 0:  # Every 30 frames
                progress = (self.frame_number / self.total_frames) * 100
                print(f"⏳ Progress: {progress:.1f}% ({self.frame_number}/{self.total_frames} frames)")

        # Cleanup
        self._finalize()

    def _process_frame(self, frame, frame_number, timestamp):
        """
        Process a single frame

        Args:
            frame: OpenCV image
            frame_number: Frame number
            timestamp: Timestamp in seconds
        """
        # Detect persons
        detections = self.detector.detect(frame)

        # Update state machine
        result = self.state_machine.update(
            detections,
            self.zone_manager,
            frame_number,
            timestamp
        )

        # Log events
        if result['event']:
            self.logger.log_event(result['event'], frame)

            if result['triggered'] and backend_server:
                timestamp_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                backend_server.trigger_incident(frame.copy(), timestamp_str)

        # Log frame-level details
        if detections:
            self.logger.log_frame_detection(
                frame_number,
                timestamp,
                detections,
                result['state'].value
            )

        # Visualize and save
        if config.DISPLAY_PREVIEW or config.SAVE_ANNOTATED_VIDEO or backend_server:
            annotated_frame = self._annotate_frame(
                frame,
                detections,
                result['state']
            )

            if backend_server:
                backend_server.update_frame(annotated_frame)

            if config.DISPLAY_PREVIEW:
                cv2.imshow("Safety Interlock", annotated_frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    print("\n⚠️  Processing interrupted by user")
                    return

            if config.SAVE_ANNOTATED_VIDEO and self.video_writer:
                self.video_writer.write(annotated_frame)

    def _annotate_frame(self, frame, detections, state):
        """
        Draw visualizations on frame

        Args:
            frame: OpenCV image
            detections: List of detections
            state: Current State

        Returns:
            Annotated frame
        """
        annotated = frame.copy()

        # Draw zone
        annotated = self.zone_manager.draw_zone(annotated)

        # Draw detections
        for detection in detections:
            bbox = detection['bbox']
            confidence = detection['confidence']
            overlap = detection.get('overlap', 0)

            # Color based on state
            if state.value == "DANGER":
                color = config.BBOX_COLOR_DANGER
            elif state.value == "WARNING":
                color = config.BBOX_COLOR_WARNING
            else:
                color = config.BBOX_COLOR_CLEAR

            # Draw bounding box
            x1, y1, x2, y2 = map(int, bbox)
            cv2.rectangle(annotated, (x1, y1), (x2, y2), color, config.BBOX_THICKNESS)

            # Draw label
            label = f"Person {confidence:.2f} | {overlap*100:.0f}%"
            label_size, _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
            cv2.rectangle(annotated, (x1, y1 - label_size[1] - 5), (x1 + label_size[0], y1), color, -1)
            cv2.putText(annotated, label, (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

        # Draw state indicator
        state_text = f"STATE: {state.value}"
        state_color = {
            "CLEAR": (0, 255, 0),
            "WARNING": (0, 255, 255),
            "DANGER": (0, 0, 255)
        }.get(state.value, (255, 255, 255))

        cv2.rectangle(annotated, (10, 10), (300, 60), (0, 0, 0), -1)
        cv2.putText(annotated, state_text, (20, 45), cv2.FONT_HERSHEY_SIMPLEX, 1.2, state_color, 3)

        # Draw frame info
        frame_text = f"Frame: {self.frame_number} | Time: {self.frame_number/self.fps:.2f}s"
        cv2.putText(annotated, frame_text, (20, self.height - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)

        return annotated

    def _finalize(self):
        """Finalize processing and generate report"""
        print("\n✅ Processing complete!")

        # Release resources
        self.cap.release()
        if self.video_writer:
            self.video_writer.release()
        cv2.destroyAllWindows()

        # Generate report
        stats = self.state_machine.get_statistics()
        video_info = {
            'filename': self.video_name,
            'width': self.width,
            'height': self.height,
            'fps': self.fps,
            'total_frames': self.total_frames,
            'duration': self.duration,
            'frames_processed': self.frames_processed
        }
        zone_info = self.zone_manager.get_zone_info()
        detector_info = self.detector.get_model_info()

        self.logger.generate_report(stats, video_info, zone_info, detector_info)

        print("\n🎉 All done!")

    def get_statistics(self):
        """Get processing statistics"""
        return self.state_machine.get_statistics()
