from common.json_handler import JsonHandler
from copy import deepcopy as deep_copy

class Save:
  attributes = JsonHandler.load_save("save.json")

  @staticmethod
  def attribute(name : str):
    return deep_copy(Save.attributes[name])

  @staticmethod
  def write():
    JsonHandler.store_save("save.json", Save.attributes)
