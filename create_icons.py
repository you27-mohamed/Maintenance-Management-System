#!/usr/bin/env python3
"""
Generate simple icon files for PWA
"""
from PIL import Image, ImageDraw, ImageFont
import os

def create_icon(size, filename):
    # Create a new image with a blue background
    img = Image.new('RGB', (size, size), color='#667eea')
    draw = ImageDraw.Draw(img)
    
    # Draw a circle in the center
    margin = size // 8
    draw.ellipse([margin, margin, size-margin, size-margin], 
                 fill='white', outline='#4CAF50', width=size//40)
    
    # Try to add text (maintenance in Arabic)
    try:
        # Use default font for simplicity
        font_size = size // 6
        font = ImageFont.load_default()
        text = "صيانة"
        
        # Get text size and center it
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        x = (size - text_width) // 2
        y = (size - text_height) // 2
        
        draw.text((x, y), text, fill='#333333', font=font)
    except:
        # If text fails, just draw a gear-like shape
        center = size // 2
        for angle in range(0, 360, 45):
            x1 = center + (size//6) * (1 if angle % 90 == 0 else 0.7) * cos(radians(angle))
            y1 = center + (size//6) * (1 if angle % 90 == 0 else 0.7) * sin(radians(angle))
            draw.line([center, center, x1, y1], fill='#333333', width=size//60)
    
    # Save the image
    img.save(filename, 'PNG')
    print(f"Created {filename} ({size}x{size})")

if __name__ == "__main__":
    from math import cos, sin, radians
    
    # Create icons
    create_icon(192, 'icon-192x192.png')
    create_icon(512, 'icon-512x512.png')