import json
import logging
import numpy as np
import pandas as pd
import requests
import socketio
from pandas.io.json import json_normalize

from .constants import *

pd.set_option('display.max_columns', 500)  # or 1000
pd.set_option('display.max_rows', 100)  # or 1000
pd.set_option('display.max_colwidth', -1)  # or 199

_LOGGER = logging.getLogger(__name__)

_ringalarm_devices = pd.DataFrame()
ringalarm_devices_list = []

required_columns = [DEVICE_ZID, DEVICE_NAME, DEVICE_BATTERY_STATUS, DEVICE_BATTERY_LEVEL, DEVICE_TYPE, \
                    DEVICE_ROOM_ID, DEVICE_TAMPER_STATUS, \
                    DEVICE_ON, DEVICE_MOTION_STATUS, DEVICE_FAULTED, \
                    DEVICE_CONTROLLER, DEVICE_MAPPED_TYPE, DEVICE_SOURCE, DEVICE_LOCKED, DEVICE_CALLBACK]

custom_columns = [DEVICE_CONTROLLER, DEVICE_MAPPED_TYPE, DEVICE_SOURCE, DEVICE_CALLBACK]

class RingLocations(object):
    def __init__(self, username, password):
        # , **kwargs):
        self.username = username
        self.password = password
        self.is_connected = False
        self.token = None
        self.params = None
        self.asset_devices_present = None
        self.total_hubs = 0
        self.hubs_devices_obtained = 0
        self.locations = []
        self.location_id = None
        self.token = self._get_oauth_token()
        self.sio=None
        if (self.token):
            self.is_connected = True

    def set_callbacks(self, **kwargs):
        self.async_add_device_callback = kwargs.get('async_add_device')
        self.async_update_device_callback = kwargs.get('async_update_device')

    def _get_oauth_token(self):
        data = {'username': self.username, 'grant_type': 'password', 'scope': 'client',
                'client_id': 'ring_official_android', 'password': self.password}
        response = requests.post(OATH_ENDPOINT, data=data)
        statusCode = response.status_code
        oauth_token = None
        responseJSON = response.json()
        if statusCode == 200:
            oauth_token = responseJSON.get('access_token', None)
            _LOGGER.info("Oauth Token obtained")
        return oauth_token

    def get_locations(self):
        data = {}
        headers = {'content-type': 'application/x-www-form-urlencoded', 'authorization': 'Bearer ' + self.token}
        response = requests.get(LOCATIONS_ENDPOINT, data=data, headers=headers).json()
        user_locations = response.get('user_locations', None)
        _LOGGER.info("User locations are " + str(user_locations))
        return user_locations

    def send_command_ring(self, zid, dst, cmd, data={}):
        _payload = {
            "body": [
                {
                    "zid": zid,
                    "command": {
                        "v1": [
                            {
                                "commandType": cmd,
                                "data": data
                            }
                        ]
                    }
                }
            ],
            "datatype": "DeviceInfoSetType",
            "dst": dst,
            "msg": "DeviceInfoSet",
            "seq": 3
        }
        self.sio.emit("message", _payload)

    def get_devices(self, location_id):
        hubs = RingHubs(location_id, self.token)
        self.sio = socketio.Client()
        self.sio.connect(hubs.wss_url, transports='websocket')
        for hub in hubs.assets:
            asset = hub.get('uuid', None)
            self.total_hubs = self.total_hubs + 1
            initial_request_get_device_list = {"msg": "DeviceInfoDocGetList", "dst": asset, "seq": 2}
            self.sio.emit("message", initial_request_get_device_list)
        _LOGGER.info("Total hubs " + str(self.total_hubs))

        @self.sio.event
        def SessionInfo(data):
            # print(json.dumps(data, indent=4))
            pass

        @self.sio.event
        def DeviceInfoSet(data):
            pass

        @self.sio.event
        def DataUpdate(data):

            # print(json.dumps(data, indent=4))
            if data["datatype"] == 'HubDisconnectionEventType':
                print ("Hub is is disconnected")
            try:
                if data["datatype"] == "DeviceInfoDocType":
                    # print(json.dumps(data, indent=4))
                    entity_dict = {}
                    if self.async_update_device_callback:
                        updated_entities = _build_update_entity_list(data)
                        # print ("Updates","-->", updated_entities[DEVICE_ZID],updated_entities[DEVICE_NAME])
                        self.async_update_device_callback(updated_entities)
            except KeyError:
                pass

        @self.sio.event
        def message(data):
            # print ("DATA IS ", data)
            # print(json.dumps(data, indent=4))
            if data['msg'] == 'DeviceInfoSet':
                pass
            else:
                try:
                    if data["datatype"] == "DeviceInfoDocType":
                        global ringalarm_devices_list
                        _build_initial_entity_list(data)
                        self.hubs_devices_obtained = self.hubs_devices_obtained + 1
                        if self.hubs_devices_obtained == self.total_hubs:
                            r = pd.DataFrame()
                            for i in ringalarm_devices_list:
                                r = pd.concat([r, i], ignore_index=True, sort=False)
                            if (self.async_add_device_callback):
                                self.async_add_device_callback(r)
                except KeyError:
                    pass


class RingHubs(object):
    hubsList = []

    def __init__(self, location_id, oath_token):
        data = {}
        HUB_HEADERS = {'content-type': 'application/x-www-form-urlencoded', 'authorization': 'Bearer ' + oath_token,
                       'user-agent': 'android:com.ringapp:2.0.67(423)'}
        response = requests.get(HUB_ENDPOINT + location_id, data=data, headers=HUB_HEADERS).json()
        self.host = response.get('host', None)
        self.ticket = response.get('ticket', None)
        self.assets = response.get('assets', None)
        self.wss_url = "wss://" + self.host + "/?authcode=" + self.ticket + "&ack=false&EIO=3"
        for asset in self.assets:
            self.hubsList.append({"uuid": asset.get('uuid', None), "doorbotId": asset.get('doorbotId', None),
                                  "kind": asset.get('kind', None), "onBattery": asset.get('onBattery', None),
                                  "status": asset.get('status', None)})


def _build_initial_entity_list(received_data):
    _hubID = received_data['src']
    ringalarm_devices = json_normalize(received_data['body'])
    ringalarm_devices.loc[:, DEVICE_SOURCE] = _hubID
    ringalarm_devices_list.append(ringalarm_devices)


def _build_update_entity_list(received_data):
    _hubID = received_data['src']
    updated_devices = json_normalize(received_data['body'])
    return updated_devices
