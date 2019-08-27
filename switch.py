import logging
from homeassistant.components.binary_sensor import (
    ENTITY_ID_FORMAT, BinarySensorDevice)
from homeassistant.components.switch import ENTITY_ID_FORMAT, SwitchDevice
from homeassistant.const import ATTR_BATTERY_LEVEL
from homeassistant.core import callback
from homeassistant.util import convert

from . import RINGALARM_DEVICES
from .ringalarmdevice import RingAlarmDevice

DEVICE_ZID = 'general.v2.zid'
DEVICE_NAME = 'general.v2.name'
DEVICE_DOORBOT_ID = 'general.v2.doorbotId'
DEVICE_BATTERY_STATUS = 'general.v2.batteryStatus'
DEVICE_TYPE = 'general.v2.deviceType'
DEVICE_LAST_UPDATE = 'general.v2.lastUpdate'
DEVICE_ROOM_ID = 'general.v2.roomId'
DEVICE_TAMPER_STATUS = 'general.v2.tamperStatus'
DEVICE_RSSI = 'device.v1.networks.wlan0.rssi'
DEVICE_ON = 'device.v1.on'
DEVICE_UPDATE_ON = 'context.v1.device.v1.on'
DEVICE_MOTION_STATUS = 'device.v1.motionStatus'
DEVICE_FAULTED = 'device.v1.faulted'
DEVICE_CONTROLLER = 'custom.controller'
DEVICE_MAPPED_TYPE = 'custom.mapped_type'
DEVICE_BATTERY_LEVEL = 'general.v2.batteryLevel'
DEVICE_SOURCE = 'custom.device.source'

_LOGGER = logging.getLogger(__name__)


def setup_platform(hass, config, add_devices, device):
    # for index, device in devices.iterrows():
    add_devices([RingAlarmSwitch(device)], True)


class RingAlarmSwitch(RingAlarmDevice, SwitchDevice):
    def __init__(self, ringalarm_device):
        super().__init__(ringalarm_device)
        self._state = ringalarm_device[DEVICE_ON]
        self._battery_level = ringalarm_device[DEVICE_BATTERY_LEVEL]
        self._tamper_status = ringalarm_device[DEVICE_TAMPER_STATUS]

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

    def _update_callback(self, data):
        try:
            self._state = data[DEVICE_UPDATE_ON]
        except:
            pass
        self.schedule_update_ha_state(True)
        return True
