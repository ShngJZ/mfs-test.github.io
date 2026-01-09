#!/usr/bin/env python3
"""
Vertical GIF Teaser Maker
Converts a ScanNet video to a vertical teaser GIF without banner overlays.

The script:
1. Reads a video with RGB, depth, and pointcloud visualizations
2. For each frame, splits into RGB/depth/pointcloud components
3. Resizes pointcloud to match RGB/depth width (keeping aspect ratio)
4. Stacks components vertically: RGB → depth → pointcloud
5. Saves as teaser_vertical.gif
"""

from PIL import Image
import numpy as np
from pathlib import Path
from moviepy import VideoFileClip

# Configuration
INPUT_VIDEO = "../videos/scannet/scene0733_00.mp4"
OUTPUT_GIF = "teaser_vertical.gif"

# Video parameters
DURATION = 6  # seconds (30 frames at 5 FPS)
FPS = 5
HEIGHT = 320  # target height

# Original ScanNet RGB resolution
SCANNET_WIDTH = 640
SCANNET_HEIGHT = 480

def split_frame_horizontal(frame_array):
    """
    Split frame into RGB, depth, and pointcloud.
    RGB and depth have same resolution (640x480 aspect ratio).
    Pointcloud has different resolution (remaining width).
    frame_array: numpy array (H, W, C)
    """
    frame_height = frame_array.shape[0]
    frame_width = frame_array.shape[1]
    
    # Calculate RGB/depth width based on 640x480 aspect ratio
    rgb_depth_width = int(frame_height * (SCANNET_WIDTH / SCANNET_HEIGHT))
    
    # Split: RGB | depth | pointcloud (with 1-pixel bias)
    rgb = frame_array[:, :rgb_depth_width, :]
    depth = frame_array[:, rgb_depth_width+1:rgb_depth_width*2+1, :]
    pointcloud = frame_array[:, rgb_depth_width*2+2:, :]
    
    return rgb, depth, pointcloud

def resize_pointcloud_to_width(pointcloud_array, target_width):
    """
    Resize pointcloud to match target width while maintaining aspect ratio.
    pointcloud_array: numpy array (H, W, C)
    target_width: desired width
    Returns: resized numpy array
    """
    pc_img = Image.fromarray(pointcloud_array)
    original_width, original_height = pc_img.size
    
    # Calculate new height to maintain aspect ratio
    aspect_ratio = original_height / original_width
    new_height = int(target_width * aspect_ratio)
    
    # Resize
    resized_pc = pc_img.resize((target_width, new_height), Image.Resampling.LANCZOS)
    
    return np.array(resized_pc)

def process_frame_vertical(frame):
    """
    Process a single frame for vertical stacking.
    frame: numpy array from moviepy (H, W, C)
    Returns: numpy array with vertical stack
    """
    # Split frame
    rgb, depth, pointcloud = split_frame_horizontal(frame)
    
    # Get RGB/depth width
    rgb_width = rgb.shape[1]
    
    # Resize pointcloud to match RGB/depth width
    pointcloud_resized = resize_pointcloud_to_width(pointcloud, rgb_width)
    
    # Stack vertically: RGB, depth, pointcloud
    result = np.concatenate([rgb, depth, pointcloud_resized], axis=0)
    
    return result

def main():
    """Main function."""
    script_dir = Path(__file__).parent
    input_path = script_dir / INPUT_VIDEO
    output_path = script_dir / OUTPUT_GIF
    
    # Load video
    clip = VideoFileClip(str(input_path))
    
    # Limit to first 6 seconds (30 frames at 5 FPS)
    actual_duration = min(DURATION, clip.duration)
    
    # Extract subclip
    subclip = clip.subclipped(0, actual_duration)
    
    # Resize to target height
    resized = subclip.resized(height=HEIGHT)
    
    # Process frames
    def frame_function(t):
        frame = resized.get_frame(t)
        return process_frame_vertical(frame)
    
    # Create processed clip
    from moviepy import VideoClip
    processed_clip = VideoClip(frame_function, duration=actual_duration)
    
    # Write GIF
    processed_clip.write_gif(str(output_path), fps=FPS)
    
    # Cleanup
    processed_clip.close()
    resized.close()
    subclip.close()
    clip.close()
    
    print(f"Done: {output_path}")

if __name__ == "__main__":
    main()
