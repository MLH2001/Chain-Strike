from common.user_interface import Environment
from common.asset_handler import AssetHandler
from common.graphics import *

class BackgroundEnvironment(Environment):
  def __init__(self, windowSize : tuple):
    super().__init__()
    self._build_assets(windowSize)

  def _build_assets(self, windowSize : tuple) -> None:
    """Build all environment assets"""
    self._build_background(windowSize)

  ###################################################################
  #                     Background Builders                         #
  ###################################################################

  def _build_background(self, windowSize : tuple) -> None:
    """Build background assets"""
    # Desired size
    snakeWidth, snakeHeight = self._relative_size(12, 16, windowSize)

    for col in range(14):
      for row in range(18):
        # Load asset
        snake = AssetHandler.get_asset("snake")

        # Scale asset
        xScale, yScale = self._scale(snake, snakeWidth, snakeHeight)
        AssetHandler.scale(snake, xScale, yScale)

        # Position asset
        x = snakeWidth * (col-1)
        y = snakeHeight * (row-1)
        AssetHandler.position(snake, x, y)
        
        # Stagger animations
        if col % 2 == 1 or row % 2 == 1:
          snake.activeFrame = len(snake.frames) // 4
        self._assets.append(snake)


class GameOverEnvironment(Environment):
  def __init__(self, windowSize : tuple):
    super().__init__()
    self._build_assets(windowSize)
  
  def _build_assets(self, windowSize : tuple) -> None:
    self._build_text(windowSize)
  
  def _build_text(self, windowSize : tuple) -> None:
    textWidth, textHeight = self._relative_size(1, 5, windowSize)
    xCenter = windowSize[0] // 2
    yCenter = textHeight
    gameOverText = Text(xCenter, yCenter, "Game Over", textHeight, Colors.RED)
    self._assets.append(gameOverText)


class VictoryEnvironment(Environment):
  def __init__(self, windowSize : tuple):
    super().__init__()
    self._build_assets(windowSize)
  
  def _build_assets(self, windowSize : tuple) -> None:
    self._build_text(windowSize)
  
  def _build_text(self, windowSize : tuple) -> None:
    textWidth, textHeight = self._relative_size(1, 5, windowSize)
    xCenter = windowSize[0] // 2
    yCenter = textHeight
    victoryText = Text(xCenter, yCenter, "Victory", textHeight, Colors.GREEN)
    self._assets.append(victoryText)


class StageEnvironment(Environment):
  def __init__(self, windowSize : tuple):
    super().__init__()
    self._build_assets(windowSize)
  
  def _build_assets(self, windowSize : tuple) -> None:
    self._build_panels(windowSize)
    self._build_stage_side(windowSize)
  
  def _build_panels(self, windowSize : tuple) -> None:
    """Build all panel assets in stage"""

    # Desired size
    panelWidth, panelHeight = self._relative_size(6, 7, windowSize)
    panelSeparation = 3
    panelWidth -= panelSeparation
    panelHeight -= panelSeparation

    color = Colors.RED
    for col in range(6):
      if col > 2:
        color = Colors.BLUE
      for row in range(3, 6):
        # Load asset
        panel = AssetHandler.get_asset("panel")
        
        # Scale asset
        xScale, yScale = self._scale(panel, panelWidth, panelHeight)
        AssetHandler.scale(panel, xScale, yScale)

        # Position asset
        x = (panelWidth + panelSeparation) * col
        y = (panelHeight + panelSeparation) * row
        AssetHandler.position(panel, x, y)

        # Color asset
        AssetHandler.color(panel, color, "border")
        self._assets.append(panel)

  def _build_stage_side(self, windowSize : tuple) -> None:
    """Build stage side assets"""
    sideWidth, sideHeight = self._relative_size(6, 14, windowSize)
    sideSeparation = 3
    sideWidth -= sideSeparation
    sideHeight -= sideSeparation

    color = Colors.RED
    for col in range(6):
      if col > 2:
        color = Colors.BLUE
      # Load asset
      side = AssetHandler.get_asset("panelSide")

      # Scale asset
      xScale, yScale = self._scale(side, sideWidth, sideHeight)
      AssetHandler.scale(side, xScale, yScale)

      # Position asset
      x = (sideWidth + sideSeparation) * col
      y = (sideHeight + sideSeparation) * 12
      AssetHandler.position(side, x, y)

      # Color asset
      AssetHandler.color(side, color, "border")
      self._assets.append(side)