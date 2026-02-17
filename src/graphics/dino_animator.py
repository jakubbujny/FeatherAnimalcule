import gifio
import displayio

import adafruit_logging as logging

from constants import SD_MOUNT_POINT
from kv_store import KVStore

log = logging.getLogger("dino")
log.setLevel(logging.DEBUG)

_STATE_WAITING = 0
_STATE_PLAYING_START = 1
_STATE_PLAYING_WAVING = 2

_TOUCH_COUNT_THRESHOLD = 10
_KV_KEY_HATCHED = "dino_hatched"

_START_GIF = f"{SD_MOUNT_POINT}/animation/dino/start.gif"
_WAVING_GIF = f"{SD_MOUNT_POINT}/animation/dino/waving_pingpong.gif"

_DINO_X = 30


class DinoAnimator:

    def __init__(self, touchscreen, root_group, display, kv):
        self._touchscreen = touchscreen
        self._root_group = root_group
        self._display = display
        self._kv = kv
        self._touch_count = 0
        self._prev_touched = False
        self._frames_played = 0

        self._gif_shader = displayio.ColorConverter(
            input_colorspace=displayio.Colorspace.RGB565_SWAPPED
        )
        self._gif_shader.make_transparent(0x000000)

        hatched = self._kv.get(_KV_KEY_HATCHED)
        if hatched:
            log.info("Already hatched, loading %s", _WAVING_GIF)
            self._odg = gifio.OnDiskGif(_WAVING_GIF)
            self._state = _STATE_PLAYING_WAVING
        else:
            log.info("Not hatched yet, loading %s", _START_GIF)
            self._odg = gifio.OnDiskGif(_START_GIF)
            self._state = _STATE_WAITING

        self._gif_tg = displayio.TileGrid(
            self._odg.bitmap,
            pixel_shader=self._gif_shader,
            x=_DINO_X,
            y=(self._display.height - self._odg.height) // 2,
        )
        self._root_group.append(self._gif_tg)
        log.debug("TileGrid placed at x=%d y=%d, gif %dx%d", _DINO_X, self._gif_tg.y, self._odg.width, self._odg.height)
        self._odg.next_frame()
        self._frames_played = 1

    def _start_playing_waving(self):
        log.info("Transition to waving, persisting hatched state")
        self._kv.set(_KV_KEY_HATCHED, "1")
        self._odg.deinit()
        self._odg = gifio.OnDiskGif(_WAVING_GIF)
        self._gif_tg.bitmap = self._odg.bitmap
        self._state = _STATE_PLAYING_WAVING

    def update(self):
        if self._state == _STATE_WAITING:
            touched = self._touchscreen.touched
            if touched and not self._prev_touched:
                self._touch_count += 1
                log.info("Touch %d/%d", self._touch_count, _TOUCH_COUNT_THRESHOLD)
            self._prev_touched = touched
            if self._touch_count >= _TOUCH_COUNT_THRESHOLD:
                log.info("Touch threshold reached, playing start animation")
                self._state = _STATE_PLAYING_START
            return 0

        if self._state == _STATE_PLAYING_START:
            self._odg.bitmap.fill(0)
            self._odg.next_frame()
            self._frames_played += 1
            log.debug("Start frame %d/%d", self._frames_played, self._odg.frame_count)
            if self._frames_played >= self._odg.frame_count:
                self._start_playing_waving()
            return delay

        if self._state == _STATE_PLAYING_WAVING:
            self._odg.bitmap.fill(0)
            self._odg.next_frame()

        return 0

        return 0
