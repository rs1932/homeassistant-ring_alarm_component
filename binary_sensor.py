#import datetime
import logging
#import time
from homeassistant.components.binary_sensor import BinarySensorDevice

from homeassistant.const import ATTR_BATTERY_LEVEL
from homeassistant.const import TEMP_CELSIUS
from homeassistant.core import callback
from homeassistant.helpers.entity import Entity
from .ringalarmdevice import RingAlarmDevice
from .constants import *

_LOGGER = logging.getLogger(__name__)

SENSOR_TYPES = {
    'sensor.motion': ['Motion', 'mdi:run', 'motion'],
    'motion-sensor.beams': ['Motion', 'mdi:run', 'motion'],
    'switch.multilevel.beams': ['Motion', 'mdi:run', 'motion'],
    'sensor.contact': ['Door', 'mdi:window-open', 'door'],
    'alarm.smoke': ['Smoke', 'mdi:smoking', 'smoke'],
    'sensor.flood-freeze': ['Flood', 'mdi:water', 'flood'],
    'alarm.co': ['Smoke', 'mdi:smoking', 'smoke']
}


def setup_platform(hass, config, add_devices, device):
    add_devices([RingAlarmBinarySensor(device)], True)


def check_sensor_status(device):
    _state = None
    try:
        if device[DEVICE_TYPE] in ['alarm.smoke', 'alarm.co']:
            if device[DEVICE_SMOKE_STATUS] == 'inactive':
                _state = False
            if device[DEVICE_SMOKE_STATUS] == 'active':
                _state = True
    except:
        pass
    try:
        if device[DEVICE_TYPE] in ['sensor.motion', 'sensor.contact']:
            _state = device[DEVICE_FAULTED]
    except:
        pass
    try:
        if device[DEVICE_TYPE] in ['motion-sensor.beams', 'switch.multilevel.beams']:
            _state = False if device[DEVICE_MOTION_STATUS] == 'clear' else True
    except:
        pass
    return _state


class RingAlarmBinarySensor(RingAlarmDevice, BinarySensorDevice):
    """Representation of a RingAlarm Binary Sensor."""

    def __init__(self, ringalarm_device):
        self._state = False
        self._callback = None
        super().__init__(ringalarm_device)
        self._state = check_sensor_status(ringalarm_device)
        stype = None
        if ringalarm_device[DEVICE_TYPE] in SENSOR_TYPES:
            stype = ringalarm_device[DEVICE_TYPE]
        if stype:
            self._device_class = SENSOR_TYPES[stype][2]
            self._icon = SENSOR_TYPES[stype][1]
        else:
            self._device_class = None
            self._icon = None

    @property
    def device_class(self):
        """Return the device class of the sensor."""
        return self._device_class

    @property
    def is_on(self):
        """Return true if sensor is on."""
        return self._state

    def update(self):
        pass

    def update_callback(self, device):
        print("UPDATE CALLBACK")
        try:
            if device[DEVICE_TYPE] in ['alarm.smoke', 'alarm.co']:
                if device[DEVICE_SMOKE_STATUS] == 'inactive':
                    self._state = False
                if device[DEVICE_SMOKE_STATUS] == 'active':
                    self._state = True
        except:
            pass
        try:
            if device[DEVICE_TYPE] in ['sensor.motion', 'sensor.contact', 'sensor.flood-freeze']:
                try:
                    self._state = device[DEVICE_FAULTED]
                except:
                    pass
        except:
            pass

        try:
            if device[DEVICE_TYPE] in ['motion-sensor.beams', 'switch.multilevel.beams']:
                self._state = False if device['context.v1.device.v1.motionStatus'] == 'clear' else True
        except:
            pass

        self.schedule_update_ha_state(True)
        return True
