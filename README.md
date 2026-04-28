# Safety Interlock System

AI-based human detection system for robotic cell safety. Detects when persons enter dangerous zones and triggers emergency stop signals.

## 🎯 Purpose

MVP (Minimum Viable Product) for testing person detection algorithms before hardware integration. Validates detection accuracy, trigger timing, and system reliability on video footage.

## 📁 Project Structure

```
WEG/
├── safety_interlock/           # Core system modules
│   ├── __init__.py            # Package initialization
│   ├── config.py              # All settings and thresholds
│   ├── detector.py            # YOLO person detection
│   ├── zone_manager.py        # Danger zone definition & overlap
│   ├── state_machine.py       # State transitions & trigger logic
│   ├── video_processor.py     # Main processing orchestrator
│   └── logger.py              # Logging & report generation
│
├── main.py                     # Entry point
├── requirements.txt            # Python dependencies
├── README.md                   # This file
│
├── videos/                     # Test videos (place here)
├── output/                     # Processing results
│   ├── logs/                  # Text and JSON logs
│   └── frames/                # Saved trigger frames
└── models/                     # YOLO weights (auto-downloaded)
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- **PyTorch**: Deep learning framework
- **Ultralytics**: YOLOv8 implementation
- **OpenCV**: Video processing
- **Shapely**: Geometry calculations

### 2. Prepare Test Video

Place your test video in the `videos/` directory:

```bash
videos/test_robot_cell.mp4
```

**Video requirements:**
- Resolution: 1080p recommended (720p minimum)
- FPS: 30fps minimum
- Format: MP4, AVI, or MOV
- Camera angle: 30-45° elevated view
- Full danger zone visible in frame

### 3. Run Processing

```bash
python main.py videos/test_video.mp4
```

### 4. Define Danger Zone

On first run, you'll define the danger zone interactively:

1. Window shows first frame
2. Click to mark boundary points (minimum 3)
3. Press ENTER when done
4. Press 'r' to reset if needed

Zone coordinates saved to `output/zone_definition.json` for reuse.

### 5. View Results

System processes video and generates:

**Console Output:**
- Real-time progress and events
- State transitions (CLEAR → WARNING → DANGER)
- Trigger notifications

**Log Files:**
- `output/logs/log_YYYYMMDD_HHMMSS.txt` - Human-readable log
- `output/logs/log_YYYYMMDD_HHMMSS.json` - Machine-readable data

**Saved Frames:**
- `output/frames/frame_XXXXX_STOP.jpg` - Moment of trigger
- `output/frames/frame_XXXXX_RESUME.jpg` - Zone cleared

**Annotated Video:**
- `output/annotated_test_video.mp4` - Video with overlays

## ⚙️ Configuration

Edit `safety_interlock/config.py` to modify system behavior:

### Key Settings

```python
# Detection sensitivity
CONFIDENCE_THRESHOLD = 0.7        # Higher = fewer false positives
DANGER_THRESHOLD = 0.50           # % of person in zone to trigger
TEMPORAL_SMOOTHING_FRAMES = 3     # Anti-flicker smoothing

# Performance
YOLO_MODEL = "yolov8n.pt"         # n=fast, s/m/l=more accurate
USE_GPU = True                    # Enable CUDA acceleration
SKIP_FRAMES = 0                   # Process every Nth frame (0=all)

# Output
SAVE_ANNOTATED_VIDEO = True       # Save visualization
DISPLAY_PREVIEW = True            # Show live preview
DETAILED_LOG = True               # Per-frame logging
```

## 📊 Understanding Output

### State Machine

System has 3 states:

- **CLEAR** 🟢: No person detected or outside zone
- **WARNING** ⚠️: Person detected, approaching zone
- **DANGER** 🚨: Person inside danger zone (TRIGGER)

### Trigger Events

**STOP**: Person entered danger zone
- Robot should stop immediately
- Logged with frame number and timestamp

**RESUME**: Person left danger zone
- Safe to resume robot operation

### Log Format

```
[Frame 00489 | 16.30s] 🚨 STOP: Person entered danger zone | Persons: 1 | Confidence: 0.94 | Overlap: 58.0%
[Frame 00654 | 21.80s] ✅ RESUME: Person left danger zone
```

### Final Report

```
=== DETECTION SUMMARY ===
Total Events: 4
STOP Triggers: 2
RESUME Events: 2
WARNING Events: 3
Total Danger Time: 5.50 seconds
```

## 🔧 Modifying the System

### Change Detection Model

```python
# config.py
YOLO_MODEL = "yolov8s.pt"  # Options: n, s, m, l, x (nano to extra-large)
```

Larger models = more accurate but slower.

### Adjust Trigger Sensitivity

```python
# config.py
DANGER_THRESHOLD = 0.40  # Trigger when 40% of person in zone (more sensitive)
CONFIDENCE_THRESHOLD = 0.8  # Require 80% confidence (less sensitive)
```

### Enable Hysteresis (Prevent Jitter)

```python
# config.py
ENABLE_HYSTERESIS = True
HYSTERESIS_EXIT = 0.40  # Must drop below 40% to exit DANGER
```

Prevents rapid state changes at boundary.

### Add Hardware Integration

Future: Modify `state_machine.py` to send actual stop signals:

```python
# In _on_state_transition method
if event_type == "STOP":
    send_stop_signal()  # Your hardware integration here
```

## 🧪 Testing Protocol

### 1. Baseline Test

Record video:
- 10s robot operating, no person
- Expected: State = CLEAR throughout

### 2. Entry Detection

Record video:
- Person enters zone
- Expected: STOP trigger within 1-2 frames of crossing boundary

### 3. Exit Detection

Record video:
- Person exits zone
- Expected: RESUME trigger when fully outside

### 4. Multiple Persons

Record video:
- 2 persons, 1 enters zone, 1 stays outside
- Expected: STOP trigger for person inside

### 5. Edge Cases

Test scenarios:
- Person bending/kneeling in zone
- Fast entry (running)
- Partial occlusion (behind object)
- Lighting changes

### 6. Performance Metrics

Target metrics:
- **Detection rate**: >99% (no missed entries)
- **False positives**: <5% (acceptable nuisance)
- **Trigger latency**: <100ms (1-3 frames at 30fps)
- **Boundary accuracy**: ±10cm

## 📈 Performance Optimization

### Speed Up Processing

1. **Use smaller model:**
   ```python
   YOLO_MODEL = "yolov8n.pt"  # Fastest
   ```

2. **Skip frames:**
   ```python
   SKIP_FRAMES = 1  # Process every other frame
   ```

3. **Disable visualization:**
   ```python
   DISPLAY_PREVIEW = False
   SAVE_ANNOTATED_VIDEO = False
   ```

4. **Enable GPU:**
   Ensure CUDA installed:
   ```bash
   pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
   ```

### Improve Accuracy

1. **Use larger model:**
   ```python
   YOLO_MODEL = "yolov8m.pt"  # More accurate
   ```

2. **Lower confidence threshold near boundary:**
   ```python
   CONFIDENCE_THRESHOLD_BOUNDARY = 0.5
   ```

3. **Increase temporal smoothing:**
   ```python
   TEMPORAL_SMOOTHING_FRAMES = 5  # More stable
   ```

## 🐛 Troubleshooting

### "Could not open video"
- Check file path is correct
- Ensure video codec supported (try converting to MP4 H.264)

### "CUDA out of memory"
- Use smaller model: `YOLO_MODEL = "yolov8n.pt"`
- Or disable GPU: `USE_GPU = False`

### Person not detected
- Check lighting (avoid silhouettes)
- Verify person clearly visible (not occluded)
- Lower confidence threshold: `CONFIDENCE_THRESHOLD = 0.5`

### False triggers
- Increase confidence threshold: `CONFIDENCE_THRESHOLD = 0.8`
- Increase danger threshold: `DANGER_THRESHOLD = 0.6`
- Enable hysteresis: `ENABLE_HYSTERESIS = True`

### Slow processing
- See "Performance Optimization" above
- Check if GPU being used (message at startup)

## 🔒 Safety Considerations

**CRITICAL**: This is an MVP for testing only.

For production deployment:
1. **Hardware interlock required** - AI is secondary layer
2. **Certified safety PLCs** - SIL 3 / PLe rated
3. **Redundant sensors** - Laser scanners as primary
4. **Third-party certification** - TÜV, UL, CSA audit
5. **Fail-safe design** - System failure = robot stop

AI vision alone **NOT sufficient** for life-safety applications.

## 📝 Next Steps

1. **Test with real footage** - Collect videos from actual robot cell
2. **Validate detection rate** - 1000+ test entries, 0 misses required
3. **Measure performance** - Latency, accuracy, false positive rate
4. **Hardware integration** - Connect to safety PLC
5. **Field testing** - Controlled deployment with safety backup
6. **Certification** - Third-party safety audit

## 📧 Support

For questions or issues, contact WEG Safety Team.

## 📄 License

Internal use only - WEG Safety Project
