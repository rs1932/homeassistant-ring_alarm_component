DOMAIN = 'ring_alarm'
import datetime
import logging
from .pyringalarm import RingLocations


_LOGGER = logging.getLogger(__name__)

from homeassistant.core import callback
from homeassistant.helpers.entity import Entity

import voluptuous as vol

from .constants import *

from homeassistant.const import ATTR_BATTERY_LEVEL

from homeassistant.const import CONF_PASSWORD, CONF_USERNAME
import homeassistant.helpers.config_validation as cv

#from pyringalarm import  RingLocations

custom_columns = [DEVICE_CONTROLLER, DEVICE_MAPPED_TYPE]


"""
DEVICE_ZID = 'general.v2.zid'
DEVICE_NAME = 'general.v2.name'
DEVICE_UPDATE_NAME='context.v1.deviceName'
DEVICE_DOORBOT_ID = 'general.v2.doorbotId'
DEVICE_BATTERY_STATUS = 'general.v2.batteryStatus'
DEVICE_BATTERY_LEVEL = 'general.v2.batteryLevel'
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
DEVICE_SOURCE = 'custom.device.source'
DEVICE_LOCKED = 'device.v1.locked'
"""
RINGALARM_CONTROLLERS = 'ringalarm_controllers'
RINGALARM_DEVICES = 'ringalarm_devices'
CONFIG = "config"

RINGALARM_COMPONENTS = ['binary_sensor', 'switch', 'lock', 'alarm_control_panel']

CONFIG_SCHEMA = vol.Schema({
    DOMAIN: vol.Schema({
        vol.Required(CONF_USERNAME): cv.string,
        vol.Required(CONF_PASSWORD): cv.string,
    }),
}, extra=vol.ALLOW_EXTRA)
#REQUIREMENTS = ['python-socketio', 'pyringalarm==0.0.2']
REQUIREMENTS = ['python-socketio']

RINGALARM_TYPEMAP = {
    'sensor.contact': 'binary_sensor',
    'sensor.flood-freeze': 'binary_sensor',
    'switch.multilevel': 'switch',
    'sensor.motion': 'binary_sensor',
    'alarm.smoke': 'binary_sensor',
    'alarm.co': 'binary_sensor',
    'motion-sensor.beams': 'binary_sensor',
    'switch.multilevel.beams': 'switch',
    'switch.transformer.beams': 'switch',
    'lock': 'lock',
    'security-panel': 'alarm_control_panel'
    # 'group.light-group.beams': 'group_switch',
    #  'hub.redsky': 'base_station',
    #  'security-keypad': 'keypad',
    #   'security-panel': 'security_panel',
    #    'access-code': 'access_code'
}


def setup(hass, config):
    logging.getLogger('socketio').setLevel(logging.ERROR)
    logging.getLogger('engineio').setLevel(logging.ERROR)
    _LOGGER.info("The ring alarm component is being initialized!")
    hass.data[RINGALARM_CONTROLLERS] = {}
    hass.data[RINGALARM_DEVICES] = {}
    hass.data[CONFIG] = config

    conf = config[DOMAIN]
    username = conf[CONF_USERNAME]
    password = conf[CONF_PASSWORD]
    hass.data[DOMAIN] = "ring_alarm"
    ring_api = RingLocations(username, password)


    locations = ring_api.get_locations()

    for location in locations:
        controller = RingLocationController(ring_api, location, hass, config)
        if controller.connect():
            hass.data[RINGALARM_CONTROLLERS][controller.hub_serial] = controller
        else:
            return False
    return True


class RingLocationController():
    """Initiate Ring Location Class."""

    def __init__(self, ring_api, location, hass, config):
        self._device_map = None  # Mapping deviceId to device object
        self._callbacks = {}  # Update value callbacks by deviceId
        self._state_handler = None
        self.hub_serial = None  # Unique serial number of the hub
        self.location_id = location.get('location_id')
        self.ring_api = ring_api
        self.ring_controller = self
        self.hass = hass
        self.config = config
        self.entities_data = None
        self.ringalarm_devices = None
        self.ringalarm_devices_list = []
        self.device_type = None

    def connect(self):
        self.ring_api.set_callbacks(async_add_device=self.async_add_device_callback,
                                    async_update_device=self.async_update_device_callback)
        self.ring_api.get_devices(self.location_id)
        return True

    @callback
    def async_add_device_callback(self, entities_data):

        self._device_map = {}
        self.entities_data = entities_data
        _LOGGER.info("Total number of Ring Alarm devices: " + str(len(entities_data.index)))

        for i in custom_columns:
            self.entities_data[i] = None
        self.add_custom_fields(self.entities_data)
        sensor_row_list = []

        for index, row in entities_data.iterrows():
            if row[DEVICE_TYPE] == 'switch.multilevel.beams':
                sensor_row = row.copy()
                sensor_row[DEVICE_ZID] = sensor_row[DEVICE_ZID] + "_1"
                sensor_row[DEVICE_NAME] = sensor_row[DEVICE_NAME] + "_1"
                sensor_row[DEVICE_TYPE] = 'motion-sensor.beams'
                sensor_row[DEVICE_MAPPED_TYPE] = 'binary_sensor'
                sensor_row_list.append(sensor_row)

        devices_data = entities_data.append(sensor_row_list, ignore_index=True)

        if self.hass.data[RINGALARM_CONTROLLERS]:
            for index, device in devices_data.iterrows():
                if device[DEVICE_MAPPED_TYPE] in RINGALARM_COMPONENTS:
                    self.hass.helpers.discovery.load_platform(device[DEVICE_MAPPED_TYPE], DOMAIN,
                                                              device, self.config)
                    _LOGGER.info("Adding component " + device[DEVICE_NAME])

    def add_custom_fields(self, devices):
        self._device_map = {}
        devices.loc[:, DEVICE_CONTROLLER] = self
        devices[DEVICE_MAPPED_TYPE] = devices[DEVICE_TYPE].apply(self._map_device_to_type)

    @callback
    def async_update_device_callback(self, updated_entities):
        for index, row in updated_entities.iterrows():
            try:
                _LOGGER.info("Update received for device " + row[DEVICE_ZID])
            except:
                pass
            _entity_id = row[DEVICE_ZID]
            if _entity_id in self._callbacks:
                self._callbacks[_entity_id](row)
            if _entity_id + "_1" in self._callbacks:
                self._callbacks[_entity_id + "_1"](row)

    def register(self, device_id, callback):
        self._callbacks[device_id] = callback

    def _map_device_to_type(self, type):
        self.device_type = None
        self.device_type = RINGALARM_TYPEMAP.get(type)
        return self.device_type



