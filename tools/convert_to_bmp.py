from PIL import Image

in_path = "image.png"
out_path = "image.bmp"

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
