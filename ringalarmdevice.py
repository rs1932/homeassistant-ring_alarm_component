"""Base class for  devices."""
from homeassistant.core import callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity import Entity
import datetime
from homeassistant.const import ATTR_BATTERY_LEVEL

from .constants import *


class RingAlarmDevice(Entity):
    """Representation of a RingAlarm device entity."""

    def __init__(self, ringalarm_device):
        self.ringalarm_device = ringalarm_device
        self.controller = ringalarm_device[DEVICE_CONTROLLER]
        self._zid = ringalarm_device[DEVICE_ZID]
        self._name = ringalarm_device[DEVICE_NAME]
        self._entity_id = self._zid
        self.controller.register(self._zid, self._callback)

        self._last_update = datetime.datetime.fromtimestamp(ringalarm_device[DEVICE_LAST_UPDATE] // 1000).strftime(
            '%A %d, %B %Y %H:%M:%S')
        try:
            self._tamper_status = ringalarm_device[DEVICE_TAMPER_STATUS]
        except:
            pass
        try:
            self._battery_level = ringalarm_device[DEVICE_BATTERY_LEVEL]
        except:
            pass
        try:
            self._battery_status = ringalarm_device[DEVICE_BATTERY_STATUS]
        except:
            pass

    @callback
    def _callback(self, data):
        try:
            self._last_update = datetime.datetime.fromtimestamp(data[DEVICE_LAST_UPDATE] // 1000).strftime(
                '%A %d, %B %Y %H:%M:%S')
        except:
            pass
        try:
            self._tamper_status = data[DEVICE_TAMPER_STATUS]
        except:
            pass
        try:
            self._battery_level = data[DEVICE_BATTERY_LEVEL]
        except:
            pass

        try:
            self._device_rssi = data[DEVICE_RSSI]
        except:
            pass

        self._update_callback(data)

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def should_poll(self):
        return False

    def update(self):
        pass

    @property
    def device_state_attributes(self):

        attr = {}
        if self._tamper_status:
            try:
                attr[ATTR_TAMPERSTATUS] = self._tamper_status
            except:
                pass
        if self._zid:
            try:
                attr[ATTR_ZID] = self._zid
            except:
                pass
        if not isNaN(self._battery_level):
            try:
                attr[ATTR_BATTERY_LEVEL] = self._battery_level
            except:
                pass
        # if not isNaN(self._device_rssi):
        #    attr[ATTR_RSSI_LEVEL] = self._device_rssi
        if not isNaN(self._last_update):
            try:
                attr[ATTR_LASTUPDATE] = self._last_update
            except:
                pass
        return attr


def isNaN(num):
    return num != num
