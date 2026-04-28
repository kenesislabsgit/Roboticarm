# System Architecture

Technical documentation for Safety Interlock System architecture.

## Overview

Modular design with clear separation of concerns:

```
┌─────────────┐
│   main.py   │  Entry point
└──────┬──────┘
       │
       ▼
┌──────────────────────────┐
│   VideoProcessor         │  Orchestrator
│   (video_processor.py)   │
└─┬──────┬──────┬──────┬──┘
  │      │      │      │
  ▼      ▼      ▼      ▼
┌────┐ ┌────┐ ┌────┐ ┌────┐
│Det │ │Zone│ │Stat│ │Log │  Components
│ect │ │Mgr │ │e M │ │ger │
│or  │ │    │ │ach │ │    │
└────┘ └────┘ └────┘ └────┘
```

## Component Details

### 1. main.py

**Purpose:** Entry point, CLI interface

**Responsibilities:**
- Parse command-line arguments
- Validate video file
- Initialize VideoProcessor
- Handle errors and interruptions

**Flow:**
```python
main()
├── Validate arguments
├── Check file exists
├── Create VideoProcessor
├── Define zone
├── Process video
└── Display results
```

### 2. VideoProcessor (video_processor.py)

**Purpose:** Main orchestrator, coordinates all components

**Key Methods:**

```python
__init__(video_path, zone_coords)
    # Load video, initialize components

define_zone()
    # Interactive or predefined zone setup

process()
    # Main processing loop
    while has_frames:
        read_frame()
        detect_persons()
        update_state()
        log_events()
        visualize()

_process_frame(frame, frame_num, timestamp)
    # Process single frame
    detect → update → log → visualize

_annotate_frame(frame, detections, state)
    # Draw visualizations

_finalize()
    # Generate reports, cleanup
```

**Data Flow:**
```
Video → Frame → Detector → Detections
                             ↓
                        Zone Manager (overlap)
                             ↓
                        State Machine (trigger)
                             ↓
                        Logger (record)
                             ↓
                        Visualize (optional)
```

### 3. PersonDetector (detector.py)

**Purpose:** YOLO-based person detection

**Key Methods:**

```python
__init__(model_name)
    # Load YOLO model, setup GPU

detect(frame, confidence_threshold)
    # Single frame detection
    returns: [{
        'bbox': [x1, y1, x2, y2],
        'confidence': float,
        'class': 'person'
    }]

detect_batch(frames)
    # Batch processing (future optimization)
```

**Implementation:**
- Uses Ultralytics YOLO
- Filters for person class (ID=0)
- Applies confidence threshold
- GPU-accelerated if available

**Performance:**
- yolov8n: ~50ms/frame (GPU)
- yolov8s: ~80ms/frame (GPU)
- yolov8m: ~120ms/frame (GPU)

### 4. ZoneManager (zone_manager.py)

**Purpose:** Danger zone definition and overlap calculation

**Key Methods:**

```python
__init__(zone_coords)
    # Initialize with coordinates or None

define_zone_interactive(frame)
    # User clicks to define zone
    returns: [(x,y), ...]

calculate_overlap(bbox)
    # Calculate bbox overlap with zone
    returns: 0.0 to 1.0

is_near_boundary(bbox)
    # Check if near zone edge

draw_zone(frame)
    # Visualize zone on frame

save_zone(filepath)
    # Persist zone coordinates

load_zone(filepath)
    # Load saved zone
```

**Overlap Calculation:**
```
person_box = Rectangle(x1, y1, x2, y2)
zone_poly = Polygon(points)

intersection = person_box ∩ zone_poly
overlap_ratio = intersection.area / person_box.area
```

Uses Shapely library for geometric operations.

### 5. SafetyStateMachine (state_machine.py)

**Purpose:** State management and trigger logic

**States:**
```python
class State(Enum):
    CLEAR = "CLEAR"      # No person or outside
    WARNING = "WARNING"  # Approaching
    DANGER = "DANGER"    # Inside zone
```

**State Transitions:**
```
CLEAR ⟷ WARNING ⟷ DANGER

Triggers:
- CLEAR → WARNING: Person detected
- WARNING → DANGER: STOP signal (entry)
- DANGER → WARNING: Person leaving
- WARNING → CLEAR: RESUME signal (exit)
```

**Key Methods:**

```python
update(detections, zone_manager, frame_num, timestamp)
    # Main update loop
    classify_state()
    apply_smoothing()
    check_transitions()
    generate_events()
    
    returns: {
        'state': State,
        'changed': bool,
        'triggered': bool,
        'event': dict
    }

_classify_state(detections)
    # Determine state from overlaps
    if max_overlap >= DANGER_THRESHOLD:
        return DANGER
    elif max_overlap > 0:
        return WARNING
    else:
        return CLEAR

_get_smoothed_state()
    # Temporal smoothing (anti-flicker)
    # Majority vote over last N frames
```

**Hysteresis:**
```
Enter DANGER: overlap >= 0.50 (50%)
Exit DANGER:  overlap < 0.40 (40%)

Prevents jitter at boundary.
```

**Temporal Smoothing:**
```
Frame buffer: [WARNING, WARNING, DANGER, DANGER, DANGER]
Majority vote: DANGER (3/5)

Prevents false triggers from single frame misdetections.
```

### 6. SafetyLogger (logger.py)

**Purpose:** Event logging and report generation

**Key Methods:**

```python
__init__(video_name)
    # Setup log files

log_event(event, frame)
    # Record state transition
    # Save frame if trigger

log_frame_detection(frame_num, timestamp, detections, state)
    # Detailed per-frame logging

save_frame(frame, frame_num, label)
    # Save screenshot

generate_report(stats, video_info, zone_info, detector_info)
    # Final summary report
```

**Output Files:**
```
output/
├── logs/
│   ├── log_20260413_203500.txt    # Human-readable
│   └── log_20260413_203500.json   # Machine-readable
├── frames/
│   ├── frame_00489_STOP.jpg       # Trigger screenshots
│   └── frame_00654_RESUME.jpg
└── annotated_test_video.mp4       # Visualization
```

**Log Format:**
```
[Frame 00489 | 16.30s] 🚨 STOP: Person entered danger zone | Persons: 1 | Confidence: 0.94 | Overlap: 58.0%
```

**JSON Structure:**
```json
{
  "run_info": {...},
  "video_info": {...},
  "detector_info": {...},
  "zone_info": {...},
  "statistics": {
    "trigger_count": 2,
    "stop_events": 2,
    "resume_events": 2,
    "total_danger_time": 5.5
  },
  "events": [...]
}
```

### 7. config.py

**Purpose:** Centralized configuration

**Categories:**

```python
# Detection
YOLO_MODEL = "yolov8n.pt"
CONFIDENCE_THRESHOLD = 0.7

# Zone Overlap
DANGER_THRESHOLD = 0.50
HYSTERESIS_EXIT = 0.40

# State Machine
TEMPORAL_SMOOTHING_FRAMES = 3
ENABLE_HYSTERESIS = True

# Performance
USE_GPU = True
SKIP_FRAMES = 0

# Output
SAVE_ANNOTATED_VIDEO = True
DISPLAY_PREVIEW = True
```

**Why Centralized:**
- Single source of truth
- Easy experimentation
- No code changes needed
- Version control friendly

### 8. utils.py

**Purpose:** Helper functions

**Functions:**
- `format_time()` - Pretty time formatting
- `calculate_iou()` - Bounding box IoU
- `resize_frame()` - Maintain aspect ratio
- `draw_text_with_background()` - Readable overlays
- `validate_video_file()` - Pre-flight checks

## Data Structures

### Detection Object
```python
{
    'bbox': [x1, y1, x2, y2],  # Pixel coordinates
    'confidence': 0.94,         # 0-1
    'class': 'person',          # Always "person"
    'overlap': 0.58             # Added by ZoneManager
}
```

### Event Object
```python
{
    'type': 'STOP',             # STOP, RESUME, WARNING, CLEAR
    'description': str,
    'frame': 489,
    'timestamp': 16.30,
    'old_state': 'WARNING',
    'new_state': 'DANGER',
    'num_persons': 1,
    'max_confidence': 0.94,
    'max_overlap': 0.58
}
```

### Video Info
```python
{
    'filename': 'test.mp4',
    'width': 1920,
    'height': 1080,
    'fps': 30.0,
    'total_frames': 1500,
    'duration': 50.0
}
```

## Processing Pipeline

### Startup Sequence
```
1. Load video (VideoProcessor.__init__)
2. Initialize YOLO (PersonDetector.__init__)
   - Download model if needed (~6MB)
   - Move to GPU if available
3. Define zone (VideoProcessor.define_zone)
   - Interactive or predefined
   - Create Shapely polygon
4. Initialize state machine (SafetyStateMachine.__init__)
5. Create logger (SafetyLogger.__init__)
```

### Frame Processing Loop
```
For each frame:
    1. Read frame from video (OpenCV)
    2. Run YOLO detection (PersonDetector.detect)
       - Neural network inference
       - Filter person class
       - Apply confidence threshold
    3. Calculate overlaps (ZoneManager.calculate_overlap)
       - For each detected person
       - Compute intersection with zone polygon
    4. Update state machine (SafetyStateMachine.update)
       - Classify state based on max overlap
       - Apply temporal smoothing
       - Check for transitions
       - Generate events
    5. Log events (SafetyLogger.log_event)
       - Write to log file
       - Save trigger frames
    6. Visualize (VideoProcessor._annotate_frame)
       - Draw zone boundary
       - Draw bounding boxes
       - Draw state indicator
    7. Display/Save (optional)
       - Show preview window
       - Write to output video
```

### Shutdown Sequence
```
1. Close video capture
2. Close video writer
3. Generate final report (SafetyLogger.generate_report)
   - Text report
   - JSON report
4. Display statistics
5. Release resources
```

## Performance Characteristics

### Time Complexity

**Per frame:**
- Detection: O(1) - Fixed neural network
- Overlap: O(n×m) - n=persons, m=zone vertices
- State update: O(k) - k=smoothing frames (small constant)
- Total: **O(1)** dominated by YOLO inference

**Full video:**
- O(F) where F=number of frames
- Linear scaling with video length

### Space Complexity

**Memory usage:**
- YOLO model: ~6MB (yolov8n) to ~130MB (yolov8x)
- Video frame: ~6MB (1920×1080×3)
- State history: ~1KB (few frames)
- Event log: ~1KB per event
- Total: **~20-150MB** depending on model

### Bottlenecks

1. **YOLO Inference** (dominant)
   - GPU: 50-200ms per frame
   - CPU: 200-1000ms per frame
   - Solution: Use GPU, smaller model, skip frames

2. **Video I/O**
   - Reading: 1-5ms
   - Writing: 5-10ms
   - Usually negligible

3. **Overlap Calculation**
   - <1ms per person
   - Negligible

## Extension Points

### Adding New Detection Models

```python
# detector.py
class CustomDetector:
    def detect(self, frame):
        # Your model here
        return detections
```

### Custom State Logic

```python
# state_machine.py
def _classify_state(self, detections):
    # Custom logic
    if custom_condition:
        return State.CUSTOM
```

### Hardware Integration

```python
# state_machine.py
def _on_state_transition(self, old, new, ...):
    if new == State.DANGER:
        self._send_stop_signal()  # Add here

def _send_stop_signal(self):
    # Serial/TCP/GPIO communication
    pass
```

### Additional Alerts

```python
# logger.py
def log_event(self, event, frame):
    super().log_event(event, frame)
    if event['type'] == 'STOP':
        self._send_email_alert()  # Add here
```

## Testing Strategy

### Unit Tests
```
detector.py:
- Test person detection accuracy
- Test confidence filtering
- Test GPU/CPU modes

zone_manager.py:
- Test overlap calculation
- Test boundary conditions
- Test zone saving/loading

state_machine.py:
- Test state transitions
- Test hysteresis
- Test temporal smoothing

logger.py:
- Test log file creation
- Test event formatting
- Test report generation
```

### Integration Tests
```
Full pipeline:
- Known input video → expected triggers
- Edge cases (fast motion, occlusion)
- Performance benchmarks
```

### Validation Tests
```
Safety validation:
- 0 false negatives (no missed detections)
- <5% false positives (acceptable nuisance)
- <100ms latency (trigger timing)
```

## Design Decisions

### Why YOLO?
- Fast (real-time capable)
- Accurate (state-of-art)
- Pre-trained (no custom training needed)
- Well-supported (Ultralytics)

### Why Shapely?
- Robust geometry operations
- Handles complex polygons
- Industry standard
- Well-tested

### Why Modular Design?
- Easy to test components independently
- Easy to replace/upgrade components
- Clear separation of concerns
- Future-proof for hardware integration

### Why Config File?
- No code changes for experiments
- Version control friendly
- Easy A/B testing
- Production vs. test configurations

## Future Enhancements

1. **Multi-camera fusion**
   - Combine views from multiple cameras
   - 3D position estimation

2. **Pose estimation**
   - Detect unusual postures (falling, crawling)
   - Better occlusion handling

3. **Object detection**
   - Detect tools, equipment in danger zone
   - Differentiate workers from visitors

4. **Predictive alerts**
   - Machine learning on trajectories
   - Predict entries before they happen

5. **Hardware integration**
   - Direct PLC communication
   - Robot control interface
   - External alarm systems

6. **Cloud connectivity**
   - Remote monitoring
   - Centralized logging
   - Analytics dashboard

7. **Model retraining**
   - Fine-tune on facility-specific data
   - Handle PPE, lighting variations
   - Improve accuracy

## Performance Tuning Guide

### For Speed
1. Use `yolov8n.pt`
2. Enable GPU
3. Set `SKIP_FRAMES = 1`
4. Disable `SAVE_ANNOTATED_VIDEO`
5. Disable `DISPLAY_PREVIEW`

### For Accuracy
1. Use `yolov8m.pt` or larger
2. Lower `CONFIDENCE_THRESHOLD = 0.6`
3. Increase `TEMPORAL_SMOOTHING_FRAMES = 5`
4. Enable `ENABLE_HYSTERESIS = True`
5. Process all frames (`SKIP_FRAMES = 0`)

### For Reliability
1. Enable temporal smoothing
2. Enable hysteresis
3. Use ensemble of models
4. Add redundant cameras
5. Hardware interlock as primary safety

## Maintenance

### Regular Tasks
- Update dependencies monthly
- Test with new videos weekly
- Review false positives/negatives
- Retrain model with new data (if applicable)

### Monitoring
- Track detection confidence over time
- Monitor false positive rate
- Log processing time per frame
- Check GPU utilization

### Debugging
- Enable `DETAILED_LOG = True`
- Save all detection frames
- Compare different YOLO models
- Test with simplified scenarios

---

**Document Version:** 1.0  
**Last Updated:** 2026-04-13  
**Author:** WEG Safety Team
