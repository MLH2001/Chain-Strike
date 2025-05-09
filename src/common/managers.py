import pygame
from common.window import Window
from common.environments import *
from common.menus import *
from common.action_layers import *
from common.action_menus import *
from common.player import *
from common.chips import *
from common.chip_library import ChipLibrary
from common.containers import *
from common.save import Save
from random import randint
from copy import deepcopy as deep_copy

###################################################################################
#                              Evironment Manager                                 #
###################################################################################

class EnvironmentManager:
  def __init__(self):
    self._window = Window((6, 4))
    self._environments = {}
    self._pausedAssets = []
    self._activeAssets = []

  def add_environment(self, key, environment : Environment, *args) -> None:
    """Add a given Environment to environments at a given key"""
    self._environments[key] = environment(self._window.get_size(), *args)

  ###################################################################
  #                          Updators                               #
  ###################################################################

  def update(self) -> None:
    """Update assets to match environemt states"""
    self._window.clear_assets()
    self._update_active_assets()
    self._window.append_assets(self._activeAssets)
    self._window.update_graphics()
    self._update_paused_assets()
    self._window.prepend_assets(self._pausedAssets)
    self._window.update()

  def _update_paused_assets(self) -> None:
    """Place all paused assets into pausedAssets list"""
    self._pausedAssets.clear()
    for key in self._environments.keys():
      env = self._environments[key]
      if env.status == Environment.PAUSE:
        self._pausedAssets += env.get_assets()

  def _update_active_assets(self) -> None:
    """Place all active assets into activeAssets list"""
    self._activeAssets.clear()
    for key in self._environments.keys():
      env = self._environments[key]
      if env.status == Environment.ACTIVE:
        if isinstance(env, (ActionLayer, ActionMenu)):
          env.frame_update(self._window.get_size())
        self._activeAssets += env.get_assets()

  def resize(self) -> None:
    """Resize all assets to fit window"""
    for key in self._environments.keys():
      env = self._environments[key]
      env.resize(self._window.get_size())
    self.update()

  ###################################################################
  #                          Accessors                              #
  ###################################################################

  def active_menu(self) -> Menu:
    """Return the current active Menu if any"""
    for key in self._environments.keys():
      env = self._environments[key]
      if isinstance(env, Menu) and env.status == Environment.ACTIVE:
        return env
  
  def get_environment(self, key) -> Environment:
    """Return the Environment at a given key"""
    return self._environments[key]
  
  def get_window_size(self) -> tuple:
    """Return width and height of window as a tuple"""
    return self._window.get_size()
  

###################################################################################
#                                Player Manager                                   #
###################################################################################

class PlayerManager:
  def __init__(self, player : Player, colRange : tuple):
    self._colMin, self._colMax = colRange
    self.player = player
    self.events = {
      "HPZERO" : False
    }
  
  def move_player(self, panelMatrix : list, windowSize : tuple, movement : tuple) -> None:
    """Move player according to a given movemnet vector"""
    stagePosition = self._update_stage_position(movement)
    self._update_asset_position(panelMatrix, windowSize, stagePosition)

  def _update_stage_position(self, movement : tuple) -> tuple:
    """Update players stage position"""
    x, y = self.player.get_stage_position()
    col = y+movement[1]
    row = x+movement[0]
    if col < self._colMin  or col > self._colMax:
        col = y
    if row < 0  or row > 2:
        row = x
    self.player.move((row, col))
    return row, col

  def _update_asset_position(self, panelMatrix : list, windowSize : tuple, stagePosition : tuple) -> None:
    """Update player asset according to stage position"""
    row, col = stagePosition
    panelX, panelY = panelMatrix[col][row]
    width, height = windowSize
    assetX = panelX - (width // 12)
    assetY = panelY - (height // 4)
    self.player.move_asset((assetX, assetY))

  def damage_player(self) -> None:
    """Damage player"""
    self.player.damage()
    if self.player.get_health() <= 0:
        self.events["HPZERO"] = True

###################################################################################
#                                Combat Manager                                   #
###################################################################################

HITCOOLDOWN = 20
SWITCH = 10
EMPTYMATRIX = Matrix([[False]*3]*3)

class CombatManager:
  def __init__(self):
    self._switchCounter = 0
    self._combinedChain = ParallelChains()
    self._p1HitCounter = HITCOOLDOWN
    self._p2HitCounter = HITCOOLDOWN
    self.events = {
      "ACTIVE" : False,
      "P1READY" : False,
      "P2READY" : False,
      "HIGHLIGHT" : True,
      "HIT" : False,
      "P1HIT" : False,
      "P2HIT" : False,
      "P1VULNERABLE" : True,
      "P2VULNERABLE" : True
    }
  
  def load_p1_chip_order(self, chipOrder : list) -> None:
    """Set p1 chip order for next round"""
    self._p1Chain = self._order_to_chain(chipOrder)
    self.events["P1READY"] = True
  
  def load_p2_chip_order(self, chipOrder : list) -> None:
    """Set p2 chip order for next round"""
    self._p2Chain = self._order_to_chain(chipOrder)
    self.events["P2READY"] = True

  def _order_to_chain(self, chipOrder : list) -> list:
    """Convert a list of chips to a list of panel matrices"""
    chain = Chain()
    for chip in chipOrder:
      for i in range(chip.highlightFrames):
        chain.append(chip.get_area_matrix())
    return chain

  def _combine_chains(self) -> None:
    """Combine p1Chain and p2Chain"""
    self._combinedChain.clear()
    self._combinedChain["P1"] = Chain()
    self._combinedChain["P2"] = Chain()
    while len(self._p1Chain) > 0 or len(self._p2Chain) > 0:
      if len(self._p1Chain) == 0:
        rightChain = EMPTYMATRIX
      else:
        rightChain = self._p1Chain.pop(0)
      if len(self._p2Chain) == 0:
        leftChain = EMPTYMATRIX
      else:
        leftChain = self._p2Chain.pop(0)
      self._combinedChain["P1"].append(leftChain)
      self._combinedChain["P2"].append(rightChain)

  def initialize_combat(self) -> None:
    """Set state for new round of combat"""
    if not self.events["ACTIVE"]:
      self._combine_chains()
      self._chainIndex = 0
      self.events["HIGHLIGHT"] = True
      self.events["HIT"] = False
      self.events["P1HIT"] = False
      self.events["P2HIT"] = False
      self.events["P1VULNERABLE"] = True
      self.events["P2VULNERABLE"] = True
      self.events["ACTIVE"] = True

  def combat(self, SAL : StageLayer, p1Manager : PlayerManager, p2Manager : PlayerManager) -> None:
    """Update the combat state"""
    if self.events["HIGHLIGHT"]:
      self._highlight(SAL, p2Manager)
      self._chainIndex += 1
    if self.events["HIT"] and self._switchCounter >= SWITCH:
      self._hit(SAL, p1Manager, p2Manager)
      self._chainIndex += 1
    self._switchCounter += 1
  
  def _highlight(self, SAL : StageLayer, p2Manager : PlayerManager) -> None:
    """Highlight next chips in chip order"""
    if self._chainIndex < len(self._combinedChain):
      SAL.highlight(self._combinedChain.merge(self._chainIndex))
    else:
      self._chainIndex = 0
      self._switchCounter = 0
      self.events["HIGHLIGHT"] = False
      self.events["HIT"] = True
      SAL.clear_highlight()
      p2Manager.player.hitOrder = self._combinedChain["P2"]
      p2Manager.player.analyze()
  
  def _hit(self, SAL : StageLayer, p1Manager : PlayerManager, p2Manager : PlayerManager) -> None:
    """Hit next chip in chip order"""
    if self._chainIndex < len(self._combinedChain):
      SAL.hit(self._combinedChain.merge(self._chainIndex))
      self._update_vulnerability()
      self._check_for_hit(p1Manager, p2Manager)
    else:
      self._chainIndex = 0
      self.events["HIGHLIGHT"] = True
      self.events["HIT"] = False
      self.events["P1READY"] = False
      self.events["P2READY"] = False
      self.events["ACTIVE"] = False
      SAL.clear_highlight()
  
  def _update_vulnerability(self) -> None:
    """Mark players as vulnerable of hit cooldown"""
    if self._p1HitCounter >= HITCOOLDOWN:
      self.events["P1VULNERABLE"] = True
    if self._p2HitCounter >= HITCOOLDOWN:
      self.events["P2VULNERABLE"] = True
  
  def _check_for_hit(self, p1Manager : PlayerManager, p2Manager : PlayerManager) -> None:
    """Detrmine if a playeer ahs been hit"""
    row, col = p1Manager.player.get_stage_position()
    if self._combinedChain["P1"][self._chainIndex][row][col] and self.events["P1VULNERABLE"]:
      self.events["P1HIT"] = True
      self.events["P1VULNERABLE"] = False
      self._p1HitCounter = -1
    row, col = p2Manager.player.get_stage_position()
    if self._combinedChain["P2"][self._chainIndex][row][col-3] and self.events["P2VULNERABLE"]:
      self.events["P2HIT"] = True
      self.events["P2VULNERABLE"] = False
      self._p2HitCounter = -1
    self._p1HitCounter += 1
    self._p2HitCounter += 1


###################################################################################
#                                 Event Manager                                   #
###################################################################################

class EventManager:
  def __init__(self):
    self._environmentManager = EnvironmentManager()
    self._initialize_players()
    self._initialize_environments()
    self._position_players()
    self._initialize_state_variables()
    self._combatManager = CombatManager()
  
  def reset(self):
    self._initialize_players()
    self._initialize_environments()
    self._position_players()
    self._combatManager = CombatManager()
    self.RESET = False
    self._pause = False

  def _initialize_players(self) -> None:
    """Create a folder and assign it to two new player objects"""
    p2Chips = []
    used = []
    while len(p2Chips) < 15:
      id = randint(0, 119)
      if id not in used:
        chip = ChipLibrary.get_chip(id)
        p2Chips.append(chip)
        used.append(id)
    p2Folder = Folder(p2Chips)
    self._playerFolder = self._to_folder(Save.attribute("playerFolder"))

    player1 = Player(self._playerFolder)
    player2 = Bot(p2Folder)
    player2.move((1, 4))

    self._p1Manager = PlayerManager(player1, (0, 2))
    self._p2Manager = PlayerManager(player2, (3, 5))

  def _position_players(self) -> None:
    """Position player assets at starting position"""
    status = self._environmentManager.get_environment("PAL").status
    self._environmentManager.get_environment("PAL").activate()
    self._move_p1((0, 0))
    self._move_p2((0, 0))
    self._environmentManager.get_environment("PAL").status = status

  def _initialize_environments(self) -> None:
    """Intanciate an object for each environment and add them to environments list"""
    self._environmentManager.add_environment("BE", BackgroundEnvironment)
    self._environmentManager.add_environment("SE", StageEnvironment)
    self._environmentManager.add_environment("SAL", StageLayer)
    self._environmentManager.add_environment("PAL", PlayerLayer, self._p1Manager.player, self._p2Manager.player)
    self._environmentManager.add_environment("GOE", GameOverEnvironment)
    self._environmentManager.add_environment("VE", VictoryEnvironment)
    self._environmentManager.add_environment("CAM", ChipMenu, self._p1Manager.player.get_folder(), self._confirm)
    self._environmentManager.add_environment("PM", PauseMenu, self._resume, self._main_menu, self.quit)
    self._environmentManager.add_environment("FAM", FolderSelectMenu, Save.attribute("playerFolder"), self._save_folder, self._close_folder_menu)
    self._environmentManager.add_environment("MM", MainMenu, self._start, self._activate_FAM, self.quit)
    self._environmentManager.get_environment("MM").activate()
    self._environmentManager.get_environment("BE").activate()
    self._environmentManager.get_environment("SE").activate()

  def _initialize_state_variables(self) -> None:
    """Initialize class state variables"""
    self.RESET = False
    self._pause = False
    self._shiftActive = False
    self._ctrlActive = False
    self._dodgeCounter = 0

  ###################################################################
  #                           Events                                #
  ###################################################################

  def event_scan(self) -> None:
    """Scan action environments for non-pygame events"""
    if self._pause:
      return
    
    if self._combatManager.events["P1READY"] and not self._combatManager.events["P2READY"]:
      p2ChipOrder = self._p2Manager.player.select_chips()
      self._combatManager.load_p2_chip_order(p2ChipOrder)

    if self._combatManager.events["P1READY"] and self._combatManager.events["P2READY"]:
      if self._combatManager.events["HIGHLIGHT"]:
        vector = self._p2Manager.player.idle()
        self._dodgeCounter = 0
      elif self._dodgeCounter > SWITCH-3:
        vector = self._p2Manager.player.dodge()
      else:
        vector = (0, 0)
        self._dodgeCounter += 1
      self._move_p2(vector)

      self._combatManager.initialize_combat()
      SAL = self._environmentManager.get_environment("SAL")
      self._combatManager.combat(SAL, self._p1Manager, self._p2Manager)
      if self._combatManager.events["P1HIT"]:
        self._p1Manager.damage_player()
        self._damage_event()
        self._combatManager.events["P1HIT"] = False
      if self._combatManager.events["P2HIT"]:
        self._p2Manager.damage_player()
        self._damage_event()
        self._combatManager.events["P2HIT"] = False
    elif self._environmentManager.get_environment("SAL").status == Environment.ACTIVE:
      self._activate_CAM()
  
  def _activate_CAM(self) -> None:
    PAL = self._environmentManager.get_environment("PAL")
    PAL.pause()
    SAL = self._environmentManager.get_environment("SAL")
    SAL.pause()
    BE = self._environmentManager.get_environment("BE")
    BE.pause()
    CAM = self._environmentManager.get_environment("CAM")
    CAM.resize(self._environmentManager.get_window_size())
    CAM.activate()

  def _activate_FAM(self) -> None:
    FAM = self._environmentManager.get_environment("FAM")
    MM = self._environmentManager.get_environment("MM")
    FAM.activate()
    MM.deactivate()

  def refresh(self) -> None:
    """Draw the next frame"""
    self._environmentManager.update()
  
  def resize(self) -> None:
    """Resize assets to window"""
    self._environmentManager.resize()
    self._position_players()

  def click(self, position : tuple) -> None:
    """Process a click event"""
    x, y = position
    self._check_buttons(x, y)
  
  def key_press(self, key) -> None:
    """Process a key-press event"""
    if key == pygame.K_UP:
      self._move_p1((-1, 0))
    elif key == pygame.K_DOWN:
      self._move_p1((1, 0))
    elif key == pygame.K_LEFT:
      self._move_p1((0, -1))
    elif key == pygame.K_RIGHT:
      self._move_p1((0, 1))
    elif key == pygame.K_ESCAPE:
      self._pause_game()
    elif key == pygame.K_LSHIFT or key == pygame.K_RSHIFT:
      self._shiftActive = True
      CAM = self._environmentManager.get_environment("CAM")
      CAM.get_events()["FAST"]()
    elif key == pygame.K_LCTRL or key == pygame.K_RCTRL:
      self._ctrlActive = True
      CAM = self._environmentManager.get_environment("CAM")
      CAM.get_events()["SLOW"]()
  
  def key_release(self, key) -> None:
    if key == pygame.K_LSHIFT or key == pygame.K_RSHIFT:
      self._shiftActive = False
      CAM = self._environmentManager.get_environment("CAM")
      CAM.get_events()["STANDARD"]()
    elif key == pygame.K_LCTRL or key == pygame.K_RCTRL:
      self._ctrlActive = False
      CAM = self._environmentManager.get_environment("CAM")
      CAM.get_events()["STANDARD"]()

  ###################################################################
  #                      Menu Button Events                         #
  ###################################################################

  def _start(self) -> None:
    """Start button event"""
    self._activate_CAM()
    SE = self._environmentManager.get_environment("SE")
    SE.deactivate()
    MM = self._environmentManager.get_environment("MM")
    MM.deactivate()
    self._environmentManager.resize()

  def _confirm(self) -> None:
    """Button event for confirming current chip order in CAM"""
    BE = self._environmentManager.get_environment("BE")
    BE.activate()
    PAL = self._environmentManager.get_environment("PAL")
    PAL.activate()
    SAL = self._environmentManager.get_environment("SAL")
    SAL.activate()
    CAM = self._environmentManager.get_environment("CAM")
    self._combatManager.load_p1_chip_order(CAM.export_chip_order())
    CAM.get_events()["CONFIRM"]()

  def _pause_game(self) -> None:
    """Pause all active environmeents and  activate pause menu"""
    if self._environmentManager.get_environment("MM").status == Environment.ACTIVE:
      return
    self._save_state()
    self._pause_all_active()
    self._environmentManager.get_environment("PM").activate()
    self._pause = True
  
  def _save_state(self) -> None:
    """Save the current status of all environments"""
    self._state = []
    environments = self._environmentManager._environments
    for key in environments.keys():
      if environments[key].status != Environment.INACTIVE:
        self._state.append((key, environments[key].status))
  
  def _load_state(self) -> None:
    """Set the status of all environments to the previous save state"""
    for key, status in self._state:
      self._environmentManager.get_environment(key).status = status
  
  def _resume(self) -> None:
    """Resume game from pause menu"""
    self._environmentManager.get_environment("PM").deactivate()
    self._load_state()
    self._pause = False
  
  def _main_menu(self) -> None:
    """Reset game"""
    self.reset()
  
  def quit(self) -> None:
    """Quit game"""
    Save.write()
    pygame.event.post(pygame.event.Event(pygame.QUIT))

  def _save_folder(self) -> None:
    """Save folder created in folder menu"""
    FAM = self._environmentManager.get_environment("FAM")
    if FAM.get_events()["SAVE"]():
      newFolder = FAM.get_folder()
      self._playerFolder = self._to_folder(newFolder)
      CAM = self._environmentManager.get_environment("CAM")
      CAM.set_folder(self._playerFolder)
      Save.attributes["playerFolder"] = deep_copy(FAM.get_folder())
  
  def _to_folder(self, indexList : list) -> Folder:
    """Convert list of chip ids to folder object"""
    chips = []
    for index in indexList:
      chip = ChipLibrary.get_chip(index)
      chips.append(chip)
    folder = Folder(chips)
    return folder
  
  def _close_folder_menu(self) -> None:
    """Close folder menu and open main menu"""
    FAM = self._environmentManager.get_environment("FAM")
    FAM.set_folder(Save.attribute("playerFolder"))
    FAM.deactivate()
    MM = self._environmentManager.get_environment("MM")
    MM.activate()

  ###################################################################
  #                           Buttons                               #
  ###################################################################

  def _check_buttons(self, x : int, y : int) -> None:
    """Check for button press in an active menu"""
    activeMenu = self._environmentManager.active_menu()
    if activeMenu:
      buttons = activeMenu.get_buttons()
      self._check_for_press(buttons, x, y)

  def _check_for_press(self, buttons : dict, x : int, y : int) -> None:
    """Determine if a button has been clicked and call its event if so"""
    for button in buttons.keys():
      if self._in_range(x, y, button.xRange, button.yRange):
        buttons[button]()
        break

  def _in_range(self, x : int, y : int, xRange : tuple, yRange : tuple) -> bool:
    """Return true if in range, false otherwise"""
    if x > xRange[0] and x < xRange[1] and y > yRange[0] and y < yRange[1]:
        return True
    return False

  ###################################################################
  #                          Movement                               #
  ###################################################################

  def _move_p1(self, movement : tuple) -> None:
    """Move p1 by a given movement vector"""
    PAL = self._environmentManager.get_environment("PAL")
    if PAL.status != Environment.ACTIVE:
      return
    SAL = self._environmentManager.get_environment("SAL")
    panelMatrix = SAL.get_panel_matrix()
    windowSize = self._environmentManager.get_window_size()
    self._p1Manager.move_player(panelMatrix, windowSize, movement)
    self.movement_event()
  
  def _move_p2(self, movement : tuple) -> None:
    """Move p2 by a given movement vector"""
    PAL = self._environmentManager.get_environment("PAL")
    if PAL.status != Environment.ACTIVE:
      return
    SAL = self._environmentManager.get_environment("SAL")
    panelMatrix = SAL.get_panel_matrix()
    windowSize = self._environmentManager.get_window_size()
    self._p2Manager.move_player(panelMatrix, windowSize, movement)
    self.movement_event()

  def movement_event(self) -> None:
    """Trigger MOVEMENT event in PlayerActionLayer"""
    PAL = self._environmentManager.get_environment("PAL")
    windowSize = self._environmentManager.get_window_size()
    player1 = self._p1Manager.player
    player2 = self._p2Manager.player
    PAL.get_events()["MOVEMENT"](windowSize, player1, player2)

  ###################################################################
  #                           Damage                                #
  ###################################################################

  def _damage_event(self) -> None:
    """Trigger DAMAGE event in PlayerActionLayer"""
    PAL = self._environmentManager.get_environment("PAL")
    windowSize = self._environmentManager.get_window_size()
    player1 = self._p1Manager.player
    player2 = self._p2Manager.player
    PAL.update(windowSize, player1, player2)

    p1State = self._p1Manager.events["HPZERO"]
    p2State = self._p2Manager.events["HPZERO"]
    if p1State:
      self._game_over()
      self._pause_all_active()
    elif p2State:
      self._victory()
      self._pause_all_active()
  
  def _pause_all_active(self):
    environments = self._environmentManager._environments
    for key in environments.keys():
      if environments[key].status == Environment.ACTIVE:
        environments[key].pause()
  
  def _game_over(self):
    self._environmentManager.get_environment("GOE").activate()
    self._environmentManager.get_environment("BE").pause()
    self._environmentManager.get_environment("SAL").pause()
    self._environmentManager.get_environment("PAL").pause()
    self.RESET = True
    self._pause = True
  
  def _victory(self):
    self._environmentManager.get_environment("VE").activate()
    self._environmentManager.get_environment("BE").pause()
    self._environmentManager.get_environment("SAL").pause()
    self._environmentManager.get_environment("PAL").pause()
    self.RESET = True
    self._pause = True
