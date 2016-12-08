import base64
import json
import requests
import pprint
from .xmldeserializer import deserialize


BASE_URL = 'https://e-api02.verisure.com/xbn/2/'

INSTALLATION_URL = BASE_URL + 'installation/{guid}/'
LOGIN_URL = BASE_URL + 'cookie'
LOGOUT_URL = BASE_URL + 'cookie'

GET_INSTALLATIONS_URL = BASE_URL + 'installation/search?email={username}'
OVERVIEW_URL = INSTALLATION_URL + 'overview'
SMARTPLUG_URL = INSTALLATION_URL + 'smartplug/state'
SET_ARMSTATE_URL = INSTALLATION_URL + 'armstate/code'
HISTORY_URL = INSTALLATION_URL + 'eventlog'
CLIMATE_URL = INSTALLATION_URL + 'climate/simple/search'
GET_LOCKSTATE_URL = INSTALLATION_URL + 'doorlockstate/search'
SET_LOCKSTATE_URL = INSTALLATION_URL + 'device/{deviceLabel}/{state}'

RESPONSE_TIMEOUT = 10

class Error(Exception):
    ''' Verisure session error '''
    pass

class RequestError(Error):
    ''' Wrapped requests.exceptions.RequestException '''
    pass

class LoginError(Error):
    ''' Login failed '''
    pass

class LoggedOutError(Error):
    ''' Login failed '''
    pass

class MaintenanceError(Error):
    ''' Login failed '''
    pass

class TemporarilyUnavailableError(Error):
    ''' Login failed '''
    pass

class ResponseError(Error):
    ''' Unexcpected response '''
    pass

class Session(object):
    """ Verisure app session """

    def __init__(self, username, password):
        self._username = username
        self._password = password
        self._vid = None
        self._giid = None
        self.installations = None

    def login(self):
        """ Login to verisure app api

        Login before calling any read or write commands

        """
        auth = 'Basic {}'.format(
                base64.b64encode(
                    'CPE/{username}:{password}'.format(
                    username=self._username,
                    password=self._password).encode('ascii')
                    ).decode('utf-8'))
        response = None
        try:
            response = requests.post(
                LOGIN_URL,
                headers={'Authorization': auth})
        except requests.exceptions.RequestException as ex:
            raise RequestError(ex)
        self.validate_response(response)
        self._vid = deserialize(response.text)[0].cookie
        self._get_installations()
        self._giid = self.installations[0].giid
    
    def validate_response(self, response):
        """ Verify that response is OK """
        if response.status_code == 200:
            return
        raise ResponseError(
            'Unable to validate response form My Pages'
            ', status code: {0} - Data: {1}'.format(
                response.status_code,
                response.text.encode('utf-8')))

    def _get_installations(self):
        """ Get information about installations """
        response=None
        try:
            response = requests.get(
                GET_INSTALLATIONS_URL.format(username=self._username),
                headers={'Cookie': 'vid={}'.format(self._vid)})
        except requests.exceptions.RequestException as ex:
            raise RequestError(ex)
        self.validate_response(response)
        self.installations = deserialize(response.text)

    def set_giid(self, giid):
        self._giid = giid
    
    def get_overview(self):
        """ Get overview for installation """
        response=None
        try:
            response = requests.get(
                OVERVIEW_URL.format(
                    guid=self._giid),
                headers={'Cookie': 'vid={}'.format(self._vid)})
        except requests.exceptions.RequestException as ex:
            raise RequestError(ex)
        self.validate_response(response)
        return deserialize(response.text)[0]

    def set_smartplug_state(self, device_label, state):
        response=None
        try:
            response = requests.post(
                SMARTPLUG_URL.format(
                    guid=self._giid),
                headers={
                    'Content-Type': 'application/json',
                    'Cookie': 'vid={}'.format(self._vid)},
                data=json.dumps([{"deviceLabel": device_label, "state": state}]))
        except requests.exceptions.RequestException as ex:
            raise RequestError(ex)
        self.validate_response(response)

    def set_arm_state(self, code, state):
        response=None
        try:
            response = requests.put(
                SET_ARMSTATE_URL.format(
                    guid=self._giid),
                headers={
                    'Content-Type': 'application/json',
                    'Cookie': 'vid={}'.format(self._vid)},
                data=json.dumps({"code": str(code), "state": state}))
        except requests.exceptions.RequestException as ex:
            raise RequestError(ex)
        self.validate_response(response)

    def get_history(self, pagesize, offset, *filters):
        response=None
        try:
            response = requests.get(
                HISTORY_URL.format(
                    guid=self._giid),
                headers={
                    'Cookie': 'vid={}'.format(self._vid)},
                params={
                    "offset": int(offset),
                    "pagesize": int(pagesize)})
        except requests.exceptions.RequestException as ex:
            raise RequestError(ex)
        self.validate_response(response)
        return deserialize(response.text)[0]

    def get_climate(self, device_label):
        response=None
        try:
            response = requests.get(
                CLIMATE_URL.format(
                    guid=self._giid),
                headers={
                    'Cookie': 'vid={}'.format(self._vid)},
                params={
                    "deviceLabel": device_label})
        except requests.exceptions.RequestException as ex:
            raise RequestError(ex)
        self.validate_response(response)
        return deserialize(response.text)[0]
    
    def get_lockstate(self):
        response=None
        try:
            response = requests.get(
                GET_LOCKSTATE_URL.format(
                    guid=self._giid),
                headers={
                    'Cookie': 'vid={}'.format(self._vid)})
        except requests.exceptions.RequestException as ex:
            raise RequestError(ex)
        self.validate_response(response)
        return deserialize(response.text)[0]

    def set_lockstate(self, code, device_label, state):
        response=None
        try:
            response = requests.put(
                GET_LOCKSTATE_URL.format(
                    guid=self._giid,
                    device_label=device_label,
                    state=state
                    ),
                headers={
                    'Cookie': 'vid={}'.format(self._vid)},
                data=json.dumps({"code": str(code)}))
        except requests.exceptions.RequestException as ex:
            raise RequestError(ex)
        self.validate_response(response)
        return deserialize(response.text)[0]

    def logout(self):
        response=None
        try:
            response = requests.delete(
                LOGOUT_URL,
                headers={
                    'Cookie': 'vid={}'.format(self._vid)}
                )
        except requests.exceptions.RequestException as ex:
            raise RequestError(ex)
        self.validate_response(response)
