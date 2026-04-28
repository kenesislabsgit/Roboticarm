# Zone Management Guide

How zone coordinates work and how to manage them.

---

## Automatic Zone Saving

**First run:**
```bash
python main.py videos/video_1.mp4
```

1. System checks for `output/zone_definition.json`
2. Not found → Opens interactive zone definition window
3. You click 4+ points to define zone
4. Press ENTER
5. Zone saved to `output/zone_definition.json`
6. Processing starts

**Second run (same or different video):**
```bash
python main.py videos/video_2.mp4
```

1. System checks for `output/zone_definition.json`
2. Found! → Automatically loads saved zone
3. **No interactive window** - uses saved coordinates
4. Processing starts immediately

**Result:** Only define zone once, reuse forever.

---

## Force Redefine Zone

If camera moved or want different zone:

```bash
python main.py videos/video_1.mp4 --redefine-zone
```

**What happens:**
1. Ignores existing `zone_definition.json`
2. Opens interactive window
3. Define new zone
4. Overwrites old saved zone
5. Future runs use new zone

---

## Zone File Location

**File:** `output/zone_definition.json`

**Format:**
```json
{
  "zone_coords": [
    [195, 366],   // Point 1 (x, y)
    [554, 713],   // Point 2
    [1093, 366],  // Point 3
    [719, 199]    // Point 4
  ],
  "area": 230786.0  // Zone area in pixels²
}
```

**Can edit manually** if needed (advanced users).

---

## Use Cases

### Same Camera, Multiple Videos

Camera fixed, processing many videos:

```bash
# First video - define zone
python main.py videos/day1.mp4

# All future videos - auto-loads zone
python main.py videos/day2.mp4
python main.py videos/day3.mp4
python main.py videos/day4.mp4
```

No redefinition needed. ✅

### Different Cameras or Angles

Different camera setups need different zones:

**Option 1: Multiple zone files**

```bash
# Camera 1
python main.py videos/cam1_video.mp4
mv output/zone_definition.json output/zone_cam1.json

# Camera 2
python main.py videos/cam2_video.mp4 --redefine-zone
mv output/zone_definition.json output/zone_cam2.json

# Use specific zone
cp output/zone_cam1.json output/zone_definition.json
python main.py videos/cam1_another.mp4
```

**Option 2: Redefine each time**

```bash
python main.py videos/cam1_video.mp4 --redefine-zone
python main.py videos/cam2_video.mp4 --redefine-zone
```

### Camera Position Changed

Camera moved or angle adjusted:

```bash
# Redefine zone for new position
python main.py videos/new_angle.mp4 --redefine-zone
```

---

## Manual Zone Management

### View Current Zone

```bash
cat output/zone_definition.json
```

### Backup Zone

```bash
cp output/zone_definition.json output/zone_backup_2026-04-13.json
```

### Restore Zone

```bash
cp output/zone_backup_2026-04-13.json output/zone_definition.json
```

### Delete Zone (force redefine next run)

```bash
rm output/zone_definition.json
# Next run will ask for zone definition
python main.py videos/video.mp4
```

---

## Programmatic Usage

### With Saved Zone

```python
from safety_interlock import VideoProcessor

# Auto-loads from output/zone_definition.json if exists
processor = VideoProcessor("videos/test.mp4")
processor.define_zone()  # Loads saved or asks for new
processor.process()
```

### With Hardcoded Zone

```python
from safety_interlock import VideoProcessor

# Define zone in code (no interactive, no saved file needed)
zone_coords = [
    (100, 200),
    (1800, 200),
    (1800, 900),
    (100, 900)
]

processor = VideoProcessor("videos/test.mp4", zone_coords=zone_coords)
processor.define_zone()  # Uses provided coords
processor.process()
```

### Force Redefine

```python
processor = VideoProcessor("videos/test.mp4")
processor.define_zone(force_redefine=True)  # Ignores saved zone
processor.process()
```

### Load Specific Zone File

```python
from safety_interlock import ZoneManager

zone_mgr = ZoneManager()
zone_mgr.load_zone("output/zone_cam1.json")

processor = VideoProcessor("videos/test.mp4", zone_coords=zone_mgr.zone_coords)
processor.process()
```

---

## Zone Definition Tips

### Accurate Boundary Clicking

1. **Start at a corner** (e.g., top-left of fence)
2. **Click clockwise** around boundary
3. **Stay on boundary line** (not inside/outside)
4. **Close the loop** - last point near first point
5. **Minimum 4 points** for rectangle
6. **Use more points** for complex shapes

### Margin for Safety

Click **slightly outside** actual danger zone:
- Gives early warning
- Accounts for detection lag
- Better safe than sorry

### Test Your Zone

After defining:
```bash
# Check annotated video
# Verify zone boundary correct
ls output/annotated_*.mp4
```

Zone drawn as cyan polygon on video.

---

## Troubleshooting

### "Zone definition cancelled" error

**Cause:** Pressed 'q' (quit) instead of ENTER

**Fix:**
```bash
# Run again, press ENTER after clicking points
python main.py videos/video.mp4
```

### Zone wrong for current video

**Cause:** Saved zone from different camera angle

**Fix:**
```bash
# Redefine zone
python main.py videos/video.mp4 --redefine-zone
```

### Can't load saved zone

**Error:** `Could not load saved zone`

**Possible causes:**
- File corrupted
- Wrong JSON format
- File permissions

**Fix:**
```bash
# Delete and redefine
rm output/zone_definition.json
python main.py videos/video.mp4
```

### Zone too small/large

**Fix:**
```bash
# Redefine with correct size
python main.py videos/video.mp4 --redefine-zone
```

---

## Best Practices

### For Single Camera Setup

1. ✅ Define zone once with first video
2. ✅ Save zone file (automatic)
3. ✅ Process all future videos (auto-loads)
4. ✅ Only redefine if camera moves

### For Multiple Camera Setup

1. ✅ Define zone for each camera
2. ✅ Save with descriptive names:
   - `zone_cam1_front.json`
   - `zone_cam2_overhead.json`
3. ✅ Copy correct zone before processing:
   ```bash
   cp zones/zone_cam1.json output/zone_definition.json
   python main.py videos/cam1_video.mp4
   ```

### For Production

1. ✅ Define zone carefully (test with person walking boundary)
2. ✅ Backup zone file (version control)
3. ✅ Document which zone for which camera
4. ✅ Verify zone loaded correctly (check console output)
5. ✅ Review annotated video to confirm zone position

---

## Quick Reference

| Command | What It Does |
|---------|--------------|
| `python main.py video.mp4` | Use saved zone or define if not exists |
| `python main.py video.mp4 --redefine-zone` | Force redefine, ignore saved |
| `cat output/zone_definition.json` | View saved zone |
| `rm output/zone_definition.json` | Delete saved zone |
| `cp zone1.json output/zone_definition.json` | Use specific zone |

**Zone file:** `output/zone_definition.json`

**Loaded automatically:** ✅ Yes (if exists)

**Reused across videos:** ✅ Yes

**One-time definition:** ✅ Yes (unless --redefine-zone)

---

## Summary

**How it works:**

1. **First run:** Define zone → Saved to `zone_definition.json`
2. **Future runs:** Auto-loads saved zone
3. **To redefine:** Use `--redefine-zone` flag

**Benefits:**

- ✅ Define once, use forever
- ✅ No repetitive clicking
- ✅ Consistent zone across videos
- ✅ Fast processing (no interactive wait)
- ✅ Can force redefine if needed

**Default behavior:** Smart - asks once, remembers forever.

---

**Questions?** Check `README.md` or `QUICKSTART.md`
