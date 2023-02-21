import glob
from collections import defaultdict
import zipfile
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
from src.qes.api.QlikSenseEngineService import QlikSenseEngineService
from src.qes.config.qspy_config import ENVS

class ScriptDownloader:
  # storage_format: zip, folder, file
  def __init__(self, environment, destination_path = None, user_directory = None, user_id = None, app_guid = None, script_file_extension = 'qvs', storage_format = 'file')
    self.qes = QlikSenseEngineService(config = ENVS, environment = environment, user_directory = user_directory, user_id = user_id)
    self.environment = environment
    self.destination_path = destination_path
    self.user_directory = user_directory
    self.user_id = user_id
    self.app_guid = app_guid
    self.script_file_extension = script_file_extension
    self.storage_format = storage_format

  def download_unpublished_scripts(self):
    self.qes.connect()
    self.qes.global_env.get_doc_list()
    self.qes.disconnect()
    output_folder = os.path.join(self.destination_path, 'unpublished')
    os.makedirs(output_folder, exist_ok = True)
    doc_name_counter = defaultdict(int)
    archive_file_name = os.path.join(self.destination_path, f'{self.user_id}_{self.environment}_unpublished.zip')
    archive_file = zipfile.ZipFile(archive_file_name, 'w', zipfile.ZIP_DEFLATED)

    for doc in self.qes.global_env.list_unpublished_docs():
      # Get the document script.
      self.qes.connect()
      doc.open(no_data = True)
      doc.get_script()
      self.qes.disconnect()

      # Determine script file name.
      doc_name = doc.doc_name
      doc_name_counter[doc_name] += 1
      if doc_name_counter[doc_name] == 1:
        # Name file after document.
        file_name = f'{doc_name}.{self.script_file_extension}'
      else:
        # Rename file since ther are multiple documents with the same name.
        file_name = f'{doc_name}({doc_name_counter[doc_name] - 1}).{self.script_file_extension}'

      # Folder to hold script file before archiving.
      output_path = os.path.join(output_folder, file_name)

      # File path within archive.
      stored_path = os.path.join(self.user_id, self.environment, 'unpublished', file_name)

      # Write, store inside archive, and delete.
      with open(output_path, "w", encoding = 'utf-8') as output_file:
        output_file.write(doc.app_script.script)
      archive_file.write(output_path, arcname = stored_path)
      os.remove(output_path)

    archive_file.close()
    os.rmdir(output_folder)

  # TODO: figure out what causes error
  def download_published_scripts(self):
    self.qes.connect()
    try:
      self.qes.global_env.get_doc_list()
    finally:
      self.qes.disconnect()
    output_folder = os.path.join(self.destination_path, 'published')
    os.makedirs(output_folder, exist_ok = True)
    doc_name_counter = defaultdict(int)
    archive_file_name = os.path.join(self.destination_path, f'{self.user_id}_{self.environment}_published.zip')
    archive_file = zipfile.ZipFile(archive_file_name, 'w', zipfile.ZIP_DEFLATED)

    for doc in self.qes.global_env.list_published_docs():
      # Get the document script.
      self.qes.connect()
      try:
        doc.open(no_data = True)
        doc.get_script()

        # Determine script file name.
        doc_name = doc.doc_name
        stream_name = doc.meta.stream.name
        script_folder = os.path.join(output_folder)
        os.makedirs(script_folder, exist_ok = True)
        doc_name_counter[stream_name + '|' + doc_name] += 1
        if doc_name_counter[stream_name + '|' + doc_name] == 1:
          # Name file after document.
          file_name = f'{doc_name}.{self.script_file_extension}'
        else:
          # Rename file since there are multiple documents with the same name.
          file_name = f'{doc_name}({doc_name_counter[stream_name + '|' + doc_name] - 1}).{self.script_file_extension}'

        # Folder to hold script file before archiving.
        output_path = os.path.join(script_folder, file_name)

        # File path within archive.
        stored_path = os.path.join(self.user_id, self.environment, stream_name, file_name)

        # Write, store inside archive, and delete.
        with open(output_path, "w", encoding = 'utf-8') as output_file:
          output_file.write(doc.app_script.script)
        archive_file.write(output_path, arcname = stored_path)
        os.remove(output_path)
      except:
        print(self.qes.response)
      finally:
        self.qes.disconnect()

    archive_file.close()
    os.rmdir(output_folder)

  def download_scripts_from_stream(self, stream_name):
    self.qes.connect()
    try:
      self.qes.global_env.get_doc_list()
    finally:
      self.qes.disconnect()
    output_file = os.path.join(self.destination_path, 'stream')
    os.makedirs(output_folder, exist_ok = True)
    doc_name_counter = defaultdict(int)
    archive_file_name = os.path.join(self.destination_path, f'{self.user_id}_{self.environment}_{stream_name}.zip')
    archive_file = zipfile.ZipFile(archive_file_name, 'w', zipfile.ZIP_DEFLATED)
    for doc in self.qes.global_env.list_docs_by_stream_name(stream_name):
      # Get the document script.
      self.qes.connect()
      try:
        doc.open(no_data = True)
        doc.get_script()
      finally:
        self.qes.disconnect()

      # Determine script file name.
      doc_name = doc.doc_name
      stream_name = doc.meta.stream.name
      doc_name_counter[stream_name + '|' + doc_name] += 1
      if doc_name_counter[stream_name + '|' + doc_name] == 1:
        # Name file after document.
        file_name = f'{doc_name}.{self.script_file_extension}'
      else:
        # Rename file since there are multiple documents with the same name.
        file_name = f'{doc_name}({doc_name_counter[stream_name + '|' + doc_name] - 1}).{self.script_file_extension}'

      # Folder to hold script file before archiving.
      output_path = os.path.join(output_folder, file_name)

      # File path within archive.
      stored_path = os.path.join(file_name)

      # Write, store inside archive, and delete.
      with open(output_path, "w", encoding = 'utf-8') as output_file:
        output_file.write(doc.app_script.script)
      archive_file.write(output_path, arcname = stored_path)
      os.remove(output_path)

    archive_file.close()
    os.rmdir(output_folder)

  def download_app_script_by_guid(self, app_guid = None):

    # If an argument was not supplied, default to using the GUID from initialization.
    if app_guid is None:
      app_guid = self.app_guid

    try:
      self.qes.connect()
      self.qes.global_env.open_doc(app_guid)
      doc = self.qes.doc
      doc.get_script()
      doc.get_app_properties()

      output_folder = None
      if self.storage_format == 'zip':
        output_folder = os.path.join(self.destination_path, 'app')
      elif self.storage_format == 'file':
        output_folder = self.destination_path
      os.makedirs(output_folder, exist_ok = True)

      # Determine script file name.
      doc_name = doc.doc_name

      archive_file_name = os.path.join(self.destination_path, f'{self.user_id}_{self.environment}_{app_guid}.zip')

      archive_file = zipfile.ZipFile(archive_file_name, 'w', zipfile.ZIP_DEFLATED)

      # Name file after document.
      file_name = f'{doc_name}.{self.script_file_extension}'

      # Folder to hold script file before archiving.
      output_path = os.path.join(output_folder, file_name)

      # File path within archive.
      stored_path - os.path.join(file_name)

      # Write, store inside archive, and delete.
      with open(output_path, "w", encoding = 'utf-8') as output_file:
        output_file.write(doc.app_script.script)
      archive_file.write(output_path, arcname = stored_path)
      os.remove(output_path)

      archive_file.close()
      os.rmdir(output_folder)
    except:
      print(self.qes.response)
    finally:
      self.qes.disconnect()