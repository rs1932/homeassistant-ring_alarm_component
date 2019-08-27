"""Constants for the ring alarm component."""
import logging
from homeassistant.const import ATTR_BATTERY_LEVEL

_LOGGER = logging.getLogger('homeassistant.components.ringalarm')

CONFIG_FILE = 'ring_alarm.conf'
OATH_ENDPOINT = "https://oauth.ring.com/oauth/token"
LOCATIONS_ENDPOINT = "https://app.ring.com/rhq/v1/devices/v1/locations"
HUB_ENDPOINT = "https://app.ring.com/api/v1/clap/tickets?locationID="

DEVICE_ZID = 'general.v2.zid'
DEVICE_NAME = 'general.v2.name'
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
DEVICE_LOCKED = 'device.v1.locked'
DEVICE_CONTROLLER = 'custom.controller'
DEVICE_MAPPED_TYPE = 'custom.mapped_type'
DEVICE_SOURCE = 'custom.device.source'
DEVICE_CALLBACK = 'custom.device.callback'
DEVICE_SMOKE_STATUS = 'device.v1.alarmstatus'
DEVICE_LOCKED_BY = 'impulse.v1.impulseType'
DEVICE_ALARM_MODE = 'device.v1.mode'


ATTR_TAMPERSTATUS = "tamper status"
ATTR_ZID = "zid"
ATTR_LASTUPDATE = "last updated"
ATTR_RSSI_LEVEL = "signal strength"




attr_list = [ATTR_BATTERY_LEVEL, ATTR_LASTUPDATE, ATTR_RSSI_LEVEL, ATTR_TAMPERSTATUS]