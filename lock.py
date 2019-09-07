import logging
from homeassistant.components.lock import ENTITY_ID_FORMAT, LockDevice
from homeassistant.util import convert
from .constants import *

from . import RINGALARM_DEVICES
    #RingAlarmDevice

from homeassistant.const import ATTR_BATTERY_LEVEL
from .ringalarmdevice import RingAlarmDevice
from homeassistant.core import callback

from homeassistant.const import (
    ATTR_BATTERY_LEVEL,
    STATE_LOCKED,
    STATE_UNLOCKED,
)

_LOGGER = logging.getLogger(__name__)


def setup_platform(hass, config, add_devices, device):
    # for index, device in devices.iterrows():
    add_devices([RingAlarmLock(device)], True)

class RingAlarmLock(RingAlarmDevice, LockDevice):

    def __init__(self, ringalarm_device):
        # self._state = True
        super().__init__(ringalarm_device)
        self._is_locked = ringalarm_device[DEVICE_LOCKED]
        self._state = ringalarm_device[DEVICE_LOCKED]
        self._battery_level = ringalarm_device[DEVICE_BATTERY_LEVEL]
        self._tamper_status = ringalarm_device[DEVICE_TAMPER_STATUS]
        self._locked_by = None

    @property
    def is_locked(self):
        return self._is_locked

    @property
    def state(self) -> str:
        return self._is_locked

    def update(self):
        pass

    def update_callback(self, data):
        try:
            self._state = data[DEVICE_LOCKED]
            self._is_locked = data[DEVICE_LOCKED]
        except:
            pass

        self.schedule_update_ha_state(True)

    def lock(self, **kwargs):
        try:
            self.controller.ring_api.send_command_ring(self.ringalarm_device[DEVICE_ZID],
                                                       self.ringalarm_device[DEVICE_SOURCE],
                                                       "lock.lock")
        except:
            pass

    def unlock(self, **kwargs):
        try:
            self.controller.ring_api.send_command_ring(self.ringalarm_device[DEVICE_ZID],
                                                       self.ringalarm_device[DEVICE_SOURCE],
                                                       "lock.unlock")
        except:
            pass
