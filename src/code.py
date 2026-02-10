import graphics.root_group_singleton
import resources_singleton

import displayio

from constants import WORLD_WIDTH, WORLD_HEIGHT, HUD_WIDTH, HUD_HEIGHT

resources = resources_singleton.get_resources()

display_root_group = graphics.root_group_singleton.get_root_group(resources.get_display())

world_bmp = displayio.Bitmap(WORLD_WIDTH, WORLD_HEIGHT, 1)
world_pal = displayio.Palette(1)
world_pal[0] = 0x003060  # world background color

world_bg = displayio.TileGrid(world_bmp, pixel_shader=world_pal, x=0, y=0)
display_root_group.append(world_bg)

# --- HUD (right) solid background ---
hud_bmp = displayio.Bitmap(HUD_WIDTH, HUD_HEIGHT, 1)
hud_pal = displayio.Palette(1)
hud_pal[0] = 0x303030  # hud background color

hud_bg = displayio.TileGrid(hud_bmp, pixel_shader=hud_pal, x=WORLD_WIDTH, y=0)
display_root_group.append(hud_bg)

while True:
    pass
