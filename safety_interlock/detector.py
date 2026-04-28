"""
Person Detection Module
Uses YOLOv8 for real-time person detection
"""

import torch
from ultralytics import YOLO
import numpy as np
from . import config


class PersonDetector:
    """Detects persons in video frames using YOLO"""

    def __init__(self, model_name=None):
        """
        Initialize YOLO detector

        Args:
            model_name: YOLO model variant (default from config)
        """
        self.model_name = model_name or config.YOLO_MODEL
        self.confidence_threshold = config.CONFIDENCE_THRESHOLD

        print(f"Loading YOLO model: {self.model_name}")
        self.model = YOLO(self.model_name)

        # Check for GPU
        self.device = 'cuda' if config.USE_GPU and torch.cuda.is_available() else 'cpu'
        print(f"Using device: {self.device}")
        if self.device == 'cuda':
            print(f"GPU: {torch.cuda.get_device_name(0)}")

        self.model.to(self.device)

        # COCO dataset class ID for person
        self.PERSON_CLASS_ID = 0

    def detect(self, frame, confidence_threshold=None):
        """
        Detect persons in a frame

        Args:
            frame: OpenCV image (numpy array)
            confidence_threshold: Override default confidence (optional)

        Returns:
            List of detections: [
                {
                    'bbox': [x1, y1, x2, y2],
                    'confidence': float,
                    'class': 'person'
                },
                ...
            ]
        """
        threshold = confidence_threshold or self.confidence_threshold

        # Run inference
        results = self.model(frame, verbose=False)[0]

        detections = []

        # Extract person detections
        for box in results.boxes:
            class_id = int(box.cls[0])
            confidence = float(box.conf[0])

            # Filter: only persons with sufficient confidence
            if class_id == self.PERSON_CLASS_ID and confidence >= threshold:
                bbox = box.xyxy[0].cpu().numpy()  # [x1, y1, x2, y2]

                detections.append({
                    'bbox': bbox.tolist(),
                    'confidence': confidence,
                    'class': 'person'
                })

        return detections

    def detect_batch(self, frames, confidence_threshold=None):
        """
        Detect persons in multiple frames (batch processing)

        Args:
            frames: List of OpenCV images
            confidence_threshold: Override default confidence

        Returns:
            List of detection lists (one per frame)
        """
        threshold = confidence_threshold or self.confidence_threshold

        # Batch inference
        results = self.model(frames, verbose=False)

        all_detections = []

        for result in results:
            frame_detections = []

            for box in result.boxes:
                class_id = int(box.cls[0])
                confidence = float(box.conf[0])

                if class_id == self.PERSON_CLASS_ID and confidence >= threshold:
                    bbox = box.xyxy[0].cpu().numpy()

                    frame_detections.append({
                        'bbox': bbox.tolist(),
                        'confidence': confidence,
                        'class': 'person'
                    })

            all_detections.append(frame_detections)

        return all_detections

    def get_model_info(self):
        """Get information about loaded model"""
        return {
            'model': self.model_name,
            'device': self.device,
            'confidence_threshold': self.confidence_threshold
        }
