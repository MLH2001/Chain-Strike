from common.asset_handler import AssetHandler
from common.graphics import Asset

class Button:
  def __init__(self, xRange : tuple, yRange : tuple):
    # Range of window monitored for click
    self.xRange = xRange
    self.yRange = yRange


class Environment:
  ACTIVE = 2
  PAUSE =  1
  INACTIVE = 0

  def __init__(self):
    self.status = Environment.INACTIVE
    self._assets = [] # list of assets to be drawn when active
  
  def get_assets(self) -> list:
    """Return environment assets"""
    return self._assets
  
  def resize(self, windowSize : tuple) -> None:
    """Resize environment assets to fit window"""
    self._assets = []
    self._build_assets(windowSize)

  def activate(self) -> None:
    """Set Environment status to ACTIVE"""
    self.status = Environment.ACTIVE

  def pause(self) -> None:
    """Set Environment status to Pause"""
    self.status = Environment.PAUSE

  def deactivate(self) -> None:
    """Set Environment status to INACTIVE"""
    self.status = Environment.INACTIVE
  
  def _relative_size(self, xProportion : int, yProportion : int, windowSize : tuple) -> tuple:
    """Return the relative size of a given proportion of the screen"""
    maxWidth, maxHeight = windowSize[0], windowSize[1]
    width = maxWidth // xProportion
    height = maxHeight // yProportion
    return width, height
  
  def _scale(self, asset : Asset, objWidth : int, objHeight : int) -> tuple:
    """Return the scaling required to make an asset a given size"""
    assetWidth, assetHeight = AssetHandler.get_size(asset)
    xScale = objWidth / assetWidth
    yScale = objHeight / assetHeight
    return xScale, yScale


class Menu(Environment):
  def __init__(self):
    super().__init__()
    self._buttons = {} # dictionary of buttons to monitor when active
  
  def get_buttons(self) -> dict:
    """Return menu buttons"""
    return self._buttons
  
  def resize(self, windowSize : tuple) -> None:
    """Resize menu assets and buttons"""
    self._assets = []
    self._buttons = {}
    self._build_assets(windowSize)
    self._build_buttons(windowSize)


class ActionLayer(Environment):
  def __init__(self):
    super().__init__()
    self._events = {} # Dictionary of non-button player-driven events
  
  def frame_update(self, windowSize : tuple) -> None:
    """Update frame dependent assets"""
    return

  def get_events(self) -> dict:
    """Return action layer events"""
    return self._events


class ActionMenu(Menu):
  def __init__(self):
    super().__init__()
    self._events = {} # Dictionary of events that require asset updates
  
  def frame_update(self, windowSize : tuple) -> None:
    """Return action menu events"""
    return

  def get_events(self) -> dict:
    """Return action menu events"""
    return self._events