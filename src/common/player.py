from common.chips import Folder
from random import randint

class Player:
  MAXHEALTH = 3

  def __init__(self, folder : Folder):
    self._folder = folder
    self._health = Player.MAXHEALTH
    self._stage_position = (1, 1)
    self._asset_position = (0, 0)
  
  def move(self, position : tuple) -> None:
    """Set player stage position to a given position"""
    self._stage_position = position
  
  def move_asset(self, position : tuple) -> None:
    """Set player asset position to a given position"""
    self._asset_position = position

  def damage(self) -> None:
    """Decrement player health"""
    self._health -= 1

  def get_folder(self) -> Folder:
    """Return player folder"""
    return self._folder

  def get_health(self) -> int:
    """Return player health"""
    return self._health
  
  def get_stage_position(self) -> tuple:
    """Return player stage position"""
    return self._stage_position
  
  def get_asset_position(self) -> tuple:
    "Return player asset position"
    return self._asset_position

class Bot(Player):
  def __init__(self, folder : Folder):
    super().__init__(folder)
    self.hitOrder = []
    self._route = []
    self._errorRate = 3
    self._movementCooldown = 2
    self._frameCounter = 0
  
  ###################################################################
  #                            Actions                              #
  ###################################################################

  def analyze(self) -> None:
    """Determine the route to nearest safe panel"""
    if len(self.hitOrder) == 0:
      return
    
    vector = self._nearest_safe_panel(self.hitOrder[0])
    self._route.clear()
    # Movement to safe row position
    while vector[0] != 0:
      if vector[0] < 0:
        self._route.append((-1, 0))
        vector[0] += 1
      else:
        self._route.append((1, 0))
        vector[0] -= 1
    # Movement to safe col position
    while vector[1] != 0:
      if vector[1] < 0:
        self._route.append((0, -1))
        vector[1] += 1
      else:
        self._route.append((0, 1))
        vector[1] -= 1
  
  def dodge(self) -> tuple:
    """Return next movement vector on route"""
    if self._frameCounter < self._movementCooldown:
      self._frameCounter += 1
      return (0, 0)

    self._frameCounter = 0
    if len(self._route) == 0:
      return self.idle()
    rand = randint(1, 10)
    if rand <= self._errorRate:
      vectors = [(1, 0), (-1, 0), (0, 1), (0, -1)]
      rand = randint(0, 3)
      return vectors[rand]
    return self._route.pop(0)
  
  def idle(self) -> tuple:
    """Random movement"""
    if self._frameCounter < self._movementCooldown:
      self._frameCounter += 1
      return (0, 0)
    self._frameCounter = 0
    vectors = [(1, 0), (-1, 0), (0, 1), (0, -1)]
    rand = randint(0, 3)
    return vectors[rand]

  def select_chips(self) -> list:
    """Build chip order"""
    self._folder.shuffle()
    chipOrder = []
    for i in range(5):
      chip = self._folder.draw()
      chipOrder.append(chip)
    return chipOrder
  
###################################################################
#                            Helpers                              #
###################################################################

  def _nearest_safe_panel(self, hitMatrix : list) -> list:
    """Returns a vector to the nearest safe panel"""
    nearestRow = -1
    nearestCol = -1
    minRowDist = 10
    minColDist = 10
    for row in range(len(hitMatrix)):
      for col in range(3, len(hitMatrix[row])):
        if not hitMatrix[row][col]:
          rowDist = abs(row - self._stage_position[0])
          colDist = abs(col - self._stage_position[1])
          if (rowDist + colDist) < (minRowDist + minColDist):
            nearestRow = row
            nearestCol = col
            minRowDist = rowDist
            minColDist = colDist
    x = nearestRow - self._stage_position[0]
    y = nearestCol - self._stage_position[1]
    vector = [x, y]
    return vector