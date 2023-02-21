from types import SimpleNamespace
from .Structs import AppScript, NxAppProperties
from .Response import Response

class GenericBookmark:
  """This class corresponds to the class in the Qlik Engine JSON API.

  Methods from the Qlik Engine JSON API are converted to Python methods as follows:
    - separate words with underscores
    - lowercase all letters
  Parameters from the Qlik Engine JSON API are converted to Python arguments as follows:
    - remove leading literal "q"
    - separate words with underscores
    - lowercase all letters

  If a method returns an object or property, that is converted into an attribute 
  of this object.
  """

  def __init__(self, qes, object_interface = None, nx_container_entry = None):
    self.qes = qes
    self.app_script = AppScript(empty = True)
    if object_interface is not None:
      print('Creating document from object interface.')
      self.guid = None
      self.type = None
      self.name = None
      self.data = None
      self.update_from_object_interface(object_interface)
    else:
      print('Creating document from nx container entry.')
      self._handle = None
      self.guid = nx_container_entry.id
      self.type = nx_container_entry.type
      self.name = nx_container_entry.name
      self.data = nx_container_entry.data

  def _initialize_request(self):
    self.qes._initialize_request()
    self.qes.request.update({
      "handle": self._handle
    })