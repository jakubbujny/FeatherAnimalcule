import subprocess
import shutil
from pathlib import Path
import argparse


def find_ffmpeg(explicit_path: str | None = None) -> str:
    if explicit_path:
        p = Path(explicit_path)
        if p.exists():
            return str(p)
        raise FileNotFoundError(f"ffmpeg not found at: {explicit_path}")

    ffmpeg = shutil.which("ffmpeg")
    if ffmpeg:
        return ffmpeg

    raise FileNotFoundError("ffmpeg not found. Install it or pass ffmpeg_path=...")

def mp4_to_transparent_gif_mcu(
    in_mp4: str,
    out_gif: str,
    *,
    ffmpeg_path: str | None = None,
    fps: int = 12,
    width: int = 160,
    colors: int = 64,
    key_color: str = "0x00FF00",
    similarity: float = 0.25,
    blend: float = 0.05,
    dither: str = "bayer:bayer_scale=3",  # or "none"
):
    ffmpeg = find_ffmpeg(ffmpeg_path)

    in_path = Path(in_mp4)
    out_path = Path(out_gif)
    if not in_path.exists():
        raise FileNotFoundError(in_mp4)

    palette_path = out_path.with_suffix(".palette.png")

    # 1) Generate palette with reserved transparent index
    palette_cmd = [
        ffmpeg, "-y",
        "-i", str(in_path),
        "-vf",
        (
            f"fps={fps},"
            f"scale={width}:-1:flags=lanczos,"
            f"colorkey={key_color}:{similarity}:{blend},"
            "format=rgba,"
            f"palettegen=max_colors={colors}:reserve_transparent=1:stats_mode=diff"
        ),
        str(palette_path)
    ]

    # 2) Use palette to create GIF (transparent)
    gif_cmd = [
        ffmpeg, "-y",
        "-i", str(in_path),
        "-i", str(palette_path),
        "-lavfi",
        (
            f"fps={fps},"
            f"scale={width}:-1:flags=lanczos,"
            f"colorkey={key_color}:{similarity}:{blend},"
            "format=rgba"
            f"[x];[x][1:v]paletteuse=dither={dither}:diff_mode=rectangle:alpha_threshold=128"
        ),
        "-gifflags", "+transdiff",
        "-loop", "0",
        str(out_path)
    ]

    def run(cmd):
        p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if p.returncode != 0:
            raise RuntimeError(f"Command failed:\n{' '.join(cmd)}\n\nffmpeg stderr:\n{p.stderr}")

    run(palette_cmd)
    run(gif_cmd)

    try:
        palette_path.unlink()
    except OSError:
        pass

    return str(out_path)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert MP4 to transparent GIF for MCU display")
    parser.add_argument("input", help="Input MP4 file path")
    parser.add_argument("output", help="Output GIF file path")
    parser.add_argument("--bg-color", default="0x00FF00",
                        help="Background color to make transparent (default: 0x00FF00)")
    parser.add_argument("--fps", type=int, default=10, help="Frame rate (default: 10)")
    parser.add_argument("--width", type=int, default=160, help="Output width in pixels (default: 128)")
    parser.add_argument("--colors", type=int, default=48, help="Number of colors (default: 48)")
    parser.add_argument("--similarity", type=float, default=0.28, help="Color similarity threshold (default: 0.28)")
    parser.add_argument("--blend", type=float, default=0.04, help="Color blend threshold (default: 0.04)")
    parser.add_argument("--dither", default="bayer:bayer_scale=2",
                        help="Dither algorithm (default: bayer:bayer_scale=2)")

    args = parser.parse_args()

    mp4_to_transparent_gif_mcu(
        args.input,
        args.output,
        fps=args.fps,
        width=args.width,
        colors=args.colors,
        key_color=args.bg_color,
        similarity=args.similarity,
        blend=args.blend,
        dither=args.dither,
    )
    print(f"Done. Converted {args.input} to {args.output}")
