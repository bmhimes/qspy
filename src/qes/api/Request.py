import json

class Request:
  def __init__(self, handle = None, method = None, params = {}, out_key = None, id = None):
    self.handle = handle
    self.method = method
    self.params = params
    self.out_key = out_key
    self.id = id

  def update(self, update_dict):
    for updated_key in update_dict:
      setattr(self, updated_key, update_dict[updated_key])

  def __repr__(self):
    method = f"'{self.method}'"
    if self.method is None:
      method = 'None'
    return f"{self.__class__.__name__}(handle = {self.handle}, method = {method}, params = {self.params}, out_key = {self.out_key}, id = {self.id})"

  def __str__(self):
    request_dict = {
      "method": self.method,
      "handle": self.handle,
      "params": self.params,
      "outKey": self.out_key,
      "id": self.id
    }
    return json.dumps(request_dict)