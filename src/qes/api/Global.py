import json
from .Structs import ObjectInterface, DocListEntry
from .Doc import Doc
from .Response import Response

class Global:
  """
  This class corresponds to the "Global" class in the Qlik Engine JSON API.
  Methods from the Qlik Engine JSON API are converted to Python methods as follows:
    - separate words with underscores
    - lowercase all letters
  Parameters from the QLik Engine JSON API are converted to Python arguments as follows:
    - remove leading literal "q"
    - separate words with underscores
    - lowercase all letters
  """

  # Dunder methods.
  def __init__(self, qes):
    # Reference to parent class.
    self.qes = qes
    self.doc_list = DocList(global_env = self)

  # Public attributes and methods.
  def engine_version(self):
    self._initialize_request()
    self.qes.request.update({
      "method": "EngineVersion"
    })
    self.qes._sync_ws_send()

  def get_doc_list(self):
    print('Getting document list.')
    self._initialize_request()
    self.qes.request.update({
      "method": "GetDocList"
    })

    self.qes._sync_ws_send()
    self.doc_list = DocList(global_env = self)
    self.doc_list.update_from_doc_list_response(self.qes.response)

  def list_unpublished_docs(self):
    return list(filter(lambda doc: doc.meta.stream is None, self.doc_list))

  def list_published_docs(self):
    return list(filter(lambda doc: doc.meta.stream is not None, self.doc_list))

  def list_docs_by_stream_name(self, stream_name):
    return list(filter(lambda doc: getattr(doc.meta.stream, 'name', None) == stream_name, self.doc_list))

  def get_document_by_guid(self, guid):
    search_result = list(filter(lambda doc: doc.guid == guid, self.doc_list))
    result = None
    if len(search_result) == 1:
      result = search_result[0]
    return result

  def open_doc(self, doc_name, user_name = "", password = "", serial = "", no_data = False):
    """
    Opens an app. doc_name is the app GUID.
    """
    self._initialize_request()
    self.qes.request.update({
      "method": "OpenDoc",
      "params": {
        "qDocName": doc_name,
        "qUserName": user_name,
        "qPassword": password,
        "qSerial": serial,
        "qNoData": no_data
      }
    })
    self.qes._sync_ws_send()

    # Create object interface, which will construct or update the Doc object.
    object_interface = ObjectInterface(self.qes.response)

    # Check to see if object is already in DocList.
    doc = self.get_document_by_guid(doc_name)

    if doc is None:

      print('Creating new document.')

      # Create the Doc object.
      doc = Doc(self.qes, object_interface = object_interface)

      # Add the Doc to the DocList.
      self.doc_list.append(doc)

    else:

      print('Updating document with object interface.')

      # Update the Doc object with the ObjectInterface.
      doc.update_from_object_interface(object_interface)

    # Update the QlikSenseEngineService with the open document.
    self.qes.doc = doc

  # Private attributes and methods.
  def _initialize_request(self):
    self.qes._initialize_request()
    self.qes.request.update({
      "handle": self.qes.global_handle
    })

class DocList(list):

  def __init__(self, global_env):
    super().__init__()
    self.global_env = global_env

  def update_from_doc_list_response(self, doc_list_response):
    for entry in doc_list_response.result.qDocList:
      response = Response(json.dumps(entry))
      doc_list_entry = DocListEntry(response)
      doc = Doc(self.global_env.qes, doc_list_entry = doc_list_entry)
      self.append(doc)