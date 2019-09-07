import logging
import pandas as pd
from homeassistant.components.alarm_control_panel import (
    AlarmControlPanel
)

from homeassistant.core import callback
from homeassistant.util import convert

from .ringalarmdevice import RingAlarmDevice
from .constants import *

from homeassistant.const import (
    STATE_ALARM_ARMED_AWAY,
    STATE_ALARM_ARMED_HOME,
    STATE_ALARM_DISARMED
)

_LOGGER = logging.getLogger(__name__)


def setup_platform(hass, config, add_devices, device):
    # for index, device in devices.iterrows():
    add_devices([RingAlarmControlPanel(device)], True)


class RingAlarmControlPanel(RingAlarmDevice, AlarmControlPanel):

    def __init__(self, ringalarm_device):

        super().__init__(ringalarm_device)
        try:
            if ringalarm_device[DEVICE_ALARM_MODE] == "none":
                self._state = STATE_ALARM_DISARMED
        except:
            pass
        try:
            if ringalarm_device[DEVICE_ALARM_MODE] == "some":
                self._state = STATE_ALARM_ARMED_HOME
        except:
            pass
        try:
            if ringalarm_device[DEVICE_ALARM_MODE] == "all":
                self._state = STATE_ALARM_ARMED_AWAY
        except:
            pass
        try:
            self._tamper_status = ringalarm_device[DEVICE_TAMPER_STATUS]
        except:
            pass

    def update(self):
        pass

    def alarm_disarm(self, code=None):
        """Send disarm command."""
        try:
            self.controller.ring_api.send_command_ring(self.ringalarm_device[DEVICE_ZID],
                                                       self.ringalarm_device[DEVICE_SOURCE],
                                                       'security-panel.switch-mode',
                                                       data={'mode': 'none', "bypass": None})
        except:
            pass

    def alarm_arm_home(self, code=None):
        """Send arm home command."""

        try:
            self.controller.ring_api.send_command_ring(self.ringalarm_device[DEVICE_ZID],
                                                       self.ringalarm_device[DEVICE_SOURCE],
                                                       'security-panel.switch-mode',
                                                       data={'mode': 'some', "bypass": None})
        except:
            pass

    def alarm_arm_away(self, code=None):
        """Send arm away command."""
        try:
            self.controller.ring_api.send_command_ring(self.ringalarm_device[DEVICE_ZID],
                                                       self.ringalarm_device[DEVICE_SOURCE],
                                                       'security-panel.switch-mode',
                                                       data={'mode': 'all', "bypass": None})
        except:
            pass

    def update_callback(self, data):
        try:
            if data[DEVICE_ALARM_MODE] == "none":
                self._state = STATE_ALARM_DISARMED
        except:
            pass
        try:
            if data[DEVICE_ALARM_MODE] == "some":
                self._state = STATE_ALARM_ARMED_HOME
        except:
            pass
        try:
            if data[DEVICE_ALARM_MODE] == "all":
                self._state = STATE_ALARM_ARMED_AWAY
        except:
            pass
        self.schedule_update_ha_state(True)

    @property
    def changed_by(self):
        """Last change triggered by."""
        return None

    @property
    def code_arm_required(self):
        """Whether the code is required for arm actions."""
        return True

    @property
    def state(self):
        """Get the state of the device."""
        return self._state
