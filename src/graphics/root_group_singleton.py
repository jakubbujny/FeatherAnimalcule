import displayio

import adafruit_hx8357
import adafruit_logging as logging

log = logging.getLogger("rootgroup")
log.setLevel(logging.DEBUG)

_instance = None

class RootGroupSingleton:

    def __init__(self, display: adafruit_hx8357.HX8357):
        self.display = display
        self.root_group = displayio.Group()
        self.display.root_group = self.root_group
        log.info("Root display group created")

    def append(self, group):
        self.root_group.append(group)
        log.debug("Appended element to root group, count: %d", len(self.root_group))



def get_root_group(display: adafruit_hx8357.HX8357) -> RootGroupSingleton:
    global _instance
    if _instance is None:
        _instance = RootGroupSingleton(display)
    return _instance
