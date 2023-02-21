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
  def get_layout(self):
    self._initialize_request()
    self.qes.request.update({
      "method": "GetLayout"
    })
    self.layout = GenericObjectLayout(self.qes.response)

  # Private attributes and methods.
  def _initialize_request(self):
    self.qes._initialize_request()
    self.qes.request.update({
      "handle": self._handle
    })