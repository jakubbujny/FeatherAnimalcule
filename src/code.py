import time
import board
import adafruit_dotstar
import feathers2

feathers2.enable_LDO2(True)

dotstar = adafruit_dotstar.DotStar(board.APA102_SCK, board.APA102_MOSI, 1, brightness=0.3, auto_write=True)

colors = [
    (255, 0, 0),   # red
    (0, 255, 0),   # green
    (0, 0, 255),   # blue
    (255, 255, 0), # yellow
    (0, 255, 255), # cyan
    (255, 0, 255), # magenta
    (255, 255, 255), # white
]

while True:
    for c in colors:
        dotstar[0] = c
        time.sleep(0.4)
        dotstar[0] = (0, 0, 0)
        time.sleep(0.2)
