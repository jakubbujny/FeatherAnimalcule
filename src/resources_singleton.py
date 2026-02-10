import os

import board
import fourwire
import adafruit_hx8357
import adafruit_sdcard
import adafruit_tsc2007
import constants
import displayio
import storage
import digitalio


_instance = None


class ResourcesSingleton:
    tft_cs = board.D5
    tft_dc = board.D6
    sd_scs = board.D20
    display_width = constants.DISPLAY_WIDTH
    display_height = constants.DISPLAY_HEIGHT
    def __init__(self):
        # Use Hardware SPI
        displayio.release_displays()
        self._spi = board.SPI()
        self._i2c = board.STEMMA_I2C()
        self._display_bus = fourwire.FourWire(self._spi, command=self.tft_dc, chip_select=self.tft_cs)
        self._display = adafruit_hx8357.HX8357(self._display_bus, width=self.display_width, height=self.display_height)
        irq_dio = None
        self._tsc = adafruit_tsc2007.TSC2007(self._i2c, irq=irq_dio)

        self._sd_cs = digitalio.DigitalInOut(self.sd_scs)
        self._sd = adafruit_sdcard.SDCard(self._spi, self._sd_cs)
        self._sd_vfs = storage.VfsFat(self._sd)
        storage.mount(self._sd_vfs, constants.SD_MOUNT_POINT)

    def get_display(self) -> adafruit_hx8357.HX8357:
        return self._display

    def get_touchscreen(self) -> adafruit_tsc2007.TSC2007:
        return self._tsc

    def get_sd_card(self) -> adafruit_sdcard.SDCard:
        return self._sd

def get_resources() -> ResourcesSingleton:
    global _instance
    if _instance is None:
        _instance = ResourcesSingleton()
    return _instance
