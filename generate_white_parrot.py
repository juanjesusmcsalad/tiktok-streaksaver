"""
Generates the white parrot emoji icon in multiple resolutions for app.ico
Uses the iconic green parrot emoji (Twemoji 1f99c) geometry transformed into a sleek white monochrome Volt icon.
"""

from pathlib import Path
from PIL import Image
from playwright.sync_api import sync_playwright

BASE_DIR = Path(__file__).resolve().parent

# Color variants for the white parrot
# Option 1: Sleek duotone white & silver with dark eye
SVG_TEMPLATE = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 36 36" width="512" height="512">
  <!-- Feet -->
  <path fill="{color_feet}" d="M17.5 35c-.128 0-.256-.049-.354-.146-.195-.195-.195-.512 0-.707L19 32.293V29.5c0-.276.224-.5.5-.5s.5.224.5.5v3.207l-2.146 2.146c-.098.098-.226.147-.354.147z"/>
  <path fill="{color_feet}" d="M19.5 33h-3c-.276 0-.5-.224-.5-.5s.224-.5.5-.5h3c.276 0 .5.224.5.5s-.224.5-.5.5zm3 2c-.128 0-.256-.049-.354-.146-.195-.195-.195-.512 0-.707L24 32.293V29.5c0-.276.224-.5.5-.5s.5.224.5.5v3.207l-2.146 2.146c-.098.098-.226.147-.354.147z"/>
  <path fill="{color_feet}" d="M24.5 33h-3c-.276 0-.5-.224-.5-.5s.224-.5.5-.5h3c.276 0 .5.224.5.5s-.224.5-.5.5z"/>

  <!-- Lower Beak -->
  <path fill="{color_beak_lower}" d="M3.53 13.798c.845.452 3.813-1.411 4.36-3.308S6.869 8.374 5.008 9.25 2.8 13.407 3.53 13.798z"/>

  <!-- Upper Beak -->
  <path fill="{color_beak_upper}" stroke="{color_beak_stroke}" stroke-width="0.3" d="M6.325 4C3.77 5 2.047 7.378 2.031 10.088c-.016 2.699 1.219 4.423 2.594 4.047.376-.103-.303-1.922.85-4.371.57-1.207 1.303-1.35 1.675-1.313.373.036.443-4.947-.825-4.451z"/>

  <!-- Main Body & Tail -->
  <path fill="{color_body}" d="M34.525 31.384c-.014.499-1.916.822-5.592-3.599-2.927 3.09-7.374 3.182-11.821 1.422-4.999-1.979-8.383-6.924-7.701-13.976.382-3.954-5.228-3.587-5.081-8.899C4.441 2.337 7.843.797 10.704.876c4.74.131 6.82 5.293 8.052 6.561 6.494 6.688 15.81 22.47 15.769 23.947z"/>

  <!-- Chest Feather Accent -->
  <path fill="{color_chest}" d="M28.932 27.785c-2.927 3.09-7.374 3.182-11.821 1.422-4.999-1.979-8.383-6.924-7.701-13.976.036 4.343 1.559 7.582 2.94 8.416-.58-2.79.117-7.062.784-7.779 1.591 9.402 10.022 14.78 15.798 11.917z"/>

  <!-- Lower Wing Tip -->
  <path fill="{color_wing_lower}" d="M13.135 15.867s1.737 5.788 7.33 9.387 8.468 2.53 8.468 2.53-2.939 3.363-7.647 2.084-9.321-5.997-8.151-14.001z"/>

  <!-- Main Wing -->
  <path fill="{color_wing}" stroke="{color_wing_stroke}" stroke-width="0.3" d="M16.938 9.417c-2.504-.588-6.666 7.123-1.009 13.392 7.436 8.241 13.004 4.976 13.004 4.976S24.785 11.259 16.938 9.417z"/>

  <!-- Eye -->
  <circle fill="{color_eye}" cx="8" cy="6" r="1.1"/>
  <circle fill="#FFFFFF" cx="7.7" cy="5.7" r="0.35"/>

  <!-- Neck Feather Line -->
  <path fill="{color_neck}" d="M10.724 13.259c-.79 0-1.509-.189-1.976-.45-.248-.139-.336-.453-.198-.701.14-.248.454-.336.701-.198.665.373 2.406.63 3.614-.423.213-.187.539-.165.726.05.187.214.164.54-.05.726-.836.729-1.877.996-2.817.996z"/>
</svg>"""

colors = {
    "color_body": "#FFFFFF",
    "color_chest": "#D4D4D4",
    "color_wing": "#EAEAEA",
    "color_wing_stroke": "#B8B8B8",
    "color_wing_lower": "#A8A8A8",
    "color_beak_upper": "#FFFFFF",
    "color_beak_stroke": "#A8A8A8",
    "color_beak_lower": "#C8C8C8",
    "color_feet": "#909090",
    "color_eye": "#171717",
    "color_neck": "#B8B8B8",
}

svg_content = SVG_TEMPLATE.format(**colors)
svg_file = BASE_DIR / "white_parrot.svg"
svg_file.write_text(svg_content, encoding="utf-8")

# Render with Playwright Chromium at 512x512
with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    page.set_viewport_size({"width": 512, "height": 512})
    html = f"""
    <!DOCTYPE html>
    <html>
    <body style="margin:0;padding:0;background:transparent;overflow:hidden;">
        {svg_content}
    </body>
    </html>
    """
    page.set_content(html)
    hi_res_png = BASE_DIR / "white_parrot_512.png"
    page.screenshot(path=str(hi_res_png), omit_background=True)
    browser.close()

print(f"Rendered high-res vector PNG to {hi_res_png}")

# Create multi-resolution ICO file
img = Image.open(hi_res_png)
sizes = [(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
output_ico = BASE_DIR / "app.ico"
img.save(output_ico, format="ICO", sizes=sizes)
print(f"Generated multi-resolution ICO at {output_ico} with sizes: {sizes}")

# Also copy to dist folder
dist_ico = BASE_DIR / "dist" / "TikTokStreakSaver" / "app.ico"
if dist_ico.parent.exists():
    import shutil
    shutil.copy2(output_ico, dist_ico)
    print(f"Synced icon to {dist_ico}")

# Create preview on Volt dark background #171717
bg = Image.new("RGBA", img.size, (23, 23, 23, 255))
bg.paste(img, (0, 0), img)
bg.save(BASE_DIR / "white_parrot_on_dark.png")
print("Saved white_parrot_on_dark.png")
