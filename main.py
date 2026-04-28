"""
Safety Interlock System - Main Entry Point
AI-based human detection for robotic cell safety

Usage:
    python main.py <video_path> [--redefine-zone]

Example:
    python main.py videos/test_video.mp4
    python main.py videos/test_video.mp4 --redefine-zone

Options:
    --redefine-zone    Force redefine zone (ignore saved zone)
"""

import sys
import os
from safety_interlock import VideoProcessor


def main():
    """Main entry point"""
    print("=" * 70)
    print("SAFETY INTERLOCK SYSTEM v1.0")
    print("AI-Based Human Detection for Robotic Cell Safety")
    print("=" * 70)

    # Check arguments
    if len(sys.argv) < 2:
        print("\n❌ Error: No video file specified")
        print("\nUsage:")
        print("  python main.py <video_path> [--redefine-zone]")
        print("\nExample:")
        print("  python main.py videos/test_video.mp4")
        print("  python main.py videos/test_video.mp4 --redefine-zone")
        print("\nOptions:")
        print("  --redefine-zone    Force redefine zone (ignore saved zone)")
        sys.exit(1)

    video_path = sys.argv[1]
    redefine_zone = '--redefine-zone' in sys.argv

    # Check if file exists
    if not os.path.exists(video_path):
        print(f"\n❌ Error: Video file not found: {video_path}")
        sys.exit(1)

    try:
        # Initialize processor
        processor = VideoProcessor(video_path)

        # Define danger zone
        processor.define_zone(force_redefine=redefine_zone)

        # Process video
        processor.process()

        # Show statistics
        stats = processor.get_statistics()
        print("\n📊 QUICK STATS:")
        print(f"   Total triggers: {stats['trigger_count']}")
        print(f"   Danger time: {stats['total_danger_time']:.2f}s")

    except KeyboardInterrupt:
        print("\n\n⚠️  Processing interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
