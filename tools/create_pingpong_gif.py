import argparse
from PIL import Image

parser = argparse.ArgumentParser(description="Create a ping-pong (boomerang) GIF from an input GIF")
parser.add_argument("input", help="Input GIF file path")
parser.add_argument("output", help="Output ping-pong GIF file path")
parser.add_argument("--scale", type=float, default=1.0,
                    help="Scale factor (e.g. 0.75). Content is scaled and centered on original canvas size.")
args = parser.parse_args()

img = Image.open(args.input)
canvas_w, canvas_h = img.width, img.height

frames = []
durations = []

# Extract all frames as RGBA to preserve alpha channel consistently.
for i in range(img.n_frames):
    img.seek(i)
    frame = img.convert("RGBA")

    if args.scale != 1.0:
        new_w = round(canvas_w * args.scale)
        new_h = round(canvas_h * args.scale)
        scaled = frame.resize((new_w, new_h), Image.LANCZOS)
        canvas = Image.new("RGBA", (canvas_w, canvas_h), (0, 0, 0, 0))
        paste_x = (canvas_w - new_w) // 2
        paste_y = canvas_h - new_h  # anchor to bottom
        canvas.paste(scaled, (paste_x, paste_y))
        frame = canvas

    frames.append(frame)
    durations.append(img.info.get("duration", 100))

# Build ping-pong sequence: forward + reverse (excluding first and last to avoid stutter)
pingpong_frames = list(frames) + list(reversed(frames[1:-1]))
pingpong_durations = list(durations) + list(reversed(durations[1:-1]))

pingpong_frames[0].save(
    args.output,
    save_all=True,
    append_images=pingpong_frames[1:],
    duration=pingpong_durations,
    loop=0,
    disposal=2,
)

print(f"Created ping-pong GIF with {len(pingpong_frames)} frames ({canvas_w}x{canvas_h}, scale={args.scale}): {args.output}")
