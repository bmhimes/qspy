import copy
import json
import random
import requests
import socket
import ssl
import string
import websocket
import sys

from .Request import Request
from .Response import Response
from .Global import Global as QlikSenseEngineServiceGlobal
from .Doc import Doc as QlikSenseEngineServiceDoc

class QlikSenseEngineService:
  """
  This class represents the Qlik Sense Engine Service (QES).
  """

  # The ID of the global handle.
  global_handle = -1

  def __init__(self, config, environment, user_directory = None, user_id = None, credential = None, password = None, app_guid = None):
    """
    Configures the client to make connections.
    """

    self.environment = environment

    self.server = config[environment]['server']
    self.port = config[environment]['qesListenPort']
    self.websocket_url = f'wss://{self.server}:{self.port}/app/'

    self.certificates = {
      'certfile': config[environment]['certLoc'] + '/client.pem',
      'keyfile': config[environment]['certLoc'] + '/client_key.pem',
      'ca_certs': config[environment]['certLoc'] + '/root.pem'
    }

    self.ssl_options = copy.deepcopy(self.certificates)
    self.ssl_options.update({
      'cert_reqs': ssl.CERT_REQUIRED,
      'server_side': False
      })
    ssl.match_hostname = lambda cert, hostname: True

    # Initialize user directory and user ID.
    if user_directory == None and user_id == None:
      user_directory = 'INTERNAL'
      user_id = 'sa_engine'
    self.user_directory = user_directory
    self.user_id = user_id

    self.headers = {
      'X-Qlik-User': f'UserDirectory={user_directory};UserId={user_id}',
      'Content-Type': 'application/json'
    }

    self.credential = credential
    self.password = password
    self.root = False
    self.app_guid = app_guid

    # Define API inner classes.
    self.request = None
    self.response = None
    self.global_env = None

    # Define the websocket internal properties.

    # Websocket object. Private.
    self._ws = None
    # Request sent over websocket. Private.
    self.request = None
    # Dict of response received over websocket. Private.
    self._ws_response = None
    # ID to use in QES requests. Private.
    self._engine_request_id = random.randint(1, 2**15)
    # Qlik Sense object handle ID. Private.
    self._handle = None
    # Handle type. Describes the class of the current handle. However, Global methods can be called with any handle.
    self._handle_type = None

  def _initialize_request(self):
    self.request = Request(
      handle = self._handle,
      method = "",
      params = {},
      out_key = -1,
      id = self._engine_request_id
    )

  def _ws_request(self):
    return str(self.request)

  def connect(self):
    try:
      self._ws = websocket.create_connection(
        self.websocket_url,
        sslopt = self.ssl_options,
        header = self.headers
      )
      response = self._ws.recv()
      self._handle_type = 'Global'
      print('Opened websocket connection.')
      # Global class of Qlik Engine JSON API.
      if self.global_env is None:
        self.global_env = QlikSenseEngineServiceGlobal(self)

    except websocket.WebSocketConnectionClosedException as e:
      print('\nException')
      print(e)

  def disconnect(self):
    if self._ws is not None:
      # This websocket method does not return a response.
      self._ws.close()
      print('Closed websocket connection.')
      self._handle_type = None

  def _sync_ws_send(self):
    # Initialize response.
    self.response = None
    # Send request over websocket.
    #print(self._ws_request())
    self._ws.send(self._ws_request())
    # The websocket returns a string. Convert it to a dict.
    self._ws_response = self._ws.recv()
    #print(self._ws_response)
    # Create reponse.
    self._generate_response_from_ws_recv()

  def _generate_response_from_ws_recv(self):
    '''Converts the websocket response JSON string into a Response object.'''
    self.response = Response(self._ws_response)

  def get_document_list(self):
    self.global_env.get_doc_list()

  def get_engine_version(self):
    self.global_env.engine_version()
    # Extract engine version string from response.
    self.engine_version = self._ws_response['result']['qVersion']['qComponentVersion']
    print(self.engine_version)

  def open_app(self, app_guid = None, no_data = False):
    if app_guid is None:
      if self.app_guid is not None:
        app_guid = self.app_guid
      else:
        raise RuntimeError('Application GUID undefined.')
    else:
      self.app_guid = app_guid
    self.global_env.open_doc(
      doc_name = self.app_guid,
      no_data = no_data
    )
    self._handle = self._ws_response['result']['qReturn']['qHandle']
    print(self._handle)
    self.handle_type = 'Doc'
    print(self._handle_type)
    self.doc = QlikSenseEngineServiceDoc(self)

  def open_app_without_data(self, app_guid = None):
    self.open_app(app_guid = app_guid, no_data = True)

  def reload(self, partial = False):
    self.doc.do_reload(partial = partial)

  def partial_reload(self):
    self.reload(partial = True)

  def save_app(self):
    self.doc.do_save()

  def get_script(self):
    self.doc.get_script()

  def download_script(self):
    self.doc.get_script()
    script = self._ws_response['result']['qScript']
    # QES returns the script as a Unicode string.
    with open("script.txt", "w", encoding = 'utf-8') as output_file:
      output_file.write(script)