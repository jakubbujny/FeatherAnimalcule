import time

import adafruit_imageload
import adafruit_ntp
import displayio
import socketpool

import adafruit_logging as logging

from constants import SD_MOUNT_POINT

log = logging.getLogger("background")
log.setLevel(logging.DEBUG)

_TIME_PERIODS = (
    (6, 12, "morning"),
    (12, 17, "day"),
    (17, 21, "evening"),
    (21, 24, "night"),
    (0, 6, "night"),
)


class BackgroundManager:

    def __init__(self, pool: socketpool.SocketPool):
        log.info("Initializing NTP client")
        self._ntp = adafruit_ntp.NTP(pool, tz_offset=1)

    def get_current_time(self) -> time.struct_time:
        return self._ntp.datetime

    def get_time_period(self) -> str:
        hour = self.get_current_time().tm_hour
        for start, end, period in _TIME_PERIODS:
            if start <= hour < end:
                return period
        return "night"

    def get_background_path(self) -> str:
        period = self.get_time_period()
        return f"{SD_MOUNT_POINT}/background/{period}.bmp"

    def load_background(self) -> displayio.TileGrid:
        path = self.get_background_path()
        ntp_time = self.get_current_time()
        period = self.get_time_period()
        log.info("NTP time: %s, period: %s, background: %s", ntp_time, period, path)
        bitmap, palette = adafruit_imageload.load(
            path,
            bitmap=displayio.Bitmap,
            palette=displayio.Palette,
        )
        log.debug("Background loaded successfully")
        return displayio.TileGrid(bitmap, pixel_shader=palette)
