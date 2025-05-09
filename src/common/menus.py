from common.user_interface import *
from common.graphics import *

###################################################################
#                          MainMenu                               #
###################################################################

class MainMenu(Menu):
  def __init__(self, windowSize : tuple, start_function, folder_function, quit_function):
    super().__init__()
    self._start = start_function
    self._folder = folder_function
    self._quit = quit_function
    self._build_assets(windowSize)
    self._build_buttons(windowSize)

  def _build_assets(self, windowSize : tuple) -> None:
    """Build all non-button assets"""
    self._build_title(windowSize)
  
  def _build_title(self, windowSize : tuple) -> None:
    textWidth, textHeight = self._relative_size(1, 5, windowSize)
    x = windowSize[0] // 3
    y = textHeight
    chainText = Text(x, y, "Chain", textHeight, Colors.RED)
    strikeText = Text(x*2, y, "Strike", textHeight, Colors.BLUE)
    self._assets.append(chainText)
    self._assets.append(strikeText)

  def _build_buttons(self, windowSize : tuple) -> None:
    """Build all buttons and their assets"""
    self._build_start_button(windowSize)
    self._build_folder_button(windowSize)
    self._build_quit_button(windowSize)
  
  def _build_start_button(self, windowSize : tuple) -> None:
    """Build start button and its asset"""
    # Desired size
    assetWidth, assetHeight = self._relative_size(6, 28, windowSize)
    # Load asset
    startAsset = AssetHandler.get_asset("trapezoid")
    # Scale asset
    xScale, yScale = self._scale(startAsset, assetWidth, assetHeight)
    startAsset = AssetHandler.scale(startAsset, xScale, yScale)
    # Position asset
    x = windowSize[0] // 2 - assetWidth // 2
    y = assetHeight * 20
    startAsset = AssetHandler.position(startAsset, x, y)
    # Color asset
    startAsset = AssetHandler.color(startAsset, Colors.RED, "trapezoid")
    self._assets.append(startAsset)
    # Create text
    xCenter, yCenter = AssetHandler.shape_center(startAsset)
    quitText = Text(xCenter, yCenter, "Start", assetHeight, Colors.WHITE)
    self._assets.append(quitText)
    # Create button
    startButton = Button((x, x+assetWidth), (y, y+assetHeight))
    self._buttons[startButton] = self._start

  def _build_folder_button(self, windowSize : tuple) -> None:
    """Build folder menu button and its asset"""
    # Desired size
    assetWidth, assetHeight = self._relative_size(6, 28, windowSize)
    # Load asset
    folderAsset = AssetHandler.get_asset("trapezoid")
    # Scale asset
    xScale, yScale = self._scale(folderAsset, assetWidth, assetHeight)
    folderAsset = AssetHandler.scale(folderAsset, xScale*.64, yScale)
    # Position asset
    x = windowSize[0] // 2 - (assetWidth*.64) // 2
    y = assetHeight * 22
    folderAsset = AssetHandler.position(folderAsset, x, y)
    # Color asset
    folderAsset = AssetHandler.color(folderAsset, Colors.RED, "trapezoid")
    self._assets.append(folderAsset)
    # Create text
    xCenter, yCenter = AssetHandler.shape_center(folderAsset)
    folderText = Text(xCenter, yCenter, "Folder", assetHeight, Colors.WHITE)
    self._assets.append(folderText)
    # Create button
    folderButton = Button((x, x+assetWidth*.64), (y, y+assetHeight))
    self._buttons[folderButton] = self._folder

  def _build_quit_button(self, windowSize : tuple) -> None:
    """Build quit button and its asset"""
    # Desired size
    assetWidth, assetHeight = self._relative_size(6, 28, windowSize)
    # Load asset
    quitAsset = AssetHandler.get_asset("trapezoid")
    # Scale asset
    xScale, yScale = self._scale(quitAsset, assetWidth, assetHeight)
    quitAsset = AssetHandler.scale(quitAsset, xScale*.64*.64, yScale)
    # Position asset
    x = windowSize[0] // 2 - (assetWidth*.64*.64) // 2
    y = assetHeight * 24
    quitAsset = AssetHandler.position(quitAsset, x, y)
    # Color asset
    quitAsset = AssetHandler.color(quitAsset, Colors.RED, "trapezoid")
    self._assets.append(quitAsset)
    # Create text
    xCenter, yCenter = AssetHandler.shape_center(quitAsset)
    quitText = Text(xCenter, yCenter, "Quit", assetHeight, Colors.WHITE)
    self._assets.append(quitText)
    # Create button
    quitButton = Button((x, x+assetWidth*.64*.64), (y, y+assetHeight))
    self._buttons[quitButton] = self._quit


###################################################################
#                          PauseMenu                              #
###################################################################

class PauseMenu(Menu):
  def __init__(self, windowSize : tuple, resumeFunction, mainMenuFunction, quitFunction):
    super().__init__()
    self._resumeFunction = resumeFunction
    self._mainMenuFunction = mainMenuFunction
    self._quitFunction = quitFunction
    self._build_assets(windowSize)
    self._build_buttons(windowSize)
  
  def _build_assets(self, windowSize : tuple) -> None:
    """Build all non-button assets"""
    self._build_frame(windowSize)

  def _build_buttons(self, windowSize : tuple) -> None:
    """Build all buttons and their assets"""
    self._build_resume_button(self._resumeFunction)
    self._build_main_menu_button(self._mainMenuFunction)
    self._build_quit_button(self._quitFunction)
  
  def _button_asset(self, index : int, text : str) -> None:
    # Load asset
    asset = AssetHandler.get_asset("square")

    # Desired size
    offset = 3
    assetWidth, assetHeight = self._relative_size(1, 3, self._frameSize)
    assetWidth -= 2 * offset
    assetHeight -= 2 * offset

    # Scale
    xScale, yScale = self._scale(asset, assetWidth, assetHeight)
    asset = AssetHandler.scale(asset, xScale, yScale)

    # Position
    x, y = self._framePosition
    x += offset
    y += offset + (index * (assetHeight + 2 * offset))
    asset = AssetHandler.position(asset, x, y)

    # Color
    asset = AssetHandler.color(asset, Colors.LIGHTGREY, "square")
    self._assets.append(asset)

    # Text
    x, y = AssetHandler.shape_center(asset)
    text = Text(x, y, text, assetHeight, Colors.BLACK)
    self._assets.append(text)

  def _button(self, index : int, function) -> None:
    # Desired size
    offset = 3
    buttonWidth, buttonHeight = self._relative_size(1, 3, self._frameSize)
    buttonWidth -= 2 * offset
    buttonHeight -= 2 * offset
    
    # Position
    offset = 3
    x, y = self._framePosition
    x += offset
    y += offset + (index * (buttonHeight + 2 * offset))

    # Button
    xRange = (x, x+buttonWidth)
    yRange = (y, y+buttonHeight)
    button = Button(xRange, yRange)
    self._buttons[button] = function

  def _build_resume_button(self, resumeFunction) -> None:
    self._button_asset(0, "Resume")
    self._button(0, resumeFunction)

  def _build_main_menu_button(self, mainMenuFunction) -> None:
    self._button_asset(1, "Main Menu")
    self._button(1, mainMenuFunction)
  
  def _build_quit_button(self, quitFunction) -> None:
    self._button_asset(2, "Quit")
    self._button(2, quitFunction)

  def _build_frame(self, windowSize : tuple) -> None:
    # Load asset
    frameAsset = AssetHandler.get_asset("square")

    # Desired size
    assetWidth, assetHeight = self._relative_size(3, 3, windowSize)
    self._frameSize = (assetWidth, assetHeight)

    # Scale
    xScale, yScale = self._scale(frameAsset, assetWidth, assetHeight)
    frameAsset = AssetHandler.scale(frameAsset, xScale, yScale)

    # Position
    x = assetWidth
    y = assetHeight
    self._framePosition = (x, y)
    frameAsset = AssetHandler.position(frameAsset, x, y)

    # Color
    frameAsset = AssetHandler.color(frameAsset, Colors.GREY, "square")
    self._assets.append(frameAsset)
  