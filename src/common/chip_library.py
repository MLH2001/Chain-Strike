from common.json_handler import JsonHandler
from common.chips import Chip

def load_all_chips() -> dict:
  """Load chips from json file"""
  chipObjs = JsonHandler.convert_data("chips.json")
  
  id = 0
  chipDict = {}
  for chip in chipObjs:
    chipDict[id] = chip
    id += 1
  return chipDict

class ChipLibrary:
  allChips = load_all_chips()

  @staticmethod
  def get_chip(id : int) -> Chip:
    """Return chip at a given id"""
    return ChipLibrary.allChips[id]
