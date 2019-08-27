import logging
from homeassistant.components.lock import ENTITY_ID_FORMAT, LockDevice
from homeassistant.util import convert

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

DEVICE_BATTERY_LEVEL = 'general.v2.batteryLevel'
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
DEVICE_MOTION_STATUS = 'device.v1.motionStatus'
DEVICE_FAULTED = 'device.v1.faulted'
DEVICE_CONTROLLER = 'custom.controller'
DEVICE_MAPPED_TYPE = 'custom.mapped_type'
DEVICE_LOCKED = 'device.v1.locked'
DEVICE_LOCKED_BY = 'impulse.v1.impulseType'
DEVICE_SOURCE = 'custom.device.source'

_LOGGER = logging.getLogger(__name__)


def setup_platform(hass, config, add_devices, device):
    # for index, device in devices.iterrows():
    add_devices([RingAlarmLock(device)], True)


def create_entity(device_frame):
    _add_devices([RingAlarmLock(device_frame)], True)


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

    def _update_callback(self, data):
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
