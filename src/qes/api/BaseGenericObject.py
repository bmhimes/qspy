# Untested class.
from .Response import Response
from .Structs import GenericObjectLayout

class BaseGenericObject:
  """This class contains the base of "GenericObject", "GenericDimension", and "GenericMeasure" classes in the Qlik Engine JSON API.
  Methods from the Qlik Engine JSON API are converted to Python methods as follows:
    - separate words with underscores
    - lowercase all letters
  Parameters from the Qlik Engine JSON API are converted to Python arguments as follows:
    - remove leading literal "q"
    - separate words with underscores
    - lowercase all letters

  If a method returns an object or property, that is converted into an attribute of this object.
  """

  # Dunder methods.
  def __init__(self, doc, object_interface = None):

    # Reference to parent class.
    self.doc = doc
    # Reference to QES.
    self.qes = self.doc.qes

    if object_interface is not None:
      self._handle = object_interface.handle
      self.type = object_interface.type
      self.generic_type = object_interface.generic_type
      self.id = object_interface.generic_id
    else:
      self._handle = None
      self.type = None
      self.generic_type = None
      self.id = None
    self.layout = None

  # Public attributes and methods.
  def approve(self):
    self._initialize_request()
    self.qes.request.update({
      "method": "Approve"
    })
    self.qes._sync_ws_send()

  def get_info(self):
    self._initialize_request()
    self.qes.request.update({
      "method": "GetInfo"
    })
    self.qes._sync_ws_send()
    self.id = self.qes.response.qInfo.qId
    self.type = self.qes.response.qInfo.qType

  def get_layout(self):
    self._initialize_request()
    self.qes.request.update({
      "method": "GetLayout"
    })
    self.qes._sync_ws_send()
    self.layout = GenericObjectLayout(self.qes.response)

  def publish(self):
    self._initialize_request()
    self.qes.request.update({
      "method": "Publish"
    })
    self.qes._sync_ws_send()

  def unapprove(self):
    self._initialize_request()
    self.qes.request.update({
      "method": "UnApprove"
    })
    self.qes._sync_ws_send()

  def unpublish(self):
    self._initialize_request()
    self.qes.request.update({
      "method": "UnPublish"
    })
    self.qes._sync_ws_send()

  #TODO: 
  # ApplyPatches
  # GetLinkedObjects
  # GetProperties
  # SetProperties

  # Private attributes and methods.
  def _initialize_request(self):
    self.qes._initialize_request()
    self.qes.request.update({
      "handle": self._handle
    })