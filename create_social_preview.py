#!/usr/bin/env python3
"""
Social Preview Image Generator for DAIOF Framework
Creates 1280x640 terminal-style banner with neon accents
"""

import os

from PIL import Image, ImageDraw, ImageFont

# Image specifications
WIDTH = 1280
HEIGHT = 640
BG_COLOR = "#0d1117"  # GitHub dark
NEON_GREEN = "#00ff9f"
WHITE = "#ffffff"
CYAN = "#00d9ff"
GRAY = "#8b949e"
TERMINAL_BG = "#161b22"

# Create image
img = Image.new("RGB", (WIDTH, HEIGHT), BG_COLOR)
draw = ImageDraw.Draw(img)

try:
    # Try to use Monaco or Courier (monospace fonts)
    title_font = ImageFont.truetype(
        "/System/Library/Fonts/Supplemental/Monaco.dfont", 72
    )
    subtitle_font = ImageFont.truetype(
        "/System/Library/Fonts/Supplemental/Monaco.dfont", 36
    )
    text_font = ImageFont.truetype(
        "/System/Library/Fonts/Supplemental/Monaco.dfont", 24
    )
    small_font = ImageFont.truetype(
        "/System/Library/Fonts/Supplemental/Monaco.dfont", 20
    )
except:
    # Fallback to default font
    title_font = ImageFont.load_default()
    subtitle_font = ImageFont.load_default()
    text_font = ImageFont.load_default()
    small_font = ImageFont.load_default()

# Title: "🧬 DAIOF FRAMEWORK"
title_text = "DAIOF FRAMEWORK"
title_bbox = draw.textbbox((0, 0), title_text, font=title_font)
title_width = title_bbox[2] - title_bbox[0]
title_x = (WIDTH - title_width) // 2
draw.text((title_x - 40, 80), "🧬", font=title_font, fill=NEON_GREEN)
draw.text((title_x + 40, 80), title_text, font=title_font, fill=NEON_GREEN)

# Subtitle: "Self-Improving Digital Organism"
subtitle_text = "Self-Improving Digital Organism"
subtitle_bbox = draw.textbbox((0, 0), subtitle_text, font=subtitle_font)
subtitle_width = subtitle_bbox[2] - subtitle_bbox[0]
subtitle_x = (WIDTH - subtitle_width) // 2
draw.text((subtitle_x, 180), subtitle_text, font=subtitle_font, fill=WHITE)

# Terminal box
box_x1, box_y1 = 100, 250
box_x2, box_y2 = 1180, 480
draw.rounded_rectangle(
    [(box_x1, box_y1), (box_x2, box_y2)],
    radius=10,
    fill=TERMINAL_BG,
    outline=CYAN,
    width=2,
)

# Terminal content
terminal_lines = [
    ("$ ./daiof-framework --status", CYAN, 280),
    ("", WHITE, 310),
    ("Status: LIVING & AUTONOMOUS ✅", NEON_GREEN, 340),
    ("Health: 100/100 EXCELLENT", NEON_GREEN, 370),
    ("Tasks:  Real-time generation every 10s", WHITE, 400),
    ("", WHITE, 420),
    ("🔄 Self-Improving  •  🏥 Self-Healing  •  🤖 Autonomous", CYAN, 440),
]

for line_text, color, y_pos in terminal_lines:
    if line_text:
        draw.text((120, y_pos), line_text, font=text_font, fill=color)

# Footer URL
footer_text = "github.com/NguyenCuong1989/DAIOF-Framework"
footer_bbox = draw.textbbox((0, 0), footer_text, font=small_font)
footer_width = footer_bbox[2] - footer_bbox[0]
footer_x = (WIDTH - footer_width) // 2
draw.text((footer_x, 550), footer_text, font=small_font, fill=GRAY)

# Version badge (bottom right)
badge_text = "v1.0.0"
badge_x, badge_y = 1100, 570
draw.rounded_rectangle(
    [(badge_x, badge_y), (badge_x + 140, badge_y + 40)],
    radius=5,
    fill="#238636",
    outline="#238636",
)
draw.text((badge_x + 20, badge_y + 8), badge_text, font=text_font, fill=WHITE)

# Save image
output_path = ".github/social-preview.png"
os.makedirs(".github", exist_ok=True)
img.save(output_path, "PNG", optimize=True)

print(f"✅ Social preview image created: {output_path}")
print(f"   Dimensions: {WIDTH}x{HEIGHT}")
print(f"   File size: {os.path.getsize(output_path) / 1024:.1f} KB")
