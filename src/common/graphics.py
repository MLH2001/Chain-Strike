import pygame

class Colors:
  RED = (255, 0, 0)
  GREEN = (0, 255, 0)
  BLUE = (0, 0, 255)
  YELLOW = (255, 255, 0)
  PURPLE = (255, 0, 255)
  WHITE = (255, 255, 255)
  BLACK = (0, 0, 0)
  GREY = (125, 125, 125)
  PANELGREY = (150, 150, 150)
  LIGHTGREY = (200, 200, 200)


class Asset:
  None


class Text(Asset):
  def __init__(self, x : int, y : int, text : str = "", size : int = 12, color : tuple = Colors.BLACK, antialias : bool = True, font=None):
    pyFont = pygame.font.Font(font, size)
    self.text = pyFont.render(text, antialias, color)
    self.text_box = self.text.get_rect(center=(x, y))


class Shape(Asset):
  def __init__(self, vertices : tuple = ((0,0), (0,0)), color : tuple = (0,0,0), width : int = 0, id=None):
    self.id = id
    self.vertices = vertices
    self.color = color
    self.width = width


class Collage(Asset):
  def __init__(self,shapes : list = [], id=None):
    self.id = id
    self.shapes = shapes
  
  def get_component(self, component_id) -> list:
    """Return list of indices of component shapes"""
    component = []
    for i in range(len(self.shapes)):
      if self.shapes[i].id == component_id:
        component.append(i)
    return component
  
  def update_shape(self, newShape : Shape, index : int) -> None:
    """Change the shape at a given index to a given new shape"""
    self.shapes[index] = newShape


class Animation(Asset):
  def __init__(self, frames : list = [Shape()], id=None):
    self.id = id
    self.frames = frames
    self.activeFrame = 0

  def update(self) -> None:
    """Set active frame to next frame"""
    nextFrame = self.activeFrame + 1
    if nextFrame >= len(self.frames):
      nextFrame = 0
    self.activeFrame = nextFrame

  def get_frame(self):
    """Return asset at active frame"""
    return self.frames[self.activeFrame]
  
  def update_frame(self, newFrame, index : int) -> None:
    """Change frame at a given index to a given new frame"""
    self.frames[index] = newFrame


class Graphics:
  def __init__(self, assets : list):
    self.assets = assets

  def get_asset(self, id : str) -> Asset:
    """Return asset in assets with a given id"""
    for asset in self.assets:
      if asset.id == id:
        return asset

  def update(self) -> None:
    """Update active frame of any animations in assets"""
    for asset in self.assets:
      if isinstance(asset, Animation):
        asset.update()
  
  def append(self, newAssets : list) -> None:
    """Append new assets onto assets"""
    self.assets += newAssets
  
  def prepend(self, newAssets : list) -> None:
    """Prepend new assets onto assets"""
    assets = newAssets + self.assets
    self.assets = assets
  
  def remove(self, asset) -> None:
    """Remove a given asset from assets"""
    self.assets.remove(asset)

  def clear(self) -> None:
    """Clear assets"""
    self.assets.clear()
