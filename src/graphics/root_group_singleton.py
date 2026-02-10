import displayio

import adafruit_hx8357

_instance = None

class RootGroupSingleton:

    def __init__(self, display: adafruit_hx8357.HX8357):
        self.display = display
        self.root_group = displayio.Group()
        self.display.root_group = self.root_group

    def append(self, group):
        self.root_group.append(group)



def get_root_group(display: adafruit_hx8357.HX8357) -> RootGroupSingleton:
    global _instance
    if _instance is None:
        _instance = RootGroupSingleton(display)
    return _instance
