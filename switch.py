import logging
from homeassistant.components.binary_sensor import (
    ENTITY_ID_FORMAT, BinarySensorDevice)
from homeassistant.components.switch import ENTITY_ID_FORMAT, SwitchDevice
from homeassistant.const import ATTR_BATTERY_LEVEL
from homeassistant.core import callback
from homeassistant.util import convert

from . import RINGALARM_DEVICES
from .ringalarmdevice import RingAlarmDevice
from .constants import *

_LOGGER = logging.getLogger(__name__)


def setup_platform(hass, config, add_devices, device):
    add_devices([RingAlarmSwitch(device)], True)


class RingAlarmSwitch(RingAlarmDevice, SwitchDevice):
    def __init__(self, ringalarm_device):
        super().__init__(ringalarm_device)
        self._state = ringalarm_device[DEVICE_ON]

    def turn_on(self, **kwargs):
        try:
            self.controller.ring_api.send_command_ring(self.ringalarm_device[DEVICE_ZID],
                                                       self.ringalarm_device[DEVICE_SOURCE],
                                                       "light-mode.set", data={"lightMode": "on", "duration": 60})
        except:
            pass

    def turn_off(self, **kwargs):
        try:
            self.controller.ring_api.send_command_ring(self.ringalarm_device[DEVICE_ZID],
                                                       self.ringalarm_device[DEVICE_SOURCE],
                                                       "light-mode.set", data={"lightMode": "default", "duration": 60})
        except:
            pass

    @property
    def is_on(self):
        return self._state

    def update(self):
        pass

    def update_callback(self, data):
        try:
            self._state = data[DEVICE_UPDATE_ON]
        except:
            pass
        self.schedule_update_ha_state(True)
        return True
