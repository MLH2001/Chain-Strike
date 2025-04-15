import os, sys

class FileHandler:
  @staticmethod
  def get_packaged_files_path(fileName):
    """Location of relative paths"""
    if getattr(sys, 'frozen', False):
      filePath = os.path.dirname(sys.executable)
    elif __file__:
      filePath = os.path.dirname(__file__)
    filePath = os.path.join(filePath, fileName)
    return filePath