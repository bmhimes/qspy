# Untested class.
from .BaseGenericObject import BaseGenericObject

class GenericDimension(BaseGenericObject):
  """This class corresponds to the "GenericDimension" class in the Qlik Engine JSON API.
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
    super().__init__(
      doc = doc,
      object_interface = object_interface
    )
    self.grouping = None
    self.field_definitions = None
    self.field_labels = None

  # Public attributes and methods.

  # Private attributes and methods.