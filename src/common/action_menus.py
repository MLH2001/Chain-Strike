from common.user_interface import Environment, ActionMenu, Button
from common.asset_handler import AssetHandler
from common.chips import Chip, Folder
from common.graphics import *
from common.containers import Matrix
from common.chip_library import ChipLibrary

FAST = 2
SLOW = 1
STANDARD = 0
COOLDOWN = 7

class ChipMenu(ActionMenu):
  def __init__(self, windowSize : tuple, folder : Folder, confirmFunction):
    super().__init__()
    self._chipAssets = []
    self._confirm = confirmFunction
    self._folder = folder # Deck of chips to choose from
    self._selectChips = [] # The chips that the player can select from
    self._chipOrder = [] # The order of chips currently selected by player
    self._highlightIndex = 0 # The index of the next chip to highlight in chipOrder
    # State of all chip buttons in menu
    self._slotStates = [Environment.ACTIVE, Environment.ACTIVE, Environment.ACTIVE, Environment.ACTIVE, Environment.ACTIVE]
    self._counter = 0 # Current frame of highlight period
    self._cooldown = COOLDOWN
    self._mode_standard()
    self._build_assets(windowSize)
    self._build_buttons(windowSize)
    self._build_events()

  def set_folder(self, folder : Folder) -> None:
    self._folder = folder
    self._chipOrder = [0, 1, 2, 3, 4]
    self._update_selectChips()

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
    self._events["CONFIRM"] = self._confirmEvent
    self._events["FAST"] = self._mode_fast
    self._events["SLOW"] = self._mode_slow
    self._events["STANDARD"] = self._mode_standard
  
  def frame_update(self, *args) -> None:
    """Update all assets that are frame dependent"""
    self._refresh_chip_assets()

    if len(self._chipOrder) == 0:
      return
    if self._highlightIndex >= len(self._chipOrder):
      if self._counter == self._cooldown:
        clearMatrix = [[False]*3]*3
        self._highlight(clearMatrix)
      elif self._counter >= COOLDOWN + self._cooldown:
        self._highlightIndex = 0
        
    
    if self._counter >= self._cooldown and self._highlightIndex < len(self._chipOrder):
      nextChipIndex = self._chipOrder[self._highlightIndex]
      nextChip = self._selectChips[nextChipIndex]
      self._cooldown = nextChip.highlightFrames
      areaMatrix = nextChip.get_area_matrix()
      color = nextChip.highlightColor
      self._highlight(areaMatrix, color)
      self._highlightIndex += 1
      self._counter = 0
    else:
      self._counter += 1

  def get_assets(self) -> list:
     """Return environment assets"""
     assets = self._assets + self._chipAssets
     return assets

  ###################################################################
  #                        General Helpers                          #
  ###################################################################

  def _highlight(self, areaMatrix : Matrix, color : tuple = Colors.YELLOW) -> None:
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
    AssetHandler.position(panelAsset, x+1, y+1)
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

    slotIndices = self._frame.get_component("slot")
    self._update_chip_selection(slotIndices)
    for i, slotIndex in enumerate(slotIndices):
      slotShape = self._frame.shapes[slotIndex]
      chip = self._selectChips[i]
      self._build_chip_asset(slotShape, chip)
      button = self._build_chip_button(slotShape)
      self._buttons[button] = self._build_slot_function(i)
  
  def _refresh_chip_assets(self) -> None:
    """Refresh chip assets without changing chipOrder"""
    self._chipAssets.clear()
    slotIndices = self._frame.get_component("slot")
    self._update_chip_selection(slotIndices)
    for i, slotIndex in enumerate(slotIndices):
      if self._slotStates[i] == Environment.ACTIVE:
        slotShape = self._frame.shapes[slotIndex]
        chip = self._selectChips[i]
        self._build_chip_asset(slotShape, chip)

  def _update_chip_selection(self, slotIndices : list) -> None:
    """Draw chips until there are enough select chips to fill chip slots"""
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
    AssetHandler.color(chipAsset, self._chipColor, "base")
    self._chipAssets.append(chipAsset)

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

  def activate(self) -> None:
    """Activate environment"""
    self._slotStates = [Environment.ACTIVE, Environment.ACTIVE, Environment.ACTIVE, Environment.ACTIVE, Environment.ACTIVE]
    self._mode_standard()
    self.status = Environment.ACTIVE

  def _mode_fast(self) -> None:
    self._chipColor = Colors.RED
    self._chipHighlight = FAST

  def _mode_slow(self) -> None:
    self._chipColor = Colors.YELLOW
    self._chipHighlight = SLOW
  
  def _mode_standard(self) -> None:
    self._chipColor = Colors.ORANGE
    self._chipHighlight = STANDARD

  def _build_slot_function(self, chipIndex : int):
    """Build event function for a given chip slot"""
    def slot_function():
      if self._slotStates[chipIndex] == Environment.ACTIVE:
        self._update_chipOrder(chipIndex)
        self._slotStates[chipIndex] = Environment.INACTIVE
    return slot_function

  def _clear(self) -> None:
    """Button event for clearing current chip order"""
    self._build_chip_buttons()
    clearMatrix = [[False]*3]*3
    self._highlight(clearMatrix)
    self._slotStates = [Environment.ACTIVE, Environment.ACTIVE, Environment.ACTIVE, Environment.ACTIVE, Environment.ACTIVE]
  
  def _confirmEvent(self) -> None:
    """Button event for confirming current chip order"""
    self._update_selectChips()
    self._highlightIndex = 0
    self._counter = 0
    self.deactivate()
  
  ###################################################################
  #                        Event Helpers                            #
  ###################################################################

  def export_chip_order(self) -> list:
    """Convert chip order list to chips"""
    chipOrder = []
    for index in self._chipOrder:
      chip = self._selectChips[index]
      chipOrder.append(chip)
    return chipOrder

  def _update_chipOrder(self, chipIndex : int) -> None:
    """Add a given chip to the current chip order and cover the chips menu slot"""
    self._empty_slot(chipIndex)
    self._chip_speed(chipIndex)
    self._chipOrder.append(chipIndex)
    self._highlightIndex = 0
  
  def _chip_speed(self, chipIndex) -> None:
    if self._chipHighlight == FAST:
      self._selectChips[chipIndex].fast()
    elif self._chipHighlight == SLOW:
      self._selectChips[chipIndex].slow()
    elif self._chipHighlight == STANDARD:
      self._selectChips[chipIndex].standard()
  
  def _update_selectChips(self) -> None:
    """Remove chips in chip order from select chips"""
    if len(self._selectChips) == 0:
      return
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


class FolderSelectMenu(ActionMenu):
  def __init__(self, windowSize : tuple, folder : list, save_function, close_function):
    super().__init__()
    self._save_function = save_function
    self._close_function = close_function
    self._allChipsIndex = 0
    self._folder = folder
    self._saveLabel = Text(0, 0)
    self._build_events()
    self._build_assets(windowSize)
    self._build_buttons()

  def get_folder(self) -> list:
    return self._folder

  def set_folder(self, folder : list) -> None:
    self._folder = folder

  def resize(self, windowSize : tuple) -> None:
    self.frame_update(windowSize)

  def frame_update(self, windowSize : tuple) -> None:
    self._buttons = {}
    self._assets.clear()
    self._build_assets(windowSize)
    self._build_buttons()
  
  def _build_events(self):
    self._events["SAVE"] = self._save_event

  def _build_assets(self, windowSize : tuple) -> None:
    """Build all non-button menu assets"""
    self._build_menu_frame(windowSize)
    self._build_folder_label()
    self._assets.append(self._saveLabel)
  
  def _build_menu_frame(self, windowSize : tuple) -> None:
    """Build menu frame"""
    # Load asset
    menuFrame = AssetHandler.get_asset("folderMenu")
    # Position asset
    AssetHandler.position(menuFrame, 0, 0)
    # Scale asset
    width, height = windowSize
    xScale, yScale = self._scale(menuFrame, width, height)
    AssetHandler.scale(menuFrame, xScale, yScale)

    self._identify_components(menuFrame)
    self._assets.append(menuFrame)

  def _build_folder_label(self):
    shape = self._frame.shapes[self._folderLabelComponent[0]]
    self._build_text("Folder", shape)

  def _build_buttons(self) -> None:
    """Build all menu buttons"""
    self._build_close_button()
    self._build_save_button()
    self._build_previous_button()
    self._build_next_button()
    self._build_select_buttons()
    self._build_folder_buttons()
  
  def _build_close_button(self) -> None:
    closeShape = self._frame.shapes[self._closeComponent[0]]
    self._build_text("Close", closeShape)
    closeButton = self._build_button(closeShape)
    self._buttons[closeButton] = self._close_function
  
  def _build_save_button(self) -> None:
    saveShape = self._frame.shapes[self._saveComponent[0]]
    self._build_text("Save", saveShape)
    saveButton = self._build_button(saveShape)
    self._buttons[saveButton] = self._save_function
  
  def _build_previous_button(self) -> None:
    previousShape = self._frame.shapes[self._previousComponent[0]]
    self._build_text("Prev", previousShape)
    previousButton = self._build_button(previousShape)
    self._buttons[previousButton] = self._previous
  
  def _build_next_button(self) -> None:
    nextShape = self._frame.shapes[self._nextComponent[0]]
    self._build_text("Next", nextShape)
    nextButton = self._build_button(nextShape)
    self._buttons[nextButton] = self._next
  
  def _build_select_buttons(self) -> None:
    for i in range(len(self._selectComponent)):
      chipIndex = self._allChipsIndex + i
      if chipIndex >= len(ChipLibrary.allChips):
        continue
      chip = ChipLibrary.get_chip(chipIndex)
      slot = self._frame.shapes[self._selectComponent[i]]
      self._build_chip_asset(chip, slot)
      button = self._build_button(slot)
      self._buttons[button] = self._build_select_function(chipIndex)

  def _build_folder_buttons(self) -> None:
    for i in range(len(self._folder)):
      chip = ChipLibrary.get_chip(self._folder[i])
      slot = self._frame.shapes[self._folderComponent[i]]
      self._build_chip_asset(chip, slot)
      button = self._build_button(slot)
      self._buttons[button] = self._build_folder_function(i)

  ###################################################################
  #                           Helpers                               #
  ###################################################################

  def _identify_components(self, menuFrame : Collage) -> None:
    self._frame = menuFrame
    self._folderComponent = menuFrame.get_component("folder")
    self._selectComponent = menuFrame.get_component("select")
    self._previousComponent = menuFrame.get_component("previous")
    self._nextComponent = menuFrame.get_component("next")
    self._saveComponent = menuFrame.get_component("save")
    self._closeComponent = menuFrame.get_component("close")
    self._folderLabelComponent = menuFrame.get_component("folderLabel")
    self._saveLabelComponent = menuFrame.get_component("saveLabel")
  
  def _build_button(self, shape : Shape) -> Button:
    """Place a button on a given shape"""
    x, y = AssetHandler.shape_position(shape)
    width, height = AssetHandler.get_size(shape)
    xRange = (x, x+width)
    yRange = (y, y+height)
    button = Button(xRange, yRange)
    return button

  def _build_chip_asset(self, chip : Chip, slot : Shape) -> None:
    # slot shape and size
    x, y = AssetHandler.shape_position(slot)
    width, height = AssetHandler.get_size(slot)
    
    # load, position, scale
    chipAsset = chip.get_asset()
    xScale, yScale = self._scale(chipAsset, width-2, height-2)
    AssetHandler.position(chipAsset, x+1, y+1)
    AssetHandler.scale(chipAsset, xScale, yScale)
    self._assets.append(chipAsset)

  def _build_text(self, text : str, shape : Shape):
    xCenter, yCenter = AssetHandler.shape_center(shape)
    width, height = AssetHandler.get_size(shape)
    textAsset = Text(xCenter, yCenter, text, int(height//1.5), Colors.BLACK)
    self._assets.append(textAsset)

  ###################################################################
  #                            Events                               #
  ###################################################################
  
  def _save_event(self):
    shape = self._frame.shapes[self._saveLabelComponent[0]]
    xCenter, yCenter = AssetHandler.shape_center(shape)
    width, height = AssetHandler.get_size(shape)
    if len(self._folder) < 15:
      self._saveLabel = Text(xCenter, yCenter, "Incomplete", int(height//1.5), Colors.BLACK)
      return False
    self._saveLabel = Text(xCenter, yCenter, "Saved", int(height//1.5), Colors.BLACK)
    return True

  def deactivate(self):
    self._allChipsIndex = 0
    self._saveLabel = Text(0, 0)
    self.status = Environment.INACTIVE

  def _previous(self):
    if self._allChipsIndex == 0:
      return
    self._allChipsIndex -= len(self._selectComponent)
  
  def _next(self):
    if (self._allChipsIndex + len(self._selectComponent)) >= len(ChipLibrary.allChips):
      return
    self._allChipsIndex += len(self._selectComponent)

  # f0  f1  f2
  # f3  f4  f5
  # f6  f7  f8
  # f9  f10 f11
  def _build_folder_function(self, folderIndex):
    def function():
      if folderIndex >= len(self._folder):
        return
      self._folder.pop(folderIndex)
    return function

  # s0  s1  s2
  # s3  s4  s5
  # s6  s7  s8
  def _build_select_function(self, chipIndex):
    def function():
      if len(self._folder) < len(self._folderComponent):
        self._folder.append(chipIndex)
    return function
  
  ###################################################################
  #                        Event Helpers                            #
  ###################################################################
  