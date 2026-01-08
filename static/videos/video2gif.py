#!/usr/bin/env python3
"""
Video to GIF Converter
Converts the first N seconds of all videos to GIF format.
"""

import os
from pathlib import Path
from moviepy import VideoFileClip

# Configuration
DURATION = 3  # Number of seconds to convert
FPS = 10      # Frames per second for GIF
HEIGHT = 640  # Height in pixels (width will be calculated to maintain aspect ratio)
INPUT_DIR = "."  # Current directory (static/videos)
OUTPUT_DIR = "../gifs"  # Output to static/gifs

def ensure_dir(directory):
    """Create directory if it doesn't exist."""
    Path(directory).mkdir(parents=True, exist_ok=True)

def convert_video_to_gif(video_path, gif_path, duration=DURATION, fps=FPS, height=HEIGHT):
    """Convert video to GIF."""
    print(f"Converting: {video_path.name}")
    
    # Load video clip
    clip = VideoFileClip(str(video_path))
    
    # Get the actual duration and use minimum of requested and actual
    actual_duration = min(duration, clip.duration)
    
    # Extract first N seconds
    subclip = clip.subclipped(0, actual_duration)
    
    # Resize to specified height (maintaining aspect ratio)
    resized = subclip.resized(height=height)
    
    # Write GIF file with optimization
    resized.write_gif(str(gif_path), fps=fps)
    
    # Clean up
    resized.close()
    subclip.close()
    clip.close()

def find_videos(directory):
    """Find all video files recursively."""
    video_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.webm']
    video_files = []
    
    for root, dirs, files in os.walk(directory):
        for file in files:
            if any(file.lower().endswith(ext) for ext in video_extensions):
                video_files.append(Path(root) / file)
    
    return video_files

def main():
    """Main function."""
    print(f"Duration: {DURATION}s, FPS: {FPS}")
    
    # Get paths
    script_dir = Path(__file__).parent
    input_path = script_dir / INPUT_DIR
    output_path = script_dir / OUTPUT_DIR
    
    # Ensure output directory exists
    ensure_dir(output_path)
    
    # Find all video files
    video_files = find_videos(input_path)
    print(f"\nFound {len(video_files)} video files\n")
    
    # Process each video
    for i, video_path in enumerate(video_files, 1):
        # Calculate relative path
        rel_path = video_path.relative_to(input_path)
        
        # Create output path with .gif extension
        gif_rel_path = rel_path.with_suffix('.gif')
        gif_path = output_path / gif_rel_path
        
        # Ensure output subdirectory exists
        ensure_dir(gif_path.parent)
        
        # Convert
        print(f"[{i}/{len(video_files)}] ", end="")
        convert_video_to_gif(video_path, gif_path)
    
    print(f"\nDone! Converted {len(video_files)} videos")

if __name__ == "__main__":
    main()
