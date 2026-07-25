#!/usr/bin/env python3
"""
Create demo screenshot image from captured output
Simulates terminal appearance for GitHub README
"""

import textwrap

from PIL import Image, ImageDraw, ImageFont

# Terminal-style image settings
WIDTH = 1000
HEIGHT = 800
BG_COLOR = "#0d1117"
TEXT_COLOR = "#c9d1d9"
PROMPT_COLOR = "#58a6ff"
SUCCESS_COLOR = "#3fb950"
HEADER_COLOR = "#f778ba"

# Read demo output
with open("assets/demo-output.txt", "r") as f:
    demo_text = f.read()

# Create image
img = Image.new("RGB", (WIDTH, HEIGHT), BG_COLOR)
draw = ImageDraw.Draw(img)

try:
    # Use monospace font
    font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Monaco.dfont", 14)
    title_font = ImageFont.truetype(
        "/System/Library/Fonts/Supplemental/Monaco.dfont", 16
    )
except:
    font = ImageFont.load_default()
    title_font = ImageFont.load_default()

# Draw terminal header
draw.rectangle([(0, 0), (WIDTH, 30)], fill="#161b22")
draw.text((10, 8), "● ● ●  DAIOF Framework Demo", font=title_font, fill=TEXT_COLOR)

# Draw terminal content
y_offset = 45
line_height = 18
max_lines = 40

lines = demo_text.split("\n")[:max_lines]

for line in lines:
    # Color coding
    color = TEXT_COLOR
    if "✅" in line or "EXCELLENT" in line:
        color = SUCCESS_COLOR
    elif "🔄" in line or "🤖" in line or "🧬" in line:
        color = HEADER_COLOR
    elif "$" in line or "Priority: HIGH" in line:
        color = PROMPT_COLOR

    # Truncate long lines
    if len(line) > 85:
        line = line[:82] + "..."

    draw.text((15, y_offset), line, font=font, fill=color)
    y_offset += line_height

    if y_offset > HEIGHT - 50:
        break

# Save image
output_path = "assets/demo-screenshot.png"
img.save(output_path, "PNG", optimize=True)

print(f"✅ Demo screenshot created: {output_path}")
print(f"   Dimensions: {WIDTH}x{HEIGHT}")
print(f"   Lines rendered: {min(len(lines), max_lines)}")
