"""
Advanced Usage Examples
Shows how to use predefined zones, batch processing, and custom configurations
"""

import os
from safety_interlock import VideoProcessor, ZoneManager
from safety_interlock import config


def example_predefined_zone():
    """Example: Process video with predefined zone coordinates"""
    print("\n=== Example 1: Predefined Zone ===\n")

    # Define zone coordinates (from Image 3 layout)
    # Adjust these coordinates based on your actual camera view
    zone_coords = [
        (100, 200),   # top-left
        (1800, 200),  # top-right
        (1800, 900),  # bottom-right
        (100, 900)    # bottom-left
    ]

    video_path = "videos/test_video.mp4"

    if not os.path.exists(video_path):
        print(f"⚠️  Video not found: {video_path}")
        return

    # Initialize processor with predefined zone
    processor = VideoProcessor(video_path, zone_coords=zone_coords)

    # Process (no interactive zone definition needed)
    processor.process()

    print("\n✅ Processing complete with predefined zone")


def example_custom_config():
    """Example: Process with custom configuration"""
    print("\n=== Example 2: Custom Configuration ===\n")

    # Temporarily modify config
    original_confidence = config.CONFIDENCE_THRESHOLD
    original_danger = config.DANGER_THRESHOLD

    # More sensitive detection
    config.CONFIDENCE_THRESHOLD = 0.6  # Lower confidence OK
    config.DANGER_THRESHOLD = 0.4      # Trigger at 40% overlap

    video_path = "videos/test_video.mp4"

    if not os.path.exists(video_path):
        print(f"⚠️  Video not found: {video_path}")
        return

    try:
        processor = VideoProcessor(video_path)
        processor.define_zone()
        processor.process()

    finally:
        # Restore original config
        config.CONFIDENCE_THRESHOLD = original_confidence
        config.DANGER_THRESHOLD = original_danger

    print("\n✅ Processing complete with custom config")


def example_batch_processing():
    """Example: Process multiple videos"""
    print("\n=== Example 3: Batch Processing ===\n")

    video_dir = "videos"
    video_files = [f for f in os.listdir(video_dir) if f.endswith(('.mp4', '.avi', '.mov'))]

    if not video_files:
        print("⚠️  No videos found in videos/ directory")
        return

    # Use same zone for all videos (adjust as needed)
    zone_coords = [
        (100, 200),
        (1800, 200),
        (1800, 900),
        (100, 900)
    ]

    results = []

    for video_file in video_files:
        video_path = os.path.join(video_dir, video_file)
        print(f"\n📹 Processing: {video_file}")

        try:
            processor = VideoProcessor(video_path, zone_coords=zone_coords)
            processor.process()

            # Collect statistics
            stats = processor.get_statistics()
            results.append({
                'video': video_file,
                'triggers': stats['trigger_count'],
                'danger_time': stats['total_danger_time']
            })

        except Exception as e:
            print(f"❌ Error processing {video_file}: {e}")
            continue

    # Summary report
    print("\n" + "=" * 70)
    print("BATCH PROCESSING SUMMARY")
    print("=" * 70)
    for result in results:
        print(f"{result['video']}: {result['triggers']} triggers, {result['danger_time']:.2f}s danger time")
    print("=" * 70)


def example_load_saved_zone():
    """Example: Load previously saved zone"""
    print("\n=== Example 4: Load Saved Zone ===\n")

    zone_file = "output/zone_definition.json"

    if not os.path.exists(zone_file):
        print(f"⚠️  No saved zone found: {zone_file}")
        print("   Run main.py first to create a zone interactively")
        return

    # Load zone
    zone_manager = ZoneManager()
    zone_manager.load_zone(zone_file)

    print(f"✅ Loaded zone with {len(zone_manager.zone_coords)} points")
    print(f"   Area: {zone_manager.zone_polygon.area:.0f} pixels²")

    # Use with processor
    video_path = "videos/test_video.mp4"

    if os.path.exists(video_path):
        processor = VideoProcessor(video_path, zone_coords=zone_manager.zone_coords)
        processor.process()


def example_zone_comparison():
    """Example: Test multiple zone configurations"""
    print("\n=== Example 5: Zone Comparison ===\n")

    video_path = "videos/test_video.mp4"

    if not os.path.exists(video_path):
        print(f"⚠️  Video not found: {video_path}")
        return

    # Define different zone sizes
    zones = {
        'tight': [(400, 300), (1520, 300), (1520, 800), (400, 800)],
        'medium': [(200, 200), (1720, 200), (1720, 900), (200, 900)],
        'wide': [(50, 100), (1870, 100), (1870, 980), (50, 980)]
    }

    results = {}

    for zone_name, zone_coords in zones.items():
        print(f"\n🔍 Testing zone: {zone_name}")

        processor = VideoProcessor(video_path, zone_coords=zone_coords)
        processor.process()

        stats = processor.get_statistics()
        results[zone_name] = {
            'triggers': stats['trigger_count'],
            'danger_time': stats['total_danger_time']
        }

    # Compare results
    print("\n" + "=" * 70)
    print("ZONE COMPARISON")
    print("=" * 70)
    for zone_name, result in results.items():
        print(f"{zone_name:10s}: {result['triggers']} triggers, {result['danger_time']:.2f}s danger time")
    print("=" * 70)


if __name__ == "__main__":
    print("=" * 70)
    print("SAFETY INTERLOCK SYSTEM - ADVANCED EXAMPLES")
    print("=" * 70)

    # Choose which example to run
    print("\nAvailable examples:")
    print("1. Predefined zone")
    print("2. Custom configuration")
    print("3. Batch processing")
    print("4. Load saved zone")
    print("5. Zone comparison")
    print("0. Run all examples")

    try:
        choice = input("\nSelect example (0-5): ").strip()

        if choice == "1":
            example_predefined_zone()
        elif choice == "2":
            example_custom_config()
        elif choice == "3":
            example_batch_processing()
        elif choice == "4":
            example_load_saved_zone()
        elif choice == "5":
            example_zone_comparison()
        elif choice == "0":
            example_predefined_zone()
            example_custom_config()
            example_batch_processing()
            example_load_saved_zone()
            example_zone_comparison()
        else:
            print("❌ Invalid choice")

    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
