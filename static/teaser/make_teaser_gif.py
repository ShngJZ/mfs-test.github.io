#!/usr/bin/env python3
"""
GIF Teaser Maker
Converts a ScanNet video to a teaser GIF with banner overlays.

The script:
1. Reads a video with RGB, depth, and pointcloud visualizations
2. For each frame, splits into RGB/depth/pointcloud components
3. Resizes banner images (Block.png, Left_banner.png, Right_banner.png)
4. Reorders components as: RGB, depth, Block, pointcloud
5. Overlays Left_banner on RGB and Right_banner on pointcloud
6. Saves as teaser.gif
"""

from PIL import Image
import numpy as np
from pathlib import Path
from moviepy import VideoFileClip

# Configuration
INPUT_VIDEO = "../videos/scannet/scene0733_00.mp4"
BLOCK_IMAGE = "Block.png"
LEFT_BANNER = "Left_banner.png"
RIGHT_BANNER = "Right_banner.png"
OUTPUT_GIF = "teaser.gif"

# Video parameters
DURATION = 12  # seconds (30 frames at 5 FPS)
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
    # When height is scaled to target, width scales proportionally
    rgb_depth_width = int(frame_height * (SCANNET_WIDTH / SCANNET_HEIGHT))
    
    # Split: RGB | depth | pointcloud (with 1-pixel bias)
    rgb = frame_array[:, :rgb_depth_width, :]
    depth = frame_array[:, rgb_depth_width+1:rgb_depth_width*2+1, :]
    pointcloud = frame_array[:, rgb_depth_width*2+2:, :]
    
    return rgb, depth, pointcloud

def resize_banner_images(target_height, script_dir):
    """
    Resize banner images using the SAME ratio.
    Ratio is determined by Block.png matching target height.
    """
    block = Image.open(script_dir / BLOCK_IMAGE).convert('RGBA')
    left_banner = Image.open(script_dir / LEFT_BANNER).convert('RGBA')
    right_banner = Image.open(script_dir / RIGHT_BANNER).convert('RGBA')
    
    # Calculate resize ratio based on Block.png
    resize_ratio = target_height / block.size[1]
    
    # Apply the SAME ratio to all three images
    block_resized = block.resize(
        (int(block.size[0] * resize_ratio), int(block.size[1] * resize_ratio)),
        Image.Resampling.LANCZOS
    )
    left_banner_resized = left_banner.resize(
        (int(left_banner.size[0] * resize_ratio), int(left_banner.size[1] * resize_ratio)),
        Image.Resampling.LANCZOS
    )
    right_banner_resized = right_banner.resize(
        (int(right_banner.size[0] * resize_ratio), int(right_banner.size[1] * resize_ratio)),
        Image.Resampling.LANCZOS
    )
    
    return block_resized, left_banner_resized, right_banner_resized

def overlay_banner(base_array, banner_image):
    """
    Overlay banner on base image at top-left corner.
    base_array: numpy array (H, W, C)
    banner_image: PIL Image
    """
    # Convert base to PIL Image
    base_img = Image.fromarray(base_array)
    
    # Convert banner to RGB
    banner_rgb = Image.new('RGB', banner_image.size, (255, 255, 255))
    if banner_image.mode == 'RGBA':
        banner_rgb.paste(banner_image, (0, 0), banner_image)
    else:
        banner_rgb = banner_image.convert('RGB')
    
    # Crop if needed
    banner_width, banner_height = banner_rgb.size
    base_width, base_height = base_img.size
    if banner_width > base_width or banner_height > base_height:
        banner_rgb = banner_rgb.crop((0, 0, min(banner_width, base_width), min(banner_height, base_height)))
    
    # Paste banner at x=1 (1 pixel from left edge)
    base_img.paste(banner_rgb, (1, 0))
    
    return np.array(base_img)

def process_frame(frame, block_resized, left_banner_resized, right_banner_resized):
    """
    Process a single frame.
    frame: numpy array from moviepy (H, W, C)
    Returns: numpy array
    """
    # Split frame
    rgb, depth, pointcloud = split_frame_horizontal(frame)
    
    # Overlay banners
    rgb_with_banner = overlay_banner(rgb, left_banner_resized)
    pointcloud_with_banner = overlay_banner(pointcloud, right_banner_resized)
    
    # Convert block to RGB array
    block_rgb = Image.new('RGB', block_resized.size, (255, 255, 255))
    if block_resized.mode == 'RGBA':
        block_rgb.paste(block_resized, (0, 0), block_resized)
    else:
        block_rgb = block_resized.convert('RGB')
    block_array = np.array(block_rgb)
    
    # Concatenate horizontally: RGB, depth, Block, pointcloud
    result = np.concatenate([rgb_with_banner, depth, block_array, pointcloud_with_banner], axis=1)
    
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
    
    # Get frame height
    first_frame = resized.get_frame(0)
    frame_height = first_frame.shape[0]
    
    # Resize banner images
    block_resized, left_banner_resized, right_banner_resized = resize_banner_images(frame_height, script_dir)
    
    # Process frames
    def frame_function(t):
        frame = resized.get_frame(t)
        return process_frame(frame, block_resized, left_banner_resized, right_banner_resized)
    
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
