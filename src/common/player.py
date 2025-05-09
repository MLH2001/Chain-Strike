from common.chips import Folder
from common.containers import Matrix, Chain
from random import randint

EMPTYMATRIX = Matrix([[False]*3]*3)

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
    self.hitOrder = Chain()
    self._route = []
    self._errorRate = 5
    self._movementCooldown = 2
    self._frameCounter = 0

  ###################################################################
  #                            Actions                              #
  ###################################################################

  def analyze(self) -> None:
    """Determine the route for the bot to take"""
    self._route.clear()
    position = self._stage_position
    for i in range(len(self.hitOrder)):
      currentHit = self.hitOrder[i]
      nextHit = EMPTYMATRIX
      if i + 1 < len(self.hitOrder):
        nextHit = self.hitOrder[i+1]
      safePanels = self._safe_panels(nextHit)
      safeSteps = self._safe_steps(currentHit, position)
      bestStep = self._best_step(safeSteps, safePanels)
      self._route.append(self._vector(bestStep, position))
      position = bestStep

  def dodge(self) -> tuple:
    """Return next movement vector on route"""
    self._frameCounter = 0
    if len(self._route) == 0:
      return self.idle()
    rand = randint(1, 100)
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
      rand = randint(0, 2)
      if rand == 0:
        chip.fast()
      elif rand == 1:
        chip.standard()
      elif rand == 2:
        chip.slow()
      chipOrder.append(chip)
    return chipOrder
  
###################################################################
#                            Helpers                              #
###################################################################

  def _best_step(self, steps : list, safePanels : list) -> tuple:
    """Return best step to take in safe steps list"""
    if len(steps) == 0:
      return (0, 0)
    
    bestStep = (0, 0)
    minDist = 10
    for step in steps:
      dist = self._nearest_safe_panel(safePanels, step)
      if dist < minDist:
        bestStep = step
        minDist = dist
    return bestStep

  def _safe_panels(self, nextHit : Matrix) -> list:
    """Return a list of all panels safe to stand on"""
    safePanels = []
    for row in range(len(nextHit)):
      for col in range(len(nextHit[row])):
        if not nextHit[row][col]:
          safePanels.append((row, col+3))
    return safePanels
  
  def _safe_steps(self, currentHit : Matrix, position : tuple) -> tuple:
    """Return a list of safe movement options"""
    possibleSteps = [(0, 0), (-1, 0), (0, -1), (1, 0), (0, 1)]
    safeSteps = []
    row, col = position
    for step in possibleSteps:
      stepRow = row + step[0]
      stepCol = col + step[1]
      if not (0 <= stepRow < 3) or not (3 <= stepCol < 6):
        continue
      if not currentHit[stepRow][stepCol-3]:
        safeSteps.append((stepRow, stepCol))
    return safeSteps

  def _vector(self, endPoint : tuple, position : tuple) -> tuple:
    """Conveert a point to a movement vector"""
    endX, endY = endPoint
    x, y = position
    return (endX-x, endY-y)

  def _nearest_safe_panel(self, safePanels : list, position : tuple) -> list:
    """Returns the distance to the nearest safe panel"""
    minDist = 10
    for panel in safePanels:
      dist = self._distance(position, panel)
      if dist < minDist:
        minDist = dist
    return minDist
  
  def _distance(self, point1 : tuple, point2 : tuple) -> int:
    """Return distance between two points"""
    xDist = abs(point2[0] - point1[0])
    yDist = abs(point2[1] - point1[1])
    return xDist + yDist