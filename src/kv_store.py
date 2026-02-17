import os

import adafruit_logging as logging

from constants import SD_MOUNT_POINT

log = logging.getLogger("kv")
log.setLevel(logging.DEBUG)

_STORE_DIR = f"{SD_MOUNT_POINT}/state"


class KVStore:

    def __init__(self):
        try:
            os.mkdir(_STORE_DIR)
            log.info("Created store directory %s", _STORE_DIR)
        except OSError:
            log.debug("Store directory %s already exists", _STORE_DIR)

    def _path(self, key):
        return f"{_STORE_DIR}/{key}"

    def get(self, key, default=None):
        try:
            with open(self._path(key), "r") as f:
                val = f.read()
            log.debug("GET %s = %s", key, val)
            return val
        except OSError:
            log.debug("GET %s -> default (%s)", key, default)
            return default

    def get_int(self, key, default=0):
        val = self.get(key)
        if val is None:
            return default
        return int(val)

    def set(self, key, value):
        with open(self._path(key), "w") as f:
            f.write(str(value))
        log.debug("SET %s = %s", key, value)

    def delete(self, key):
        try:
            os.remove(self._path(key))
            log.debug("DEL %s", key)
        except OSError:
            log.debug("DEL %s (not found)", key)

    def keys(self):
        try:
            result = os.listdir(_STORE_DIR)
            log.debug("KEYS -> %s", result)
            return result
        except OSError:
            return []
