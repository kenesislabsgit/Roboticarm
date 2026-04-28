"""
Zone Manager Module
Handles danger zone definition and person-zone overlap calculations
"""

import cv2
import numpy as np
from shapely.geometry import Polygon, box
from . import config


class ZoneManager:
    """Manages danger zone definition and overlap detection"""

    def __init__(self, zone_coords=None):
        """
        Initialize zone manager

        Args:
            zone_coords: List of (x,y) tuples defining zone polygon
                        If None, will require interactive definition
        """
        self.zone_coords = zone_coords or config.PREDEFINED_ZONE
        self.zone_polygon = None

        if self.zone_coords:
            self._create_polygon()

    def _create_polygon(self):
        """Create Shapely polygon from coordinates"""
        if len(self.zone_coords) < 3:
            raise ValueError("Zone must have at least 3 points")

        self.zone_polygon = Polygon(self.zone_coords)
        print(f"Zone defined with {len(self.zone_coords)} points")
        print(f"Zone area: {self.zone_polygon.area:.0f} pixels²")

    def define_zone_interactive(self, frame):
        """
        Let user define zone by clicking on frame

        Args:
            frame: First frame of video to display

        Returns:
            List of (x,y) coordinates
        """
        print("\n=== INTERACTIVE ZONE DEFINITION ===")
        print("Click to define danger zone boundary (minimum 3 points)")
        print("Press ENTER when done")
        print("Press 'r' to reset")
        print("Press 'q' to quit")

        points = []
        frame_copy = frame.copy()

        def mouse_callback(event, x, y, flags, param):
            if event == cv2.EVENT_LBUTTONDOWN:
                points.append((x, y))
                # Draw point
                cv2.circle(frame_copy, (x, y), 5, (0, 255, 0), -1)
                # Draw line to previous point
                if len(points) > 1:
                    cv2.line(frame_copy, points[-2], points[-1], (0, 255, 0), 2)
                # Update display
                temp = frame_copy.copy()
                if len(points) > 2:
                    cv2.polylines(temp, [np.array(points)], True, (0, 255, 0), 2)
                cv2.imshow("Define Danger Zone", temp)

        cv2.namedWindow("Define Danger Zone")
        cv2.setMouseCallback("Define Danger Zone", mouse_callback)
        cv2.imshow("Define Danger Zone", frame_copy)

        while True:
            # Draw current polygon
            temp = frame_copy.copy()
            if len(points) > 2:
                cv2.polylines(temp, [np.array(points)], True, (0, 255, 0), 2)
                # Fill with transparency
                overlay = temp.copy()
                cv2.fillPoly(overlay, [np.array(points)], (0, 255, 0))
                temp = cv2.addWeighted(temp, 0.8, overlay, 0.2, 0)

            # Show point count
            cv2.putText(temp, f"Points: {len(points)} (min 3)", (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

            cv2.imshow("Define Danger Zone", temp)

            key = cv2.waitKey(100) & 0xFF

            if key == 13:  # ENTER
                if len(points) >= 3:
                    break
                else:
                    print("Need at least 3 points!")
            elif key == ord('r'):  # Reset
                points = []
                frame_copy = frame.copy()
                cv2.imshow("Define Danger Zone", frame_copy)
            elif key == ord('q'):  # Quit
                cv2.destroyAllWindows()
                return None

        cv2.destroyAllWindows()

        self.zone_coords = points
        self._create_polygon()

        return points

    def calculate_overlap(self, bbox):
        """
        Calculate what % of person bounding box overlaps with danger zone

        Args:
            bbox: [x1, y1, x2, y2] person bounding box

        Returns:
            float: Overlap ratio (0.0 to 1.0)
        """
        if self.zone_polygon is None:
            raise ValueError("Zone not defined! Call define_zone_interactive() first")

        # Create person polygon from bbox
        person_box = box(bbox[0], bbox[1], bbox[2], bbox[3])

        # Calculate intersection
        try:
            intersection = self.zone_polygon.intersection(person_box)
            intersection_area = intersection.area
        except Exception as e:
            print(f"Warning: Overlap calculation failed: {e}")
            return 0.0

        # Calculate person area
        person_area = person_box.area

        if person_area == 0:
            return 0.0

        # Overlap ratio
        overlap_ratio = intersection_area / person_area

        return overlap_ratio

    def is_near_boundary(self, bbox, threshold_distance=50):
        """
        Check if person is near zone boundary (for adaptive confidence)

        Args:
            bbox: [x1, y1, x2, y2]
            threshold_distance: pixels from boundary to consider "near"

        Returns:
            bool: True if near boundary
        """
        if self.zone_polygon is None:
            return False

        # Get person center point
        center_x = (bbox[0] + bbox[2]) / 2
        center_y = (bbox[1] + bbox[3]) / 2

        from shapely.geometry import Point
        person_center = Point(center_x, center_y)

        # Distance to zone boundary
        distance = self.zone_polygon.boundary.distance(person_center)

        return distance <= threshold_distance

    def draw_zone(self, frame, color=None, thickness=None):
        """
        Draw danger zone on frame

        Args:
            frame: OpenCV image
            color: BGR color tuple (default from config)
            thickness: Line thickness (default from config)

        Returns:
            frame with zone drawn
        """
        if self.zone_coords is None:
            return frame

        color = color or config.ZONE_COLOR
        thickness = thickness or config.ZONE_THICKNESS

        points = np.array(self.zone_coords, dtype=np.int32)
        cv2.polylines(frame, [points], True, color, thickness)

        # Semi-transparent fill
        overlay = frame.copy()
        cv2.fillPoly(overlay, [points], color)
        frame = cv2.addWeighted(frame, 0.9, overlay, 0.1, 0)

        return frame

    def get_zone_info(self):
        """Get zone information"""
        if self.zone_polygon is None:
            return None

        return {
            'points': self.zone_coords,
            'num_points': len(self.zone_coords),
            'area': self.zone_polygon.area,
            'bounds': self.zone_polygon.bounds  # (minx, miny, maxx, maxy)
        }

    def save_zone(self, filepath):
        """Save zone coordinates to file"""
        import json

        if self.zone_coords is None:
            raise ValueError("No zone defined")

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump({
                'zone_coords': self.zone_coords,
                'area': self.zone_polygon.area
            }, f, indent=2)

        print(f"Zone saved to {filepath}")

    def load_zone(self, filepath):
        """Load zone coordinates from file"""
        import json

        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        self.zone_coords = [tuple(p) for p in data['zone_coords']]
        self._create_polygon()

        print(f"Zone loaded from {filepath}")
