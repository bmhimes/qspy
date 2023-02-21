import json
from types import SimpleNamespace

class Response(SimpleNamespace):
  """
  Constructs a Response object from a JSON string.
  Note that the string must use double quotes internally.
  Example: my_response = Response('{"jsonrpc": "2.0"}')
  """

  def __init__(self, json_string):

    json_dict = json.loads(json_string, object_pairs_hook=dict)

    self.response_keys = list(json_dict.keys())

    def convert_dict(value_obj, value_dict):

      for key in value_dict.keys():
        if type(value_dict[key]) != dict:
          setattr(value_obj, key, value_dict[key])
        else:
          if len(value_dict[key].keys()) > 0:
            setattr(value_obj, key, SimpleNamespace())
            convert_dict(getattr(value_obj, key), value_dict[key])
          else:
            setattr(value_obj, key, None)

    convert_dict(self, json_dict)     

  def __str__(self):
    ns_str = super().__str__()
    result = ns_str.replace('namespace', 'SimpleNamespace')
    return result