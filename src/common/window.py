import pygame
from common.file_handler import FileHandler
from common.graphics import *

class Window:
  def __init__(self, aspectRatio : tuple):
    self.graphics = Graphics([])
    self.scale_window(aspectRatio)
    pygame.display.set_caption("Chain Strike")
    path = FileHandler.get_packaged_files_path("icon.jpg")
    icon = pygame.image.load(path)
    pygame.display.set_icon(icon)

  def scale_window(self, aspectRatio : tuple) -> None:
    """Scale window to monitor with a given aspect ratio"""
    # Gather monitor width and height
    displayInfo = pygame.display.get_desktop_sizes()[0]
    screenWidth, screenHeight = displayInfo
    
    # Scale window width and height to screen
    width = screenWidth * .9
    height = (width * aspectRatio[1]) // aspectRatio[0]

    if height > screenHeight:
      height = screenHeight * .9
      width = (height * aspectRatio[0]) // aspectRatio[1]

    # Create pygame window
    self.window = pygame.display.set_mode((width, height), pygame.RESIZABLE)
  
  def update(self) -> None:
    """Redraw all active assets"""
    self.window.fill(Colors.BLACK)
    for asset in self.graphics.assets:
      self.draw(asset)
    pygame.display.flip()
  
  def update_graphics(self) -> None:
    """Update the active frame of all animations in graphics"""
    self.graphics.update()

  def get_size(self) -> tuple:
    """Return window width and height as tuple"""
    return self.window.get_size()
  
  def clear_assets(self) -> None:
    """Remove all assets in graphics"""
    self.graphics.clear()

  def append_assets(self, assets : list) -> None:
    """Append the given assets to graphics"""
    self.graphics.append(assets)

  def prepend_assets(self, assets : list) -> None:
    """Prepend the given assets to graphics"""
    self.graphics.prepend(assets)
  
  def draw(self, asset : Asset) -> None:
    """Draw a given asset in the window"""
    if isinstance(asset, Text):
      self.window.blit(asset.text, asset.text_box)
    elif isinstance(asset, Shape):
      pygame.draw.polygon(self.window, *asset.to_tuple())
    elif isinstance(asset, Collage):
      self.draw_collage(asset)
    elif isinstance(asset, Animation):
      frame = asset.get_frame()
      self.draw(frame)
    else:
      print("Invalid object found in graphics")
      print(asset)
      self.graphics.remove(asset)
      print("Object removed")

  def draw_collage(self, collage : Collage) -> None:
    """Draw a given Collage object in the window"""
    for shape in collage.shapes:
      pygame.draw.polygon(self.window, shape.color, shape.vertices, shape.width)