import json
from common.file_handler import FileHandler
from common.graphics import *
from common.chips import Chip

def json_to_matrix(dict : dict) -> list:
  """Convert dictionary to matrix"""
  matrix = []
  row = []
  r = 0
  for key in dict.keys():
    current = int(key[0])
    if current != r:
      matrix.append(row)
      row = []
      r = int(key[0])
    row.append(dict[key])
  matrix.append(row)
  return matrix

###################################################################
#                         JsonHandler                             #
###################################################################

class JsonHandler:
  @staticmethod
  def convert_data(fileName : str) -> list:
    """Convert json file to list of objects"""
    filePath = FileHandler.get_packaged_files_path(fileName)
    with open(filePath, "r") as file:
      data = json.load(file)
    objs = []
    for key in data.keys():
      objDict = data[key]
      if objDict["type"] == 0:
        obj = JsonHandler.json_to_shape(objDict)
        objs.append(obj)
      elif objDict["type"] == 1:
        obj = JsonHandler.json_to_collage(objDict)
        objs.append(obj)
      elif objDict["type"] == 2:
        obj = JsonHandler.json_to_animation(objDict)
        objs.append(obj)
      elif objDict["type"] == 3:
        obj = JsonHandler.json_to_chip(objDict)
        objs.append(obj)
    return objs

  @staticmethod
  def json_to_shape(dict : dict) -> Shape:
    """Convert dictionary to Shape object"""
    id = dict["id"]
    vertices = dict["vertices"]
    color = dict["color"]
    width = dict["width"]
    shape = Shape(vertices, color, width, id)
    return shape

  @staticmethod
  def json_to_collage(dict : dict) -> Collage:
    """Convert dictionary to Collage object"""
    id = dict["id"]
    shapes = []
    for key in list(dict.keys())[2:]:
      shape = JsonHandler.json_to_shape(dict[key])
      shapes.append(shape)
    collage = Collage(shapes, id)
    return collage

  @staticmethod
  def json_to_animation(dict : dict) -> Animation:
    """Convert dictionary to Animation object"""
    id = dict["id"]
    frames = []
    skip = False
    for key in list(dict.keys())[2:]:
      frameDict = dict[key]
      if frameDict["type"] == 0:
        frame = JsonHandler.json_to_shape(frameDict)
      elif frameDict["type"] == 1:
        frame = JsonHandler.json_to_collage(frameDict)
      else:
        print("invalid frame detected")
        skip = True
      if not skip:
        frames.append(frame)
    animation = Animation(frames, id)
    return animation
  
  @staticmethod
  def json_to_chip(dict : dict) -> Chip:
    """Convert dictionary to Chip object"""
    # Covert chip asset
    assetDict = dict[str(0)]
    if assetDict["type"] == 0:
      asset = JsonHandler.json_to_shape(assetDict)
    elif assetDict["type"] == 1:
      asset = JsonHandler.json_to_collage(assetDict)
    elif assetDict["type"] == 2:
      asset = JsonHandler.json_to_animation(assetDict)
    
    #convert chip areaMatrix
    matrixDict = dict[str(1)]
    areaMatrix = json_to_matrix(matrixDict)

    chip = Chip(asset, areaMatrix)
    return chip