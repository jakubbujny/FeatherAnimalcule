import argparse
from PIL import Image

parser = argparse.ArgumentParser(description="Convert image to 8-bit BMP with green background for transparency")
parser.add_argument("input", help="Input image file path")
parser.add_argument("output", help="Output BMP file path")
args = parser.parse_args()

in_path = args.input
out_path = args.output

GREEN = (0, 255, 0, 255)  # RGB 00ff00 + fully opaque alpha

img = Image.open(in_path)

# Replace any transparency with green-screen (00ff00)
img_rgba = img.convert("RGBA")
bg = Image.new("RGBA", img_rgba.size, GREEN)
img_no_alpha = Image.alpha_composite(bg, img_rgba).convert("RGB")

# Convert to 8-bit paletted image (max 256 colors)
img_8bit = img_no_alpha.convert(
    "P",
    palette=Image.Palette.ADAPTIVE,
    colors=256,
)

# Save as 8-bit BMP
img_8bit.save(out_path, format="BMP")

print("Saved:", out_path)
