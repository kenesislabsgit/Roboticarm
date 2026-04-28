# Installation Guide

Quick setup instructions for Safety Interlock System.

## Prerequisites

- **Python**: 3.9 or higher
- **pip**: Latest version
- **Git**: For cloning (optional)
- **CUDA**: Optional, for GPU acceleration

## Step-by-Step Installation

### 1. Check Python Version

```bash
python --version
```

Should show Python 3.9 or higher.

### 2. Create Virtual Environment (Recommended)

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**Linux/Mac:**
```bash
python -m venv venv
source venv/bin/activate
```

### 3. Upgrade pip

```bash
python -m pip install --upgrade pip
```

### 4. Install Dependencies

**CPU only:**
```bash
pip install -r requirements.txt
```

**With GPU support (CUDA 11.8):**
```bash
# Install PyTorch with CUDA first
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118

# Then install other dependencies
pip install ultralytics opencv-python shapely numpy
```

**With GPU support (CUDA 12.1):**
```bash
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121
pip install ultralytics opencv-python shapely numpy
```

### 5. Verify Installation

```bash
python -c "import torch; print(f'PyTorch: {torch.__version__}')"
python -c "import cv2; print(f'OpenCV: {cv2.__version__}')"
python -c "from ultralytics import YOLO; print('YOLO: OK')"
```

Should print versions without errors.

### 6. Check GPU (Optional)

```bash
python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}')"
python -c "import torch; print(f'GPU: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else \"None\"}')"
```

## First Run Test

### 1. Verify Structure

```bash
ls -la
```

Should see:
- `main.py`
- `safety_interlock/` directory
- `requirements.txt`
- `videos/` directory

### 2. Check Help

```bash
python main.py
```

Should show usage instructions.

### 3. Place Test Video

Put a test video in `videos/` directory:
```bash
videos/test_video.mp4
```

### 4. Run Processing

```bash
python main.py videos/test_video.mp4
```

First run will:
- Download YOLO model (~6MB for yolov8n.pt)
- Show first frame for zone definition
- Process video
- Generate reports

## Troubleshooting

### "No module named 'ultralytics'"

```bash
pip install ultralytics
```

### "Could not find a version that satisfies torch"

Update pip and try again:
```bash
python -m pip install --upgrade pip
pip install torch torchvision
```

### "CUDA out of memory"

Option 1: Use smaller model
```python
# Edit config.py
YOLO_MODEL = "yolov8n.pt"  # nano = smallest
```

Option 2: Disable GPU
```python
# Edit config.py
USE_GPU = False
```

### "Could not open video"

- Check file path is correct
- Try converting video to MP4 H.264:
  ```bash
  ffmpeg -i input.avi -c:v libx264 -c:a aac output.mp4
  ```

### Video Processing Very Slow

- Make sure GPU is being used (check startup messages)
- Use smaller model: `YOLO_MODEL = "yolov8n.pt"`
- Skip frames: `SKIP_FRAMES = 1`
- Disable preview: `DISPLAY_PREVIEW = False`

### ImportError with shapely

**Windows:**
```bash
pip install shapely --force-reinstall
```

**Linux:**
```bash
sudo apt-get install libgeos-dev
pip install shapely
```

## Performance Benchmarks

Expected processing speeds (1080p video):

| Hardware | Model | FPS |
|----------|-------|-----|
| CPU (i7) | yolov8n | 5-8 fps |
| CPU (i7) | yolov8s | 2-4 fps |
| GPU (RTX 3060) | yolov8n | 60+ fps |
| GPU (RTX 3060) | yolov8s | 45+ fps |
| GPU (RTX 3060) | yolov8m | 30+ fps |

## Next Steps

After successful installation:

1. **Run basic test:**
   ```bash
   python main.py videos/test_video.mp4
   ```

2. **Check output:**
   - `output/logs/` - Processing logs
   - `output/frames/` - Trigger screenshots
   - `output/annotated_*.mp4` - Visualization video

3. **Adjust configuration:**
   - Edit `safety_interlock/config.py`
   - Modify thresholds, model, etc.

4. **Run advanced examples:**
   ```bash
   python example_advanced.py
   ```

5. **Test with your videos:**
   - Place videos in `videos/`
   - Process and analyze results

## System Requirements

**Minimum:**
- CPU: Intel i5 or equivalent
- RAM: 4GB
- Storage: 2GB free
- GPU: None (CPU mode works)

**Recommended:**
- CPU: Intel i7 or equivalent
- RAM: 8GB+
- Storage: 10GB free (for videos)
- GPU: NVIDIA with 4GB+ VRAM

**For Real-Time (30fps+):**
- GPU: NVIDIA RTX series
- VRAM: 6GB+
- CUDA: 11.8 or 12.1

## Update Instructions

To update dependencies:

```bash
pip install --upgrade ultralytics torch torchvision opencv-python
```

To switch YOLO model:

```python
# In config.py
YOLO_MODEL = "yolov8s.pt"  # Will auto-download on first use
```

Available models:
- `yolov8n.pt` - Nano (fastest, least accurate)
- `yolov8s.pt` - Small (balanced)
- `yolov8m.pt` - Medium (more accurate)
- `yolov8l.pt` - Large (very accurate)
- `yolov8x.pt` - Extra-large (most accurate, slowest)

## Support

If issues persist:

1. Check Python version (3.9+)
2. Update all packages: `pip install --upgrade -r requirements.txt`
3. Try in fresh virtual environment
4. Check GPU drivers (if using CUDA)
5. Test with simpler video (720p, 30fps)

For bug reports, include:
- Python version
- OS version
- Error message
- Contents of `requirements.txt`
