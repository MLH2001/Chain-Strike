import pygame
from common.window import Window
from common.environments import *
from common.menus import *
from common.action_layers import *
from common.action_menus import *
from common.player import *
from common.chips import *
from common.chip_library import ChipLibrary
from random import randint

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

class CombatManager:
  def __init__(self):
    self._frameCounter = -1
    self._highlightFrames = 10
    self._hitFrames = 1
    self._p1Vulnerable = True
    self._p2Vulnerable = True
    self.events = {
      "HIGHLIGHT" : True,
      "HIT" : False,
      "P1HIT" : False,
      "P2HIT" : False,
      "P1VULNERABLE" : True,
      "P2VULNERABLE" : True
    }
  
  def combat(self, SAL : StageLayer, p1Manager : PlayerManager, p2Manager : PlayerManager) -> None:
    """Update the combat state"""
    self._frameCounter += 1
    if self._frameCounter == 0:
      if self.events["HIGHLIGHT"]:
        self._highlight(SAL)
        self._hitMatrix = [[False]*6]*3
        if not self.events["HIGHLIGHT"]:
          p2Manager.player.hitOrder = SAL.get_hit_order()
          p2Manager.player.analyze()
          self.events["HIT"] = True
        return
      if self.events["HIT"]:
        self._hit(SAL)
        p2Manager.player.analyze()
        if self._hitMatrix == [[False]*6]*3:
          self.events["HIT"] = False
          self.events["HIGHLIGHT"] = True
    if self._frameCounter == self._highlightFrames:
      self.events["P1VULNERABLE"] = True
      self.events["P2VULNERABLE"] = True
      self._frameCounter = -1
      return
    if self.events["HIT"] and self._frameCounter == self._hitFrames:
      SAL.clear_highlight()
      self._hitMatrix = [[False]*6]*3
    
    if self.events["HIT"]:
      row, col = p1Manager.player.get_stage_position()
      if self._hitMatrix[row][col] and self.events["P1VULNERABLE"]:
        self.events["P1HIT"] = True
      row, col = p2Manager.player.get_stage_position()
      if self._hitMatrix[row][col] and self.events["P2VULNERABLE"]:
        self.events["P2HIT"] = True
  
  def _highlight(self, SAL : StageLayer) -> None:
    """Highlight next chips in chip order"""
    self.events["HIGHLIGHT"] = SAL.highlight_chip()
  
  def _hit(self, SAL : StageLayer) -> None:
    """Hit next chip in chip order"""
    self._hitMatrix = SAL.hit_chip()


###################################################################################
#                                 Event Manager                                   #
###################################################################################

class EventManager:
  def __init__(self):
    self._environmentManager = EnvironmentManager()
    self._initialize_players()
    self._initialize_environments()
    self._position_players()
    self._combatManager = CombatManager()
    self.RESET = False
    self._pause = False
  
  def reset(self):
    self._initialize_players()
    self._initialize_environments()
    self._position_players()
    self._combatManager = CombatManager()
    self.RESET = False
    self._pause = False

  def _initialize_players(self) -> None:
    """Create a folder and assign it to two new player objects"""
    chips = []
    used = []
    while len(chips) < 15:
      id = randint(210, 419)
      if id not in used:
        chip = ChipLibrary.get_chip(id)
        chips.append(chip)
        used.append(id)
    folder = Folder(chips)

    player1 = Player(folder)
    player2 = Bot(folder)
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
    self._environmentManager.add_environment("CAM", ChipMenu, self._p1Manager.player.get_folder())
    self._environmentManager.add_environment("PM", PauseMenu, self._resume, self._main_menu, self._quit)
    self._environmentManager.add_environment("MM", MainMenu)
    self._environmentManager.get_environment("MM").activate()
    self._environmentManager.get_environment("BE").activate()
    self._environmentManager.get_environment("SE").activate()

  ###################################################################
  #                           Events                                #
  ###################################################################

  def event_scan(self) -> None:
    """Scan action environments for non-pygame events"""
    if self._pause:
      return
    
    SAL = self._environmentManager.get_environment("SAL")
    stageEvents = SAL.get_events()
    if stageEvents["P1READY"] and not stageEvents["P2READY"]:
      p2ChipOrder = self._p2Manager.player.select_chips()
      SAL.load_p2_chip_order(p2ChipOrder)

    inCombat = False
    if stageEvents["P1READY"] and stageEvents["P2READY"]:
      inCombat = True
      SAL = self._environmentManager.get_environment("SAL")
      self._combatManager.combat(SAL, self._p1Manager, self._p2Manager)
      if self._combatManager.events["P1HIT"]:
        self._p1Manager.damage_player()
        self._damage_event()
        self._combatManager.events["P1HIT"] = False
        self._combatManager.events["P1VULNERABLE"] = False
      if self._combatManager.events["P2HIT"]:
        self._p2Manager.damage_player()
        self._damage_event()
        self._combatManager.events["P2HIT"] = False
        self._combatManager.events["P2VULNERABLE"] = False
    elif self._environmentManager.get_environment("SAL").status == Environment.ACTIVE:
      self._environmentManager.get_environment("CAM").activate(self._environmentManager)
    
    if inCombat:
      if self._combatManager.events["HIGHLIGHT"]:
        vector = self._p2Manager.player.idle()
      else:
        vector = self._p2Manager.player.dodge() 
      self._move_p2(vector)
  
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
  
  def _resume(self, *args) -> None:
    """Resume game from pause menu"""
    self._environmentManager.get_environment("PM").deactivate()
    self._load_state()
    self._pause = False
  
  def _main_menu(self, *args) -> None:
    """Reset game"""
    self.reset()
  
  def _quit(self, *args) -> None:
    """Quit game"""
    pygame.event.post(pygame.event.Event(pygame.QUIT))

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
        buttons[button](self._environmentManager)
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
