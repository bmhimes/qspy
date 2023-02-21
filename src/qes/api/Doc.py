from types import SimpleNamespace
from .Structs import AppScript, NxAppProperties
from .Response import Response

class Doc:
  """This class corresponds to the "Doc" class in the Qlik Engine JSON API.
  Methods from the Qlik Engine JSON API are converted to Python methods as follows:
    - separate words with underscores
    - lowercase all letters
  Parameters from the QLik Engine JSON API are converted to Python arguments as follows:
    - remove leading literal "q"
    - separate words with underscores
    - lowercase all letters

  If a method returns an object or property, that is converted into an attribute of this object.
  """

  # Dunder methods.
  def __init__(self, qes, object_interface = None, doc_list_entry = None):

    # Reference to parent class.
    self.qes = qes

    self.app_script = AppScript(empty = True)

    if object_interface is not None:

      print('Creating document from object interface.')

      # Initialize DocListEntry-derived attributes to None.
      self.guid = None
      self.connected_users = None
      self.file_time = None
      self.file_size = None
      self.meta = None
      #self.last_reload_time = None
      self.doc_name = None
      #self.thumbnail = None

      # Set attributes from ObjectInterface.
      self.update_from_object_interface(object_interface)

    else:

      print('Creating document from document list entry.')

      # Initialize ObjectInterface-derived attributes to None.
      self._handle = None

      # Set attributes from DocListEntry.
      self.guid = doc_list_entry.doc_id
      self.connected_users = doc_list_entry.connected_users
      self.file_time = doc_list_entry.file_time
      self.file_size = doc_list_entry.file_size
      self.meta = doc_list_entry.meta
      #self.last_reload_time = doc_list_entry.last_reload_time
      self.doc_name = doc_list_entry.doc_name
      #self.thumbnail = doc_list_entry.thumbnail

  # Public attributes and methods.
  def open(self, user_name = "", password = "", serial = "", no_data = False):
    self.qes.global_env.open_doc(self.guid, user_name, password, serial, no_data)

  def update_from_object_interface(self, object_interface):
    self._handle = object_interface.handle
    if self.guid is None:
      self.guid = object_interface.generic_id

  def generic_id(self):
    return self.guid

  def doc_id(self):
    return self.guid

  def do_reload(self, mode = 0, partial = False, debug = False):
    self._initialize_request()
    self.qes.request.update({
      "method": "DoReload",
      "params": {
        "qMode": mode,
        "qPartial": partial,
        "qDebug": debug
      }
    })
    self.qes._sync_ws_send()
    return

  def do_save(self, file_name = ""):
    self._initialize_request()
    self.qes.request.update({
      "method": "DoSave",
      "params": {
        "qFileName": file_name
      }
    })

  def evaluate(self, expression):
    """ Evaluates an expression and returns the result as a string. Evaluate method of Doc class."""

    self._initialize_request()
    self.qes.response.update({
      "method": "Evaluate",
      "params": {
        "qExpression": expression
      }
    })
    self.qes._sync_ws_send()
    return

  def evaluate_ex(self, expression):
    """Evaluates an expression and returns the result as  a dual. EvaluateEx method of Doc class."""

    self._initialize_request()
    self.qes.request.update({
      "method": "EvaluateEx",
      "params": {
        "qExpression": expression
      }
    })
    self.qes._sync_ws_send()

  def get_app_properties(self):
    """GetAppProperties method of Doc class."""

    self._initialize_request()
    self.qes.request.update({
      "method": "GetAppProperties"
    })
    self.qes._sync_ws_send()
    app_properties = NxAppProperties(self.qes.response)
    self.doc_name = app_properties.title
    self.description = app_properties.description

  def get_script(self):
    """GetScript method of Doc class."""

    self._initialize_request()
    self.qes.request.update({
      "method": "GetScript"
    })
    self.qes._sync_ws_send()
    # qScript contains the app script in Unicode.
    self.app_script = AppScript(response = self.qes.response)

  def set_script(self, script):
    """SetScript method of Doc class."""

    self._initialize_request()
    self.qes.request.update({
      "method": "SetScript",
      "qScript": script
    })
    self.qes._sync_ws_send()

  def update_remote_script(self):
    """Updates the Doc on the server with the script in this Doc object."""
    self.set_script(self.app_script.script)

  # Private attributes and methods.
  def _initialize_request(self):
    self.qes._initialize_request()
    self.qes.request.update({
      "handle": self._handle
    })