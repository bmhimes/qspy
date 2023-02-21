# Untested class.
from .BaseGenericObject import BaseGenericObject
from .Response import Response

class GenericObject(BaseGenericObject):
  """This class corresponds to the "GenericObject" class in the Qlik Engine JSON API.
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

  # Public attributes and methods.

  # Private attributes and methods.