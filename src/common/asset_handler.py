from copy import deepcopy as deep_copy
from common.json_handler import JsonHandler
from common.graphics import *

###################################################################
#                      General Helpers                            #
###################################################################

def load_all_assets() -> dict:
  """Convert json file to objects in dict"""
  assets = JsonHandler.convert_data("assets.json")
  assetDict = {}
  for asset in assets:
    assetDict[asset.id] = asset
  return assetDict

def ref_point(frame : Asset) -> tuple:
  """Find the reference point of an asset"""
  if isinstance(frame, Shape):
    refPoint = frame.vertices[0]
    return refPoint
  elif isinstance(frame, Collage):
    refPoint = frame.shapes[0].vertices[0]
    return refPoint
  else:
    return (0, 0)

def shape_size(asset : Shape) -> tuple:
  """Find the size of an asset"""
  xMin, yMin = [1000000] * 2
  xMax, yMax = [-1] * 2
  for point in asset.vertices:
    if point[0] < xMin:
      xMin = point[0]
    if point[0] > xMax:
      xMax = point[0]
    if point[1] < yMin:
      yMin = point[1]
    if point[1] > yMax:
      yMax = point[1]
  return (xMax - xMin), (yMax - yMin)

def animation_size(asset : Animation) -> tuple:
  """Find the size of an Animation"""
  widthMax, heightMax = [-1] * 2
  for frame in asset.frames:
    width, height = AssetHandler.get_size(frame)
    if width > widthMax:
      widthMax = width
    if height > heightMax:
      heightMax = height
  return widthMax, heightMax

###################################################################
#                        Color Helpers                            #
###################################################################

def color_collage(asset : Collage, color : tuple, id : str) -> None:
  """Color a given component of a Collage a given color"""
  component = asset.get_component(id)
  for shapeIndex in component:
    shape = asset.shapes[shapeIndex]
    newShape = AssetHandler.color(shape, color, id)
    asset.update_shape(newShape, shapeIndex)

def color_animation(asset : Animation, color : tuple, id : str) -> None:
  """Color a given component of an Animation a given color"""
  index = 0
  for frame in asset.frames:
    newFrame = AssetHandler.color(frame, color, id)
    asset.update_frame(newFrame, index)
    index += 1

###################################################################
#                       Position Helpers                          #
###################################################################

def position_shape(asset : Shape, x : int, y : int) -> Shape:
  """Position a Shape at x, y"""
  vertices = []
  originPoint = asset.vertices[0]
  for point in asset.vertices:
    xShift = point[0] - originPoint[0]
    yShift = point[1] - originPoint[1]
    newPoint = (x+xShift, y+yShift)
    vertices.append(newPoint)
  asset = Shape(vertices, asset.color, asset.width, asset.id)
  return asset

def position_collage(asset : Collage, x : int, y : int) -> None:
  """Position a Collage at x, y"""
  index = 0
  base = asset.shapes[0]
  for shape in asset.shapes:
    xShift = ref_point(shape)[0] - ref_point(base)[0] # x distance between curr shape and origin
    yShift = ref_point(shape)[1] - ref_point(base)[1] # y distance between curr shape and origin
    newShape = AssetHandler.position(shape, x+xShift, y+yShift)
    asset.update_shape(newShape, index)
    index += 1

def position_animation(asset : Animation, x : int, y : int) -> None:
  """Position an Animation at x, y"""
  index = 0
  basePoint = ref_point(asset.frames[0])
  for frame in asset.frames:
    xShift = ref_point(frame)[0] - basePoint[0]
    yShift = ref_point(frame)[1] - basePoint[1]
    newFrame = AssetHandler.position(frame, x+xShift, y+yShift)
    asset.update_frame(newFrame, index)
    index += 1

###################################################################
#                        Scale Helpers                            #
###################################################################

def scale_shape(asset : Shape, xScale : float, yScale : float) -> Shape:
  """Scale a Shape by given factors"""
  vertices = []
  xOrigin = ref_point(asset)[0]
  yOrigin = ref_point(asset)[1]
  for point in asset.vertices:
    xDist = point[0] - xOrigin
    yDist = point[1] - yOrigin
    newPoint = (xDist*xScale+xOrigin, yDist*yScale+yOrigin)
    vertices.append(newPoint)
  asset = Shape(vertices, asset.color, asset.width, asset.id)
  return asset

def scale_collage(asset : Collage, xScale : float, yScale : float) -> None:
  """Scale a Collage by given factors"""
  index = 0
  xBase = ref_point(asset.shapes[0])[0]
  yBase = ref_point(asset.shapes[0])[1]
  for shape in asset.shapes:
    xDist = ref_point(shape)[0] - xBase # x distance between curr shape and origin
    yDist = ref_point(shape)[1] - yBase # y distance between curr shape and origin
    newShape = AssetHandler.position(shape, xDist*xScale+xBase, yDist*yScale+yBase)
    newShape = AssetHandler.scale(newShape, xScale, yScale)
    asset.update_shape(newShape, index)
    index += 1

def scale_animation(asset : Animation, xScale : float, yScale : float) -> None:
  """Scale an Animation by given factors"""
  index = 0
  xBase = ref_point(asset.frames[0])[0]
  yBase = ref_point(asset.frames[0])[1]
  for frame in asset.frames:
    xDist = ref_point(frame)[0] - xBase
    yDist = ref_point(frame)[1] - yBase
    newFrame = AssetHandler.position(frame, xDist*xScale+xBase, yDist*yScale+yBase)
    newFrame = AssetHandler.scale(newFrame, xScale, yScale)
    asset.update_frame(newFrame, index)
    index += 1

###################################################################
#                       X Flip Helpers                            #
###################################################################

def x_flip_shape(asset : Shape, center : tuple) -> Shape:
  """Reflect a Shape across the y-axis"""
  vertices = []
  xCenter, yCenter = center
  for point in asset.vertices:
    x = 2*xCenter - point[0]
    y = point[1]
    vertices.append((x, y))
  shape = Shape(vertices, asset.color, asset.width, asset.id)
  return shape

def x_flip_collage(asset : Collage) -> None:
  """Reflect a Collage across the y-axis"""
  base = asset.get_component("base")[0]
  center = AssetHandler.shape_center(asset.shapes[base])

  index = 0
  for shape in asset.shapes:
    flipped_shape = x_flip_shape(shape, center)
    asset.update_shape(flipped_shape, index)
    index += 1

def x_flip_animation(asset : Animation) -> None:
  """Reflect an Animation across the y-axis"""
  index = 0
  for frame in asset.shapes:
    flipped_frame = AssetHandler.x_flip(frame)
    asset.update_frame(flipped_frame, index)
    index += 1

###################################################################
#                        AssetHandler                             #
###################################################################

class AssetHandler:
  assets = load_all_assets()
  
  @staticmethod
  def get_asset(id : str):
    """Return a copy of a given asset"""
    try:
      return deep_copy(AssetHandler.assets[id])
    except(KeyError):
      print("Asset", id, "not found")
      return deep_copy(AssetHandler.assets["unknown"])

  @staticmethod
  def scale(asset : Asset, xScale : float, yScale : float) -> Shape:
    """Scale an asset by the given factors"""
    if isinstance(asset, Shape):
      asset = scale_shape(asset, xScale, yScale)
    elif isinstance(asset, Collage):
      scale_collage(asset, xScale, yScale)
    elif isinstance(asset, Animation):
      scale_animation(asset, xScale, yScale)
    return asset

  @staticmethod
  def position(asset : Asset, x : int, y : int) -> Shape:
    """Position an asset at x, y"""
    if isinstance(asset, Shape):
      asset = position_shape(asset, x, y)
    elif isinstance(asset, Collage):
      position_collage(asset, x, y)
    elif isinstance(asset, Animation):
      position_animation(asset, x, y)
    return asset
  
  @staticmethod
  def x_flip(asset : Asset) -> Shape:
    """Reflect an asset across the y-axis"""
    if isinstance(asset, Shape):
      center = AssetHandler.shape_center(asset)
      asset = x_flip_shape(asset, center)
    elif isinstance(asset, Collage):
      x_flip_collage(asset)
    elif isinstance(asset, Animation):
      x_flip_animation(asset)
    return asset

  @staticmethod
  def color(asset : Asset, color : tuple, id : str) -> Shape:
    """Color an asset component a given color"""
    if isinstance(asset, Shape):
      asset = Shape(asset.vertices, color, asset.width, asset.id)
    elif isinstance(asset, Collage):
      color_collage(asset, color, id)
    elif isinstance(asset, Animation):
      color_animation(asset, color, id)
    return asset
  
  @staticmethod
  def get_size(asset : Asset) -> tuple:
    """Return the size of an asset"""
    if isinstance(asset, Shape):
      return shape_size(asset)
    elif isinstance(asset, Collage):
      base = asset.get_component("base")[0]
      return shape_size(asset.shapes[base])
    elif isinstance(asset, Animation):
      return animation_size(asset)
  
  @staticmethod
  def shape_position(shape : Shape) -> tuple:
    """Return the position of a given Shape"""
    xMin, yMin = [1000000] * 2
    for point in shape.vertices:
      if point[0] < xMin:
        xMin = point[0]
      if point[1] < yMin:
        yMin = point[1]
    return xMin, yMin
  
  @staticmethod
  def shape_center(shape : Shape) -> tuple:
    """Return the center of a given Shape"""
    width, height = AssetHandler.get_size(shape)
    x, y = AssetHandler.shape_position(shape)
    center = (x+width//2, y+height//2)
    return center
  
  @staticmethod
  def collage_center(collage : Collage) -> tuple:
    """Return the center of a given Collage"""
    baseIndex = collage.get_component("base")[0]
    base = collage.shapes[baseIndex]
    return AssetHandler.shape_center(base)