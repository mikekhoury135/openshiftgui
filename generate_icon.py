#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Simple script to generate a basic icon for the application
This creates a simple colored square icon if no icon exists
"""

import os
from PIL import Image, ImageDraw

def generate_basic_icon():
    """Generate a basic icon if none exists"""
    icon_path = os.path.join('app', 'resources', 'icon.ico')
    
    # Check if icon already exists
    if os.path.exists(icon_path):
        print(f"Icon already exists at {icon_path}")
        return
    
    # Create directories if they don't exist
    os.makedirs(os.path.dirname(icon_path), exist_ok=True)
    
    # Create a simple 256x256 icon
    icon_size = 256
    img = Image.new('RGBA', (icon_size, icon_size), color=(0, 0, 0, 0))
    
    # Create a drawing context
    draw = ImageDraw.Draw(img)
    
    # Draw a square with a blue color (typical for dev/admin tools)
    draw.rectangle([(10, 10), (icon_size-10, icon_size-10)], fill=(24, 102, 180))
    
    # Draw some lines to make it look like a dashboard/console
    for i in range(30, icon_size-30, 40):
        draw.line([(30, i), (icon_size-30, i)], fill=(255, 255, 255), width=4)
    
    # Save the image as ICO
    try:
        img.save(icon_path)
        print(f"Generated basic icon at {icon_path}")
    except Exception as e:
        print(f"Failed to generate icon: {e}")
        # Create an empty file to prevent future failures
        with open(icon_path, 'wb') as f:
            pass
        print(f"Created empty icon file at {icon_path}")

if __name__ == "__main__":
    generate_basic_icon()