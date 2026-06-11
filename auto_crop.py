import os
import sys
import glob
import re
from PIL import Image

# Configuration
# Targets both recovered pattern files (e.g., _NHL0591-_NHL0592.JPG)
FILE_PATTERN = "*-*.JPG" 
# How many pixels wide to sample when checking for solid gray blocks
SAMPLE_WIDTH = 200 


def find_corrupt_bottom_row(img: Image.Image) -> int:
    """
    Scans the image from the bottom upwards to find the first line 
    that contains actual image color/detail instead of solid gray/black filler.
    """
    width, height = img.size
    pix = img.load()
    
    # Define a central sampling bounding area to avoid edge vignetting/shadows
    start_x = max(0, (width // 2) - (SAMPLE_WIDTH // 2))
    end_x = min(width, start_x + SAMPLE_WIDTH)

    # Scan from the very last row upwards
    for y in range(height - 1, -1, -1):
        first_pixel = pix[start_x, y]
        
        # JPEGs use YCbCr filler color blocks, check if pixels in this row match 
        # within a tight threshold tolerance (indicating a solid uniform bar)
        is_solid_row = True
        for x in range(start_x + 1, end_x):
            current_pixel = pix[x, y]
            
            # Compare RGB differences
            diff = sum(abs(a - b) for a, b in zip(first_pixel, current_pixel))
            if diff > 15: # Threshold for variance (higher means looser match)
                is_solid_row = False
                break
                
        # The moment we find a row that is NOT solid gray/filler, 
        # we have hit the real image data boundary.
        if not is_solid_row:
            return y + 1
            
    return height


def main():
    # Grab files in the current working directory matching the pattern
    files = glob.glob(FILE_PATTERN)
    if not files:
        print(f"No files found matching pattern '{FILE_PATTERN}' in the current folder.")
        return

    print(f"Found {len(files)} recovered images to process...\n")

    for file_path in files:
        base_name = os.path.basename(file_path)
        print(f"Processing: {base_name}")
        
        try:
            with Image.open(file_path) as img:
                # Convert to RGB to safely inspect raw pixel arrays
                rgb_img = img.convert("RGB")
                
                # Detect the real data height
                clean_height = find_corrupt_bottom_row(rgb_img)
                
                if clean_height < img.height:
                    crop_amount = img.height - clean_height
                    print(f"-> Found corrupt scanline blocks. Cropping {crop_amount}px from bottom.")
                    
                    # Crop dimensions: (left, top, right, bottom)
                    cropped_img = img.crop((0, 0, img.width, clean_height))
                    
                    # Generate clean filename output
                    name, ext = os.path.splitext(file_path)
                    output_name = f"{name}-cropped{ext}"
                    
                    # Save back with identical max quality settings
                    cropped_img.save(output_name, "JPEG", quality=100, subsampling=0)
                    print(f"-> Saved clean image: {os.path.basename(output_name)}\n")
                else:
                    print("-> Image appears clean. No non-color filler detected at the bottom.\n")
                    
        except Exception as e:
            print(f"-> Error processing file: {e}\n")

    input("Processing complete. Press enter to exit...")


if __name__ == "__main__":
    main()
