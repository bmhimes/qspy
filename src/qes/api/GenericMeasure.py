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
  def get_measure(self):
    self._initialize_request()
    self.qes.request.update({
      "method": "GetMeasure"
    })
    self.qes._sync_ws_send()
    measure = self.qes.response.qMeasure
    self.label = measure.qLabel
    self.definition = measure.qDef
    self.grouping = measure.qGrouping
    self.expressions = measure.qExpressions
    self.active_expression = measure.qActiveExpression
    self.label_expression = measure.qLabelExpression
    self.number_format = measure.qNumFormat

  # Private attributes and methods.