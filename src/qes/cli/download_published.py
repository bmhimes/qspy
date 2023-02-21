from qspy.src.qes.process.ScriptDownloader import ScriptDownloader

if __name__ == '__main__':
  script_downloader = ScriptDownloader(environment = 'env', destination_path = 'C:\\temp', user_directory = 'AD', user_id = 'userid')

  script_downloader.download_published_scripts()