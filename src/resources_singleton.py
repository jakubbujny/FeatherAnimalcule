import board
import fourwire
import adafruit_hx8357
import adafruit_tsc2007
import constants
import displayio


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
        self.spi = board.SPI()
        self.i2c = board.STEMMA_I2C()
        self.display_bus = fourwire.FourWire(self.spi, command=self.tft_dc, chip_select=self.tft_cs)
        self.display = adafruit_hx8357.HX8357(self.display_bus, width=self.display_width, height=self.display_height)
        irq_dio = None
        self.tsc = adafruit_tsc2007.TSC2007(self.i2c, irq=irq_dio)

    def get_display(self) -> adafruit_hx8357.HX8357:
        return self.display

    def get_touchscreen(self) -> adafruit_tsc2007.TSC2007:
        return self.tsc

def get_resources() -> ResourcesSingleton:
    global _instance
    if _instance is None:
        _instance = ResourcesSingleton()
    return _instance
