#!/usr/bin/env python3
"""
Script to compress large images in the static/images directory.
Reduces file size while maintaining good quality for web use.
"""
import os
from PIL import Image
from pathlib import Path

# Target max file size (in KB)
MAX_SIZE_KB = 500  # 500KB for most images
MAX_SIZE_KB_LARGE = 1000  # 1MB for hero/banner images

# Images directory
IMAGES_DIR = Path(__file__).parent / 'static' / 'images' / 'general'

# Large banner images that can be slightly larger
BANNER_IMAGES = [
    'access hour banner.jpg',
    'event and gathering.jpg',
    'daily prayer.jpg',
    'uplift your morning banner.jpg',
    'Screenshot 2025-12-03 at 15.20.14.png'
]

def compress_image(image_path, max_size_kb=MAX_SIZE_KB, quality=85, max_dimension=1920):
    """Compress an image to reduce file size."""
    try:
        img = Image.open(image_path)
        original_size = os.path.getsize(image_path) / 1024  # KB
        
        # If already small enough, skip
        if original_size <= max_size_kb:
            print(f"✓ {image_path.name} ({original_size:.1f}KB) - already optimized")
            return False
        
        # Resize if image is too large (maintain aspect ratio)
        width, height = img.size
        if width > max_dimension or height > max_dimension:
            if width > height:
                new_width = max_dimension
                new_height = int(height * (max_dimension / width))
            else:
                new_height = max_dimension
                new_width = int(width * (max_dimension / height))
            img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            print(f"  Resized from {width}x{height} to {new_width}x{new_height}")
        
        # Convert RGBA to RGB if necessary (for JPEG)
        if img.mode in ('RGBA', 'LA', 'P'):
            background = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'P':
                img = img.convert('RGBA')
            background.paste(img, mask=img.split()[-1] if img.mode in ('RGBA', 'LA') else None)
            img = background
        
        # Try different quality levels if still too large
        current_quality = quality
        output_path = image_path
        
        while current_quality >= 60:
            img.save(
                output_path,
                'JPEG' if image_path.suffix.lower() in ['.jpg', '.jpeg'] else 'PNG',
                optimize=True,
                quality=current_quality
            )
            new_size = os.path.getsize(output_path) / 1024  # KB
            if new_size <= max_size_kb or current_quality <= 60:
                break
            current_quality -= 5
        
        new_size = os.path.getsize(output_path) / 1024  # KB
        reduction = ((original_size - new_size) / original_size) * 100
        
        print(f"✓ {image_path.name}: {original_size:.1f}KB → {new_size:.1f}KB ({reduction:.1f}% reduction, quality: {current_quality})")
        return True
        
    except Exception as e:
        print(f"✗ Error compressing {image_path.name}: {e}")
        return False

def main():
    """Main function to compress all large images."""
    print("Starting image compression...\n")
    
    compressed_count = 0
    
    # Process banner images (can be slightly larger, but resize if needed)
    for banner_name in BANNER_IMAGES:
        banner_path = IMAGES_DIR / banner_name
        if banner_path.exists():
            if compress_image(banner_path, max_size_kb=MAX_SIZE_KB_LARGE, quality=75, max_dimension=1920):
                compressed_count += 1
        else:
            print(f"⚠ Banner image not found: {banner_name}")
    
    # Process other large images
    for image_file in IMAGES_DIR.glob('*.jpg'):
        if image_file.name not in BANNER_IMAGES:
            if compress_image(image_file, max_size_kb=MAX_SIZE_KB, quality=85, max_dimension=1920):
                compressed_count += 1
    
    for image_file in IMAGES_DIR.glob('*.JPG'):
        if compress_image(image_file, max_size_kb=MAX_SIZE_KB, quality=85, max_dimension=1920):
            compressed_count += 1
    
    for image_file in IMAGES_DIR.glob('*.png'):
        if image_file.name not in BANNER_IMAGES:
            if compress_image(image_file, max_size_kb=MAX_SIZE_KB, quality=85, max_dimension=1920):
                compressed_count += 1
    
    print(f"\n✓ Compression complete! {compressed_count} images compressed.")
    print("\nNote: Original images have been replaced with compressed versions.")
    print("If you need originals, restore them from git or backup first.")

if __name__ == '__main__':
    main()
