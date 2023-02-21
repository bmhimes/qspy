# Untested class.
from .BaseGenericObject import BaseGenericObject

class GenericMeasure(BaseGenericObject):
  """This class corresponds to the "GenericMeasure" class in the Qlik Engine JSON API.
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
    self.label = None
    self.definition = None
    self.grouping = None
    self.expressions = None
    self.active_expression = None
    self.label_expression = None
    self.number_format = None

  # Public attributes and methods.

  # Private attributes and methods.