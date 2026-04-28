"""
Run Safety Interlock System with backend server
Starts Flask server in background thread before processing video
"""

import sys
import os
import threading
from safety_interlock import VideoProcessor
import backend_server

def start_server():
    """Start Flask server in background"""
    backend_server.app.run(host='0.0.0.0', port=5000, debug=False, threaded=True, use_reloader=False)

def main():
    """Main entry point"""
    print("=" * 70)
    print("SAFETY INTERLOCK SYSTEM v1.0 - WITH WEB INTERFACE")
    print("=" * 70)

    if len(sys.argv) < 2:
        print("\n❌ Error: No video file specified")
        print("\nUsage:")
        print("  python run_with_server.py <video_path> [--redefine-zone]")
        print("\nExample:")
        print("  python run_with_server.py videos/test_video.mp4")
        sys.exit(1)

    video_path = sys.argv[1]
    redefine_zone = '--redefine-zone' in sys.argv

    if not os.path.exists(video_path):
        print(f"\n❌ Error: Video file not found: {video_path}")
        sys.exit(1)

    print("\n🌐 Starting backend server...")
    backend_server.load_incidents()
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()

    print("✅ Backend server running at http://localhost:5000")
    print("   Stream: http://localhost:5000/api/stream")
    print("   Incidents API: http://localhost:5000/api/incidents\n")

    try:
        processor = VideoProcessor(video_path)
        processor.define_zone(force_redefine=redefine_zone)
        processor.process()

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
