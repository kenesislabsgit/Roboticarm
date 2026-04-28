# Quick Start Guide

Get up and running with Safety Interlock System in 5 minutes.

## Prerequisites

- Python 3.9+
- Test video file
- 2GB free disk space

## Installation (2 minutes)

### 1. Install Dependencies

```bash
pip install torch torchvision ultralytics opencv-python shapely numpy
```

Wait for downloads to complete (~500MB).

### 2. Verify Installation

```bash
python -c "from ultralytics import YOLO; print('✓ Ready')"
```

Should print: `✓ Ready`

## First Run (3 minutes)

### 1. Prepare Video

Place test video in `videos/` folder:

```bash
videos/test_video.mp4
```

**Video must show:**
- Robot/machine operating
- Clear view of danger zone (fenced area)
- Person entering the zone

### 2. Run System

```bash
python main.py videos/test_video.mp4
```

### 3. Define Zone

**Interactive zone definition window appears:**

1. **Click 4+ corners** around danger zone (yellow fence in your case)
2. **Press ENTER** when done
3. Window closes, processing starts

**Tips:**
- Click in clockwise order
- Include entire fenced area
- Don't click on objects, click on floor boundary
- Press 'r' to reset if mistake

### 4. Watch Processing

**Console shows:**
```
📹 Video loaded: test_video.mp4
   Resolution: 1920x1080
   FPS: 30.00
   Frames: 1500
   Duration: 50.00s

🔧 Initializing components...
Loading YOLO model: yolov8n.pt
Using device: cuda
GPU: NVIDIA GeForce RTX 3060

🚀 Starting video processing...

⏳ Progress: 20.0% (300/1500 frames)
[Frame 00487] ⚠️  WARNING: Person approaching
[Frame 00489] 🚨 STOP: Person entered danger zone | Confidence: 0.94 | Overlap: 58%
  💾 Saved: output/frames/frame_00489_STOP.jpg
⏳ Progress: 40.0% (600/1500 frames)
[Frame 00654] ✅ RESUME: Person left danger zone
  💾 Saved: output/frames/frame_00654_RESUME.jpg
⏳ Progress: 100.0% (1500/1500 frames)

✅ Processing complete!
```

### 5. Check Results

**Output files created:**

```
output/
├── logs/
│   ├── log_20260413_203500.txt     ← Read this first
│   └── log_20260413_203500.json
├── frames/
│   ├── frame_00489_STOP.jpg        ← Exact moment of trigger
│   └── frame_00654_RESUME.jpg      ← Person exiting
├── annotated_test_video.mp4        ← Watch this
└── zone_definition.json            ← Saved for reuse
```

## Understanding Results

### 1. Open Log File

```bash
cat output/logs/log_20260413_203500.txt
```

**Look for:**
- ✅ Total trigger events
- ✅ Time in danger zone
- ✅ Detection confidence

**Example:**
```
=== DETECTION SUMMARY ===
Total Events: 4
STOP Triggers: 2
RESUME Events: 2
Total Danger Time: 5.50 seconds
```

### 2. View Trigger Frames

**Open:** `output/frames/frame_00489_STOP.jpg`

**Check:**
- ✓ Person visible in frame?
- ✓ Person inside yellow zone boundary?
- ✓ Red bounding box around person?
- ✓ Frame number and timestamp shown?

### 3. Watch Annotated Video

**Open:** `output/annotated_test_video.mp4`

**You'll see:**
- 🟦 Cyan zone boundary
- 🟢 Green box = person outside (CLEAR)
- 🟡 Yellow box = person approaching (WARNING)
- 🔴 Red box = person inside (DANGER)
- State label in top-left corner

## Interpreting States

### State: CLEAR 🟢
- No person detected, or
- Person detected but far from zone
- **Robot action:** Continue normal operation

### State: WARNING ⚠️
- Person detected and approaching zone
- Not yet inside
- **Robot action:** Slow down (precautionary)

### State: DANGER 🚨
- Person inside danger zone boundary
- **Robot action:** STOP IMMEDIATELY

## Common Issues

### Issue: No person detected

**Symptoms:** Video processes but no WARNING/DANGER states

**Solutions:**
1. Check person clearly visible in video
2. Lower confidence threshold:
   ```python
   # Edit safety_interlock/config.py
   CONFIDENCE_THRESHOLD = 0.6
   ```
3. Check zone defined correctly (reload video and redefine)

### Issue: Too many false triggers

**Symptoms:** DANGER state when person outside zone

**Solutions:**
1. Increase danger threshold:
   ```python
   DANGER_THRESHOLD = 0.60  # Require 60% overlap
   ```
2. Redefine zone (make it smaller/tighter)

### Issue: Processing very slow

**Symptoms:** Takes >10 seconds per second of video

**Solutions:**
1. Check GPU being used (startup messages)
2. Use faster model:
   ```python
   YOLO_MODEL = "yolov8n.pt"  # Already fastest
   ```
3. Skip frames:
   ```python
   SKIP_FRAMES = 1  # Process every other frame
   ```

### Issue: Person detected late

**Symptoms:** Trigger happens after person already inside

**Solutions:**
1. Make zone larger (include approach area)
2. Use WARNING zone for early detection
3. Lower overlap threshold:
   ```python
   DANGER_THRESHOLD = 0.40  # Trigger at 40%
   ```

## Next Steps

### Test Different Scenarios

1. **Empty zone (baseline)**
   - Process video with no person
   - Should stay CLEAR throughout

2. **Person walks through**
   - Enter, pause, exit
   - Check trigger timing accurate

3. **Multiple persons**
   - 2+ people, 1 enters zone
   - Should trigger for person inside only

4. **Fast movement**
   - Person runs into zone
   - Check detection within 2 frames

### Tune Configuration

**Edit:** `safety_interlock/config.py`

Try different values:
```python
# More sensitive (earlier triggers)
CONFIDENCE_THRESHOLD = 0.6
DANGER_THRESHOLD = 0.40

# Less sensitive (fewer false positives)
CONFIDENCE_THRESHOLD = 0.8
DANGER_THRESHOLD = 0.60

# Smoother (less jitter)
TEMPORAL_SMOOTHING_FRAMES = 5
ENABLE_HYSTERESIS = True
```

Run again and compare results.

### Process Multiple Videos

**Batch processing:**

```bash
python example_advanced.py
# Select option 3: Batch processing
```

Processes all videos in `videos/` folder automatically.

### Save Your Zone

Zone auto-saved to: `output/zone_definition.json`

**Reuse in future:**
```python
# In your script
from safety_interlock import ZoneManager

zone_mgr = ZoneManager()
zone_mgr.load_zone("output/zone_definition.json")
```

No need to redefine interactively.

## Success Criteria

**Your MVP is working if:**

✅ Person detected with >90% confidence  
✅ Trigger fires within 2 frames of zone entry  
✅ No missed entries (0% false negatives)  
✅ <5% false positive rate acceptable  
✅ Processing speed ≥10fps (for 30fps video)  

**If all ✅, ready for:**
- More test videos
- Different lighting conditions
- Different people/clothing
- Edge cases (bending, kneeling)

## Quick Commands Reference

```bash
# Basic run
python main.py videos/test.mp4

# With saved zone (no interactive)
python main.py videos/test2.mp4

# Advanced examples
python example_advanced.py

# Check GPU
python -c "import torch; print(torch.cuda.is_available())"

# Verify install
python -c "from ultralytics import YOLO; print('OK')"
```

## Performance Targets

| Metric | Target | Check |
|--------|--------|-------|
| Detection confidence | >0.85 | Log file |
| Trigger latency | <100ms | Frame diff |
| False negatives | 0% | Manual review |
| False positives | <5% | Manual review |
| Processing speed | ≥10fps | Console output |

## What to Report

When testing, record:

1. **Video info:**
   - Resolution, FPS, duration
   - Lighting conditions
   - Camera angle

2. **Detection results:**
   - Total triggers
   - False positives (triggered but shouldn't)
   - False negatives (missed entry)
   - Average confidence

3. **Performance:**
   - Processing time (total)
   - FPS achieved
   - GPU used?

4. **Issues:**
   - Missed detections (with frame numbers)
   - Incorrect triggers (with frame numbers)
   - Any errors/warnings

## Getting Help

**Check documentation:**
- `README.md` - Full overview
- `INSTALL.md` - Installation details
- `ARCHITECTURE.md` - Technical deep-dive

**Common fixes:**
- Update dependencies: `pip install --upgrade -r requirements.txt`
- Fresh environment: Create new venv
- Simpler video: Test with 720p 30fps first

**Report issues with:**
- Python version
- GPU model (if using)
- Error message (full traceback)
- Video specifications

---

**Time to first result:** ~5 minutes  
**Learning curve:** Minimal (just click zone, run)  
**Complexity:** Abstracted away (all in config)

Ready? Run: `python main.py videos/test_video.mp4`
