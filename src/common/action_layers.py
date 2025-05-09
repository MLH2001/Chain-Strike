from common.user_interface import ActionLayer
from common.asset_handler import AssetHandler
from common.graphics import *
from common.player import Player
from common.containers import Matrix

###################################################################################
#                                PlayerLayer                                      #
###################################################################################

class PlayerLayer(ActionLayer):
  def __init__(self, windowSize : tuple, player1 : Player, player2 : Player):
    super().__init__()
    self._build_assets(windowSize, player1, player2)
    self._build_events()

  def _build_assets(self, windowSize : tuple, player1 : Player, player2 : Player) -> None:
    """Build all environment assets"""
    self._build_healthbars(windowSize, player1.get_health(), player2.get_health())
    self._build_players(windowSize, player1, player2)
    # remember players in case of resize
    self._player1 = player1
    self._player2 = player2

  def _build_events(self) -> None:
    """Build all events"""
    self._events["DAMAGE"] = self.update
    self._events["MOVEMENT"] = self.update

  def update(self, windowSize : tuple, player1 : Player, player2 : Player) -> None:
    """Rebuild all environment assets"""
    self._assets.clear()
    self._build_assets(windowSize, player1, player2)
  
  def resize(self, windowSize : tuple) -> None:
    """Resize all assets to fit window"""
    self._assets.clear()
    self._build_assets(windowSize, self._player1, self._player2)

  ###################################################################
  #                     Healthbar Builders                          #
  ###################################################################

  def _build_healthbars(self, windowSize : tuple, p1Health : int, p2Health : int) -> None:
    """Build player healthbars"""
    self._build_p1_healthbar(windowSize, p1Health)
    self._build_p2_healthbar(windowSize, p2Health)

  def _build_p1_healthbar(self, windowSize : tuple, p1Health : int) -> None:
    """Build player1 healthbar"""
    p1Healthbar = self._load_healthbar_asset(windowSize)

    # Proportion health to player health
    healthScale = p1Health / Player.MAXHEALTH
    healthIndex = p1Healthbar.get_component("health")[0]
    health = p1Healthbar.shapes[healthIndex]
    health = AssetHandler.scale(health, healthScale, 1)
    p1Healthbar.update_shape(health, healthIndex)

    # Position healthbar
    AssetHandler.position(p1Healthbar, 0, 0)
    self._assets.append(p1Healthbar)
  
  def _build_p2_healthbar(self, windowSize : tuple, p2Health : int) -> None:
    """Build player2 healthbar"""
    p2Healthbar = self._load_healthbar_asset(windowSize)

    # Proportion health to player health
    healthScale = p2Health / Player.MAXHEALTH
    healthIndex = p2Healthbar.get_component("health")[0]
    health = p2Healthbar.shapes[healthIndex]
    health = AssetHandler.scale(health, healthScale, 1)
    p2Healthbar.update_shape(health, healthIndex)

    # Flip healthbar
    AssetHandler.x_flip(p2Healthbar)

    # Position healthbar
    AssetHandler.position(p2Healthbar, windowSize[0], 0)
    self._assets.append(p2Healthbar)
  
  def _load_healthbar_asset(self, windowSize : tuple):
    """Get and adjust healthbar asset from AssetHandler"""
    # Desired size
    barWidth, barHeight = self._relative_size(4, 24, windowSize)
    
    # Load asset
    healthbar = AssetHandler.get_asset("healthbar")

    # Scale asset
    xScale, yScale = self._scale(healthbar, barWidth, barHeight)
    AssetHandler.scale(healthbar, xScale, yScale)
    return healthbar

  ###################################################################
  #                       Player Builders                           #
  ###################################################################

  def _build_players(self, windowSize : tuple, player1 : Player, player2 : Player) -> None:
    """Build player assets"""
    # Desired size
    assetWidth, assetHeight = self._relative_size(6, 4, windowSize)
    
    # Load assets
    p1Asset = AssetHandler.get_asset("player")
    p2Asset = AssetHandler.get_asset("player")

    # Scale assets
    xScale, yScale = self._scale(p1Asset, assetWidth, assetHeight)
    AssetHandler.scale(p1Asset, xScale, yScale)
    xScale, yScale = self._scale(p2Asset, assetWidth, assetHeight)
    AssetHandler.scale(p2Asset, xScale, yScale)

    # Position assets
    x, y = player1.get_asset_position()
    xOffset = assetWidth * 45 // 243
    yOffset = assetHeight * 25 // 254
    AssetHandler.position(p1Asset, x-xOffset, y+yOffset)
    x, y = player2.get_asset_position()
    AssetHandler.position(p2Asset, x+xOffset, y+yOffset)

    # Flip player2
    AssetHandler.x_flip(p2Asset)

    p1Asset.shapes.pop(0)
    p2Asset.shapes.pop(0)
    self._assets.append(p1Asset)
    self._assets.append(p2Asset)
    

###################################################################################
#                                 StageLayer                                      #
###################################################################################

class StageLayer(ActionLayer):
  def __init__(self, windowSize : tuple):
    super().__init__()
    self._highlights = Matrix([[False]*6]*3)
    self._hits = Matrix([[False]*6]*3)
    self._build_assets(windowSize)
    self._build_events()

  def _build_assets(self, windowSize : tuple) -> None:
    """Build all environment assets"""
    self._build_panels(windowSize)
    self._build_stage_side(windowSize)

  def _build_events(self) -> None:
    """Build all events"""
    self._events["P1READY"] = False
    self._events["P2READY"] = False

  def get_panel_matrix(self) -> list:
    """Return panel matrix"""
    return self._panelMatrix

  def frame_update(self, windowSize : tuple) -> None:
    """Update frame dependent assets"""
    self._assets.clear()
    self._build_assets(windowSize)

  def highlight(self, matrix : Matrix) -> None:
    """Highlight panels in matrix"""
    self._highlights = matrix
  
  def hit(self, matrix : Matrix) -> None:
    """Hit panels in matrix"""
    self._hits = matrix
  
  def clear_highlight(self) -> None:
    """Clear all active highlights"""
    self._highlights.clear()
    self._hits.clear()

  ###################################################################
  #                        Stage Builders                           #
  ###################################################################
  
  def _build_panels(self, windowSize : tuple) -> None:
    """Build all panel assets in stage"""
    self._panelMatrix = [] # matrix of panel asset centers
    centerRow = []

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

        # Highlight panel
        if self._highlights[row-3][col]:
          AssetHandler.color(panel, Colors.YELLOW, "base")
        elif self._hits[row-3][col]:
          AssetHandler.color(panel, Colors.PURPLE, "base")
        
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

        centerRow.append(AssetHandler.collage_center(panel))
      self._panelMatrix.append(centerRow)
      centerRow = []

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