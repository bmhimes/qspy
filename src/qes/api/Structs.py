import copy
import re
import inspect
from .Response import Response
from types import SimpleNamespace
import json

#TODO generate classes from schema

# Method for creating default Struct key getter.
def create_getter(prop):
  # Getter function object configured for a specific Struct key.
  def getter(self):
    return getattr(self, f"_{prop}")
  return getter

# Method for creating default Struct key setter.
def create_setter(prop):
  # Setter function object configured for a specific Struct key.
  def setter(self, value):
    setattr(self, f"_{prop}", value)
  return setter

# Method for creating default Struct key deleter.
def create_deleter(prop):
  # Deleter function object configured for a specific Struct key.
  def deleter(self):
    delattr(self, f"_{prop}")
  return deleter

def convert_response_key_to_property(response_key):

  # Initialize property name.
  property_name = response_key

  # Put underscore in front of each capital letter.
  property_name = re.sub(pattern = r'([A-Z])', repl = '_\\1', string = property_name)

  # Remove leading 'q_'.
  property_name = re.sub(pattern = r'^(q_)', repl = '', string = property_name)

  # Lowercase letters.
  property_name = property_name.lower()

  # Handle reserved keywords.
  if property_name in ['return']:
    property_name = property_name + '_'

  return property_name

class Struct(SimpleNamespace):
  """
  A Struct is created from a Response or by directly setting properties.
  This base class is not intended to be used directly.
  The concrete subclass is responsible for defining:
    - response_struct_keys
    - struct_keys
  """
  def __init__(self, response_struct_keys, struct_keys = None, response = None, result_key = None, empty = False):

    # Validate input.

    # Validate response Struct keys.
    assert (type(response_struct_keys) == list), "response_struct_keys argument must be a list."
    assert (len(response_struct_keys) > 0), "response_struct_keys argument must have list values."
    for i in range(0, len(response_struct_keys)):
      assert(type(str(response_struct_keys[i])) == str), f"response_struct_keys value must be convertible to strings. Type of value in response is {type(response_struct_keys[i])}."
    assert(type(empty) == bool), "empty argument must be a boolean value."

    # If empty == False, we are creating the Struct directly from a Response.
    # Ensure that all required arguments are present.
    if empty == False:
      assert (response is not None), f"response argument must be supplied if {self.__class__.__name__} is not empty."
      assert (type(response) == Response), "response argument must be a Response object."
      if result_key is not None:
        assert (type(str(result_key)) == str), "result_key argument must be a string."
      if struct_keys is not None:
        assert (type(struct_keys) == list), "struct_keys argument must be a list."
        assert (len(struct_keys) > 0), "struct_keys argument must have list values."
        for i in range(0 len(response_struct_keys)):
          assert (type(str(struct_keys[i])) == str), f"struct_keys value must be convertible to strings. Type of value in struct_keys[{i}] is {type(struct_keys[i])}."
        if empty == True:
          assert (response is None), f"response argument must be None if {self.__class__.__name__} is empty."

    # Validate Response data.
    if empty == False:
      if type(self)._response_substruct == False:
        assert (hasattr(response, 'result')), "response does not have result attribute."
        if result_key is not None:
          assert (hasattr(response.result, result_key)), f"response result does not have any {result_key}, per result_key argument."
        for response_struct_key in response_struct_keys:
          assert_return_value = None
          if result_key is not None:
            assert_return_value = getattr(response.result, result_key)
          elif type(self)._response_substruct == False:
            assert_return_value = response.result
          else:
            assert_return_value = response
          assert (hasattr(assert_return_value, response_struct_key)), f"{result_key} in Response result does not have response_struct_key attribute."

    # Holds the Response used to create the Struct, if any.
    self.response = response

    # Holds the key to the Response result.
    self.result_key = result_key

    # Holds the keys to the Response.
    self.response_struct_keys = response_struct_keys

    # Holds the keys to the specific properties of the Struct.
    # Test if struct_keys was supplied.
    if struct_keys is not None:
      # Assign value from argument.
      self.struct_keys = struct_keys
    else:
      # Generate Struct keys from response Struct keys.
      self.struct_keys = [convert_response_key_to_property(key) for key in response_struct_keys]


    # Initialize properties, depending on using a Response or creating the object manually.
    # Name the return value of the response to reduce aliasing.
    return_value = None
    if empty == False:
      if self.result_key is not None:
        return_value = getattr(resonse.result, result_key)
      elif type(self)._response_substruct == False:
        return_value = response.result
      else:
        return_value = response

    def convert_dict(value_obj, value_dict):

      for key in value_dict.keys():

        if type(value_dict[key]) != SimpleNamespace:
          setattr(value_obj, prop_key, value_dict[key])

        else:
          setattr(value_obj, prop_key, SimpleNamespace())
          convert_dict(getattr(value_obj, prop_key), value_dict[key].__dict__)

    if empty == False:
      convert_dict(self, return_value.__dict__)
    else:
      for key in self.struct_keys:
        prop_key = convert_response_key_to_property(key)
        setattr(self, prop_key, None)

    """
    # Initialize instance Struct key values.
    for key_index in range(0, len(self.struct_keys)):

      # Get property name, based on response key.
      property_name = self.struct_keys[key_index]

      # Initialize property value.
      property_value = None

      # If Struct is not empty, get property value from response.
      if empty == False:
        property_value = return_value[self.response_struct_keys[key_index]]

      # Set the property value.
      setattr(self, property_name, property_name)
    """

ConcreteStructSubclasses = []

def ConcreteStruct(cls):
  """
  Applies dynamic, class-specific logic to each concrete subclass of Struct.
  The assumption is that each Struct key will be defined as property within the subclass
  if any there needs to be a custom getter, setter, or deleter for that Struct key.
  Any getters, setters, and deleters not already defined for Struct keys by the end of
  subclass initialization will be automatically defined.
  The decorated class name is added to ConcreteStructSubclasses.
  """

  # Validate class.
  assert (cls.response_struct_keys is not None), f"{cls.__name__} class does not have response Struct keys defined."
  assert (type(cls.response_struct_keys) == list), f"response_struct_keys type is {type(cls.response_struct_keys)} but should be a list."
  assert (len(cls.response_struct_keys) > 0), f"response_struct_keys must have entries defined."
  if hasattr(cls, '_use_default_init') == True:
    assert (type(cls._use_default_init) == bool), "_use_default_init must be a boolean value."

  # Initialize _use_default_init
  if hasattr(cls, '_use_default_init') == False:
    setattr(cls, '_use_default_init', True)

  # Initialize _response_substruct
  if hasattr(cls, '_response_substruct') == False:
    setattr(cls, '_response_substruct', False)

  # Initialize the Struct keys for the class.
  cls.struct_keys = []

  # Iterate through the response Struct keys for the class.
  for response_struct_key in cls.response_struct_keys:

    # Convert response Struct key into Pythonic name.
    property_name = convert_response_key_to_property(response_struct_key)

    # Add property name to class Struct keys.
    cls.struct_keys.append(property_name)

    # Generate default doc_string.
    default_doc_string = f"Struct key property '{property_name}' created from result.{cls.result_key}.{response_struct_key}."

    # Check to see if Struct key has already been defined for the class.
    if not hasattr(cls, property_name):

      # Create the Struct key property from scratch.
      setattr(cls, property_name, property(fget = create_getter(property_name), fset = create_setter(property_name), fdel = create_deleter(property_name)))
      #print(f"Created property {property_name} from {response_struct_key} from scratch for {cls.__name__}.")

      # def default_attribute(self):
      # return getattr(self, property_name)
      # setattr(cls, property_name, default_attribute)

    else:

      # Ensure that previously defined Struct key is a property.
      assert (type(getattr(cls, property_name)) == property), f"All Struct keys mst be type property, but {property_name} is type {type(getattr(cls, property_name))}."

  # Define the default initializer.
  if cls._use_default_init == True:

    def default_initializer(self, response = None, empty = False):
      super(cls, self).__init__(
        response_struct_keys = cls.response_struct_keys,
        struct_keys = cls.struct_keys,
        response = response,
        result_key = cls.result_key,
        empty = empty
      )

    setattr(cls, '__init__', default_initializer)

  # Add class name to ConcreteStructSubclasses.
  ConcreteStructSubclasses.append(cls.__name__)

@ConcreteStruct
class AppScript(Struct):
  """
  Qlik Engine JSON API class reference:
  """
  response_struct_keys = ['qScript', 'qMeta']
  result_key = 'qScript'
  _use_default_init = False

  def __init__(self, response = None, empty = False):
    init_response = None
    if empty == False:
      # If the response came from a GetScript call, restructure the response to match
      # the response of a GetScriptEx call.
      if hasattr(response.result.qScript, 'qMeta') == False:
        init_response = response
        init_response.result.qScript = SimpleNamespace(
          qScript = resonse.result.qScript,
          qMeta = None
        )
      else:
        init_response = response
    super().__init__(
      response_struct_keys = AppScript.response_struct_keys,
      struct_keys = AppScript.struct_keys,
      response = init_response,
      result_key = AppScript.result_key,
      empty = empty
    )
    if empty == False:
      # Replace new lines to work correctly on all systems.
      self.script = self.script.replace('\r\n', '\n')
      self._generate_sections()
    else:
      # Initialize sections as empty list.
      self.sections = list()

  @property
  def script(self):
    return self._script

  @script.setter
  def script(self, value):
    if value is not None:
      self._script = value.replace('\r\n', '\n')
      self._generate_sections()

  def insert_section(self, name = None, content = '', before_position = 'END')
    if name == None:
      name = AppScriptSection.default_name
    section = AppScriptSection(name = name, content = content)
    if type(before_position) == int:
      self.sections.insert(before_position, section)
    elif before_position.upper() == 'END':
      self.sections.append(section)
    self._rebuild_script_from_sections()
    self._generate_sections()

  def delete_section_by_id(self, id):
    self.sections.pop(id)
    self._rebuild_script_from_sections()
    self._generate_sections()

  def _generate_sections(self):

    self.sections = list()
    section_start_indexes = [m.start() for m in re.finditer(AppScriptSection.header_code.replace("$", r"\$"), self.script)]
    section_count = len(section_start_indexes)

    for section_index in range(0, section_count):
      section_start_index = section_start_indexes[section_index]
      section_end_index = None
      if section_index != section_count - 1:
        section_end_index = section_start_indexes[section_index + 1] - 1 # subtract 1 for the new line that is used to join sections.
      else:
        section_end_index = len(self.script)

      # The section name is the series of characters between the app script section header code and the end of the line.
      section_name_match = re.search('(?<=' + AppScriptSection.header_code.replace("$", r"\$") + ').*(?=\n)', self.script[section_start_index])
      section_name = section_name_match.group(0)
      section_name_end_index = section_start_index + section_name_match.end(0) + 1
      section_content = self.script[section_name_end_index:section_end_index]

      self.sections.append(AppScriptSection(
        name = section_name,
        content = section_content,
        app_script_object = self,
        start_index = section_start_index,
        end_index = section_end_index
      ))

  def _rebuild_script_from_sections(self):
    self._script = '\n'.join(str(section) for section in self.sections)

class AppScriptSection:
  """Section of an app script. This does not correspond to a JSON API struct."""

  # This code tells Qlik Sense that a new app script section is beginning.
  header_code = '///$tab ' # 8 characters.

  # This is the default section name assigned by Qlik Sense.
  default_name = 'Section'

  def __init__(self, name = None, content = '\n', app_script_object = None, start_index = None, end_index = None):
    self.app_script = app_script_object
    if name is not None:
      if type(name) != str:
        raise ValueError('name must be a string.')
      if type(content) != str:
        raise ValueError('content must be a string.')
      if len(name.strip()) > 0:
        self._name = name
      else:
        self._name = self.default_name
        print('Pure white space is not a valid section name. Changing section name to default.')
    else:
      self._name = self.default_name
    self.content = content
    if self.app_script is not None:
      start_index >= end_index:
        raise ValueError('start_index is equal to or greater than end_index. Indexes are invalid.')
      if end_index - start_index < len(self.header_code) + 3:
        raise ValueError(f'Lenght of string implied by end_index - start_index ({end_index - start_index}) is less than the minimum possible length.')
      if start_index < 0:
        raise ValueError('start_index must be non-negative.')
      if end_index < 0:
        raise ValueError('end_index must be non-negative.')
      index_implied_length = end_index - start_index
      string_implied_length = len(self.header_code) + len(self.name) + len('\n') + len(self.content)
      if index_implied_length != string_implied_length:
        print(self.app_script.script)
        print(f"name: {self._name}")
        print(f"content: {self.content}")
        raise ValueError(f'Length of string implied by end_index - start_index ({index_implied_length})  does not match length of section string.')
      self.start_index = start_index
      self.end_index = end_index
    else:
      if start_index is not None:
        raise ValueError('start_index is only valid in relation to an AppScript object, per app_script_object argument.')
      if end_index is not None:
        raise ValueError('end_index is only valid in relation to an AppScript object, per app_script_object argument.')
      self.start_index = None
      self.end_index = None

  def __str__(self):
    return self.header_code + self._name + '\n' + self._content

  def _update_app_script(self):
    #self.app_script._rebuild_script_from_sections()
    pass

  @property
  def name(self):
    return self._name

  @name.setter
  def name(self, value):
    if len(value.strip()) == 0:
      raise ValueError("Section name cannot contain only white space.")
    self._x = value
    if self.app_script is not None:
      self._update_app_script()

  @property
  def content(self):
    return self._content

  @content.setter
  def content(self, value):
    # Replace new lines to work correctly on all systems.
    value = value.replace('\r\n', '\n')
    self._content = value
    if self.app_script is not None:
      self._update_app_script()

@ConcreteStruct
class ObjectInterface(Struct):
  """
  Qlik Engine JSON API class reference:
  """
  response_struct_keys = ['qType', 'qHandle', 'qGenericId', 'qGenericType']
  result_key = 'qReturn'
  _use_default_init = False

  def __init__(self, response = None, empty = False):
    init_response_struct_keys = copy.deepcopy(type(self).response_struct_keys)
    init_struct_keys = copy.deepcopy(type(self).struct_keys)
    if empty == False and type(response) == Response:
      if response.result.qReturn.qType == 'Doc':
        # The 'qGenericType' key is not present when the object is an app.
        init_response_struct_keys.remove('qGenericType')
        init_struct_keys.remove(convert_response_key_to_property('qGenericType'))

    super().__init__(
      response_struct_keys = init_response_struct_keys,
      struct_keys = init_struct_keys,
      response = response,
      result_key = type(self).result_key,
      empty = empty
    )

@ConcreteStruct
class DocListEntry(Struct):
  """
  Qlik Engine JSON API class reference:
  """

  # qReadOnly is excluded because testing did not actually return that key.
  # qLastReloadTime only exists if document has been reloaded.
  response_struct_keys = ['qDocName', 'qConnectedUsers', 'qFileTime', 'qFileSize', 'qDocId', 'qMeta', 'qTitle']
  result_key = None
  _use_default_init = True
  _response_substruct = True

@ConcreteStruct
class NxContainerEntry(Struct):
  """
  Qlik Engine JSON API class reference:
  """
  response_struct_keys = ['qId', 'qType', 'qName', 'qData']
  result_key = None
  _use_default_init = False
  _response_substruct = True

  def __init__(self, response = None, empty = False):
    if not empty and type(response) == Response:
      if hasattr(response, 'qInfo'):
        response.qId = response.qInfo.qId
        response.qType = response.qInfo.qType
      if hasattr(response, 'qMeta'):
        response.qName = response.qMeta.qName
    super().__init__(NxContainerEntry.response_struct_keys, response = response, empty = empty)

@ConcreteStruct
class AlternateStateData(Struct):
  """
  Qlik Engine JSON API class reference:
  """
  response_struct_keys = ['qStateName', 'qFieldItems']
  result_key = None
  _use_default_init = False
  _response_substruct = True

  def __init__(self, response = None, empty = False):
    super().__init__(AlternateStateData.response_struct_keys, response = response, empty = empty)

class AlternateStateDataList(list):

  def update_from_response(self, response):
    for item in response.qStateData:
      self.append(AlternateStateData(Response(json.dumps(item))))

class FieldValueList(list):

  def update_from_response(self, response):
    for item in response.qFieldValues:
      self.append(FieldValue(Response(json.dumps(item))))

class BookmarkFieldItemList(list):

  def update_from_response(self, response):
    for item in reponse.qFieldItems:
      self.append(BookmarkFieldItem(Response(json.dumps(item))))

class ObjectList(list):
  pass

class SheetList(list):
  pass

class DimensionList(list):
  pass

class MeasureList(list):
  pass

@ConcreteStruct
class BookmarkFieldItem(Struct):
  """
  Qlik Engine JSON API class reference:
  """
  response_struct_keys = ['qValues', 'qExcludedValues']
  result_key = None
  _use_default_init = False
  _response_substruct = True

  def __init__(self, response = None, empty = False):
    super().__init__(BookmarkFieldItem.response_struct_keys, response = response, empty = empty)

@ConcreteStruct
class FieldValue(Struct):
  """
  Qlik Engine JSON API class reference:
  """
  response_struct_keys = ['qText', 'qIsNumeric', 'qNumber']
  result_key = None
  _use_default_init = False
  _response_substruct = True

  def __init__(self, response = None, empty = False):
    if not empty and type(response) == Response:
      if not hasattr(response, 'qText'):
        response.qText = None
      if not hasattr(response, 'qNumber'):
        response.qNumber = None
      if not hasattr(response, 'qIsNumeric'):
        response.qIsNumeric = None
      if response.qNumber == 'NaN' and response.qIsNumeric == None:
        response.isNumeric = False
    super().__init__(FieldValue.response_struct_keys, response = response, empty = empty)

@ConcreteStruct
class NxAppProperties(Struct):
  """
  Qlik Engine JSON API class reference:
  """
  response_struct_keys = ['qTitle', 'description']
  result_key = 'qProp'
  _use_default_init = True
  _response_substruct = False

@ConcreteStruct
class NxEngineVersion(Struct):
  """
  Qlik Engine JSON API class reference:
  """
  response_struct_keys = ['qComponentVersion']
  result_key = 'qVersion'

@ConcreteStruct
class GenericObjectLayout(Struct):
  """
  Qlik Engine JSON API class reference: https://help.qlik.com/en-US/sense-developer/May2022/Subsystems/EngineJSONAPI/Content/models-genericobjectlayout.htm
  """
  response_struct_keys = ['qInfo', 'qMeta', 'qExtendsId', 'qHasSoftPatches', 'qError', 'qSelectionInfo', 'qStateName']
  result_key = None
  _use_default_init = True
  _response_substruct = False