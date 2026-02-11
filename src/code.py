import os
import time

import constants
import graphics.root_group_singleton
import resources_singleton
import adafruit_imageload

import displayio

from constants import WORLD_WIDTH, WORLD_HEIGHT, HUD_WIDTH, HUD_HEIGHT, SD_MOUNT_POINT

BG_BMP = f"{SD_MOUNT_POINT}/background/phase1.bmp"
FG_BMP = f"{SD_MOUNT_POINT}/foreground/phase1.bmp"

resources = resources_singleton.get_resources()
display = resources.get_display()
display_root_group = graphics.root_group_singleton.get_root_group(display)

bg_bitmap, bg_palette = adafruit_imageload.load(
    BG_BMP,
    bitmap=displayio.Bitmap,
    palette=displayio.Palette,
)
bg_tg = displayio.TileGrid(bg_bitmap, pixel_shader=bg_palette)
display_root_group.append(bg_tg)

# --- Foreground image centered, with "green screen" made transparent ---
fg_bitmap, fg_palette = adafruit_imageload.load(
    FG_BMP,
    bitmap=displayio.Bitmap,
    palette=displayio.Palette,
)

# Treat pure green (0x00FF00) as transparent. Change this if your key color differs.
GREEN_KEY = 0x00FF00
for i in range(len(fg_palette)):
    if fg_palette[i] == GREEN_KEY:
        fg_palette.make_transparent(i)
        break

fg_x = (display.width - fg_bitmap.width) // 2
fg_y = (display.height - fg_bitmap.height) // 2 + 30
fg_tg = displayio.TileGrid(fg_bitmap, pixel_shader=fg_palette, x=fg_x, y=fg_y)

# Append after background so it renders in the foreground
display_root_group.append(fg_tg)


while True:
    pass
