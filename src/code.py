import json
import time
import wifi
import socketpool

import adafruit_logging as logging

import graphics.root_group_singleton
from graphics.background_manager import BackgroundManager
from graphics.dino_animator import DinoAnimator
from kv_store import KVStore
import resources_singleton

from constants import SD_MOUNT_POINT

log = logging.getLogger("main")
log.setLevel(logging.DEBUG)

CONFIG_FILE = f"{SD_MOUNT_POINT}/config.json"

log.info("Initializing hardware resources")
resources = resources_singleton.get_resources()
display = resources.get_display()
touchscreen = resources.get_touchscreen()

log.info("Loading WiFi config from %s", CONFIG_FILE)
with open(CONFIG_FILE, "r") as f:
    config = json.load(f)

log.info("Connecting to WiFi SSID: %s", config["wifi_ssid"])
wifi.radio.connect(config["wifi_ssid"], config["wifi_password"])
log.info("WiFi connected, IP: %s", wifi.radio.ipv4_address)

pool = socketpool.SocketPool(wifi.radio)
background_manager = BackgroundManager(pool)

display_root_group = graphics.root_group_singleton.get_root_group(display)

bg_tg = background_manager.load_background()
display_root_group.append(bg_tg)

kv = KVStore()
dino_animator = DinoAnimator(touchscreen, display_root_group, display, kv)

display.auto_refresh = False
log.info("Setup complete, entering main loop")

while True:
    dino_animator.update()
    display.refresh()
