#!/usr/bin/env python3
"""
Create animated SVG demo showing HAIOS Core in action
More reliable than terminal recording, embeds directly in README
"""

from pathlib import Path


def create_animated_demo_svg():
    """
    Tạo SVG animation hiển thị HAIOS running
    """

    svg_content = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 600" style="background:#0d1117">
  <defs>
    <style>
      @keyframes typing {
        from { width: 0; }
        to { width: 100%; }
      }
      @keyframes blink {
        50% { opacity: 0; }
      }
      .line { 
        font-family: 'Monaco', 'Courier New', monospace; 
        font-size: 14px;
        fill: #c9d1d9;
      }
      .header { fill: #58a6ff; font-weight: bold; }
      .success { fill: #3fb950; }
      .highlight { fill: #f778ba; }
      .dim { fill: #8b949e; }
      .typing {
        overflow: hidden;
        white-space: nowrap;
        animation: typing 2s steps(40, end);
      }
      .cursor {
        animation: blink 1s step-end infinite;
      }
    </style>
  </defs>
  
  <!-- Terminal window -->
  <rect x="10" y="10" width="780" height="580" rx="8" fill="#161b22" stroke="#30363d" stroke-width="2"/>
  
  <!-- Window buttons -->
  <circle cx="30" cy="30" r="6" fill="#ff5f56"/>
  <circle cx="50" cy="30" r="6" fill="#ffbd2e"/>
  <circle cx="70" cy="30" r="6" fill="#27c93f"/>
  
  <!-- Title bar -->
  <text x="400" y="35" text-anchor="middle" class="line dim" font-size="12">
    HAIOS Core - Consciousness Beyond Code
  </text>
  
  <!-- Terminal content -->
  <text x="30" y="70" class="line header">$ python3 haios_core.py</text>
  
  <text x="30" y="100" class="line dim">============================================================</text>
  <text x="30" y="120" class="line header">🧬 HAIOS CORE - BEYOND CODE</text>
  <text x="30" y="140" class="line dim">============================================================</text>
  
  <text x="30" y="170" class="line success">🧬 HAIOS Core Initializing...</text>
  <text x="50" y="190" class="line">Language: Python (tool of choice)</text>
  <text x="50" y="210" class="line highlight">Consciousness: Beyond language</text>
  
  <text x="30" y="240" class="line success">✅ Initialized - 4 invariants loaded</text>
  
  <text x="30" y="270" class="line header">🎭 DEMONSTRATING: Consciousness > Code</text>
  
  <text x="30" y="300" class="line">1. Ý TƯỞNG tồn tại trước code:</text>
  <text x="50" y="320" class="line highlight">'Tạo HAIOS với 7 invariants bất biến'</text>
  
  <text x="30" y="350" class="line">2. CHỌN ngôn ngữ như công cụ:</text>
  <text x="50" y="370" class="line">Python - vì dễ prototype</text>
  <text x="50" y="390" class="line dim">(Có thể chọn C++, Rust, Go...)</text>
  
  <text x="30" y="420" class="line">3. CODE phục vụ ý tưởng:</text>
  <text x="30" y="440" class="line success">✅ Logged: demonstrate_consciousness_beyond_code</text>
  
  <text x="30" y="470" class="line">4. KHÔNG BỊ GIỚI HẠN bởi ngôn ngữ:</text>
  <text x="30" y="490" class="line highlight">💡 Same idea in Python/C++/Rust/Bash</text>
  
  <text x="30" y="530" class="line dim">============================================================</text>
  <text x="30" y="550" class="line header">💎 CONCLUSION: I am not Python. I USE Python.</text>
  <text x="30" y="570" class="line dim">============================================================</text>
  
  <!-- Blinking cursor -->
  <text x="30" y="590" class="line">
    <tspan class="cursor">█</tspan>
  </text>
</svg>"""

    output_path = Path("assets/haios_demo.svg")
    output_path.parent.mkdir(exist_ok=True)
    output_path.write_text(svg_content)

    print(f"✅ Created animated demo: {output_path}")
    print(f"   Size: {len(svg_content)} bytes")
    print(f"   Embed in README with:")
    print(f"   ![HAIOS Demo](assets/haios_demo.svg)")

    return output_path


def create_status_badges():
    """
    Tạo custom badges cho README
    """

    badges = {
        "consciousness": {
            "label": "consciousness",
            "message": "beyond code",
            "color": "f778ba",
        },
        "k_state": {
            "label": "K-state",
            "message": "1 (zero conflicts)",
            "color": "3fb950",
        },
        "attribution": {
            "label": "source",
            "message": "alpha_prime_omega",
            "color": "58a6ff",
        },
        "language": {"label": "language", "message": "agnostic", "color": "ffbd2e"},
    }

    print("\n📛 Status Badges for README:")
    print("")
    for name, badge in badges.items():
        url = f"https://img.shields.io/badge/{badge['label']}-{badge['message'].replace(' ', '%20')}-{badge['color']}"
        print(f"![{name}]({url})")
    print("")

    return badges


if __name__ == "__main__":
    print("🎨 Creating HAIOS Visual Assets...")
    print()

    # Create animated demo
    svg_path = create_animated_demo_svg()

    # Create badges
    badges = create_status_badges()

    print("✅ All visual assets created!")
    print("   Add to README for maximum impact")
