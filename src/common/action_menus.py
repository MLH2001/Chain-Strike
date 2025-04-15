from common.user_interface import Environment, ActionMenu, Button
from common.asset_handler import AssetHandler
from common.chips import Chip, Folder
from common.graphics import *

class ChipMenu(ActionMenu):
  def __init__(self, windowSize : tuple, folder : Folder):
    super().__init__()
    self._folder = folder # Deck of chips to choose from
    self._selectChips = [] # The chips that the player can select from
    self._chipOrder = [] # The order of chips currently selected by player
    self._highlightOrder = [] # The order of chips to highlight on the screen
    # State of all chip buttons in menu
    self._slotStates = [Environment.ACTIVE, Environment.ACTIVE, Environment.ACTIVE, Environment.ACTIVE, Environment.ACTIVE]
    self._counter = 0 # Current frame of highlight period
    self._cooldown = 7 # Number of frames panels are highlighted
    self._build_assets(windowSize)
    self._build_buttons(windowSize)
    self._build_events()

  def _build_assets(self, windowSize : tuple) -> None:
    """Build all non-button assets"""
    self._build_frame(windowSize)
    self._build_screen()
  
  def _build_buttons(self, windowSize : tuple) -> None:
    """Build all menu buttons and their assets"""
    self._build_chip_buttons()
    self._build_clear_button()
    self._build_confirm_button()
  
  def _build_events(self) -> None:
    """Build all non-button player driven events"""
    return
  
  def frame_update(self, windowSize : tuple) -> None:
    """Update all assets that are frame dependent"""
    if self._counter >= self._cooldown and len(self._highlightOrder) > 0:
      nextChipIndex = self._highlightOrder.pop(0)
      self._highlightOrder.append(nextChipIndex)
      nextChip = self._selectChips[nextChipIndex]
      areaMatrix = nextChip.get_area_matrix()
      color = Colors.YELLOW
      if nextChipIndex == self._chipOrder[0]:
        color = Colors.GREEN
      self._highlight(areaMatrix, color)
      self._counter = 0
    else:
      self._counter += 1
  
  ###################################################################
  #                        General Helpers                          #
  ###################################################################

  def _highlight(self, areaMatrix : list, color : tuple = Colors.YELLOW) -> None:
    """Highlight panels designated in areaMatrix with a given color"""
    for row in range(len(areaMatrix)):
      for col in range(len(areaMatrix[row])):
        if areaMatrix[row][col]:
          AssetHandler.color(self._screenMatrix[row][col], color, "base")
        else:
          AssetHandler.color(self._screenMatrix[row][col], Colors.PANELGREY, "base")

  ###################################################################
  #                        Asset Builders                           #
  ###################################################################

  def _build_frame(self, windowSize : tuple) -> None:
    """Load, position, and scale menu frame asset"""
    # Desired size
    menuWidth, menuHeight = self._relative_size(2, 1, windowSize)
    # Load asset
    menuFrame = AssetHandler.get_asset("chipMenu")
    # Position asset
    AssetHandler.position(menuFrame, 0, 0)
    # Scale asset
    xScale, yScale = self._scale(menuFrame, menuWidth, menuHeight)
    AssetHandler.scale(menuFrame, xScale, yScale)
    self._assets.append(menuFrame)
    self._frame = menuFrame
  
  def _build_screen(self) -> None:
    """Fill the screen component of the menu frame with a mock stage"""
    # Get screen component from frame
    originX, originY, width, height = self._get_component_info("window")

    # Fill screen
    self._screenMatrix = [[], [], []]
    panelWidth, panelHeight = self._relative_size(3, 3, (width, height))
    y = originY
    for row in range(3):
      x = originX
      for col in range(3):
        panelAsset = self._build_panel(x, y, panelWidth, panelHeight)
        self._screenMatrix[row].append(panelAsset)
        self._assets.append(self._screenMatrix[row][col])
        x += panelWidth
      y += panelHeight

  def _build_panel(self, x : int, y : int, panelWidth : int, panelHeight : int) -> None:
    """Load, position, and scale a panel asset"""
    panelAsset = AssetHandler.get_asset("panel")
    AssetHandler.color(panelAsset, Colors.BLUE, "border")
    AssetHandler.position(panelAsset, x, y)
    xScale, yScale = self._scale(panelAsset, panelWidth, panelHeight)
    AssetHandler.scale(panelAsset, xScale, yScale)
    return panelAsset
  
  def _get_component_info(self, componentID : str, index : int = 0) -> tuple:
    """Get the position and size of a given component in the menu frame"""
    componentIndex = self._frame.get_component(componentID)[index]
    componentShape = self._frame.shapes[componentIndex]
    x, y = AssetHandler.shape_position(componentShape)
    width, height = AssetHandler.get_size(componentShape)
    return x, y, width, height

  ###################################################################
  #                        Button Builders                          #
  ###################################################################

  def _build_clear_button(self) -> None:
    """Place a button on the clear component of the frame attached to the clear function"""
    # Get clear button component from frame
    x, y, width, height = self._get_component_info("clear")

    # Build button
    clearButton = self._build_button(x, y, width, height)
    self._buttons[clearButton] = self._clear

  def _build_confirm_button(self) -> None:
    """Place a button on the confirm component of the frame attached to the confirm function"""
    # Get clear button component from frame
    x, y, width, height = self._get_component_info("confirm")

    # Build button
    confirmButton = self._build_button(x, y, width, height)
    self._buttons[confirmButton] = self._confirm

  def _build_chip_buttons(self) -> None:
    """Place buttons and their assets in each chip slot in the frame"""
    self._chipOrder.clear()
    self._highlightOrder.clear()

    slotFunctions = (self._slot0, self._slot1, self._slot2, self._slot3, self._slot4)
    slotIndices = self._frame.get_component("slot")
    self._update_chip_selection(slotIndices)
    for i, slotIndex in enumerate(slotIndices):
      slotShape = self._frame.shapes[slotIndex]
      chip = self._selectChips[i]
      self._build_chip_asset(slotShape, chip)
      button = self._build_chip_button(slotShape)
      self._buttons[button] = slotFunctions[i]

  def _update_chip_selection(self, slotIndices : list) -> None:
    """Draw chips until there are enough selecct chips to fill chip slots"""
    for i in range(len(slotIndices)-len(self._selectChips)):
      chip = self._folder.draw()
      while chip in self._selectChips:
        chip = self._folder.draw()
      self._selectChips.append(chip)

  def _build_chip_asset(self, slotShape : Shape, chip : Chip) -> None:
    """Fill a given slot with a given chips asset"""
    # Slot position and size
    x, y = AssetHandler.shape_position(slotShape)
    width, height = AssetHandler.get_size(slotShape)

    # Load asset
    chipAsset = chip.get_asset()

    # Position and scale asset
    AssetHandler.position(chipAsset, x, y)
    xScale, yScale = self._scale(chipAsset, width, height)
    AssetHandler.scale(chipAsset, xScale, yScale)
    self._assets.append(chipAsset)

  def _build_chip_button(self, slotShape : Shape) -> Button:
    """Place a button on a given chip slot"""
    # Slot position and size
    x, y = AssetHandler.shape_position(slotShape)
    width, height = AssetHandler.get_size(slotShape)

    # Create button object
    chipButton = self._build_button(x, y, width, height)
    return chipButton
  
  def _build_button(self, x : int, y : int, width : int, height : int) -> Button:
    """Build a button object with a specified position and size"""
    xRange = (x, x+width)
    yRange = (y, y+height)
    button = Button(xRange, yRange)
    return button

  ###################################################################
  #                            Events                               #
  ###################################################################

  def activate(self, environmentManager) -> None:
    """Activate environment"""
    PAL = environmentManager.get_environment("PAL")
    PAL.pause()
    SAL = environmentManager.get_environment("SAL")
    SAL.pause()
    BE = environmentManager.get_environment("BE")
    BE.pause()
    self.resize(environmentManager.get_window_size())
    self._slotStates = [Environment.ACTIVE, Environment.ACTIVE, Environment.ACTIVE, Environment.ACTIVE, Environment.ACTIVE]
    self.status = Environment.ACTIVE

  def _slot0(self, environmentManager) -> None:
    """Button event for chip slot 0"""
    chipIndex = 0
    if self._slotStates[chipIndex] == Environment.ACTIVE:
      self._update_chipOrder(chipIndex)
      self._slotStates[chipIndex] = Environment.INACTIVE
  
  def _slot1(self, environmentManager) -> None:
    """Button event for chip slot 1"""
    chipIndex = 1
    if self._slotStates[chipIndex] == Environment.ACTIVE:
      self._update_chipOrder(chipIndex)
      self._slotStates[chipIndex] = Environment.INACTIVE
  
  def _slot2(self, environmentManager) -> None:
    """Button event for chip slot 2"""
    chipIndex = 2
    if self._slotStates[chipIndex] == Environment.ACTIVE:
      self._update_chipOrder(chipIndex)
      self._slotStates[chipIndex] = Environment.INACTIVE
  
  def _slot3(self, environmentManager) -> None:
    """Button event for chip slot 3"""
    chipIndex = 3
    if self._slotStates[chipIndex] == Environment.ACTIVE:
      self._update_chipOrder(chipIndex)
      self._slotStates[chipIndex] = Environment.INACTIVE
  
  def _slot4(self, environmentManager) -> None:
    """Button event for chip slot 4"""
    chipIndex = 4
    if self._slotStates[chipIndex] == Environment.ACTIVE:
      self._update_chipOrder(chipIndex)
      self._slotStates[chipIndex] = Environment.INACTIVE

  def _clear(self, environmentManager) -> None:
    """Button event for clearing current chip order"""
    self._build_chip_buttons()
    clearMatrix = [[False]*3]*3
    self._highlight(clearMatrix)
    self._slotStates = [Environment.ACTIVE, Environment.ACTIVE, Environment.ACTIVE, Environment.ACTIVE, Environment.ACTIVE]
  
  def _confirm(self, environmentManager) -> None:
    """Button event for confirming current chip order"""
    BE = environmentManager.get_environment("BE")
    BE.activate()
    PAL = environmentManager.get_environment("PAL")
    PAL.activate()
    SAL = environmentManager.get_environment("SAL")
    SAL.activate()
    SAL.load_p1_chip_order(self._export_chip_order())
    self._update_selectChips()
    self._counter = 0
    self.deactivate()
  
  ###################################################################
  #                        Event Helpers                            #
  ###################################################################

  def _export_chip_order(self) -> list:
    """Convert chip order list to chips"""
    chipOrder = []
    for index in self._chipOrder:
      chip = self._selectChips[index]
      chipOrder.append(chip)
    return chipOrder

  def _update_chipOrder(self, chipIndex : int) -> None:
    """Add a given chip to the current chip order and cover the chips menu slot"""
    self._empty_slot(chipIndex)
    self._chipOrder.append(chipIndex)
    self._highlightOrder.clear()
    for chip in self._chipOrder:
      self._highlightOrder.append(chip)
  
  def _update_selectChips(self) -> None:
    """Remove chips in chip order from select chips"""
    for chipIndex in sorted(self._chipOrder, reverse=True):
      self._selectChips.pop(chipIndex)

  def _empty_slot(self, slotIndex : int) -> None:
    """Cover a given chip slot with a black square"""
    slotIndices = self._frame.get_component("slot")
    slotShape = self._frame.shapes[slotIndices[slotIndex]]
    # Slot position and size
    x, y = AssetHandler.shape_position(slotShape)
    width, height = AssetHandler.get_size(slotShape)

    # Fill slot with black square
    squareAsset = AssetHandler.get_asset("square")
    squareAsset = AssetHandler.color(squareAsset, Colors.BLACK, "base")
    squareAsset = AssetHandler.position(squareAsset, x, y)
    xScale, yScale = self._scale(squareAsset, width, height)
    squareAsset = AssetHandler.scale(squareAsset, xScale, yScale)
    self._assets.append(squareAsset)
