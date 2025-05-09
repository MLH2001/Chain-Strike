from random import randint
from common.graphics import Asset, Colors
from common.containers import Matrix

class Chip:
  # Number of frames panels are highlighted
  FASTHIGHLIGHT = 5
  STANDARDHIGHLIGHT = 10
  SLOWHIGHLIGHT = 30

  def __init__(self, asset : Asset, areaMatrix : list):
    self._asset = asset
    self._areaMatrix = Matrix(areaMatrix)
    self._invertedMatrix = Matrix(self._invert_matrix())
    self.highlightFrames = Chip.STANDARDHIGHLIGHT
    self.highlightColor = Colors.ORANGE

  def fast(self) -> None:
   """Set highlightFrames to fast"""
   self.highlightFrames = Chip.FASTHIGHLIGHT
   self.highlightColor = Colors.RED
  
  def standard(self) -> None:
   """Set highlightFrames to standard"""
   self.highlightFrames = Chip.STANDARDHIGHLIGHT
   self.highlightColor = Colors.ORANGE

  def slow(self) -> None:
   """Set highlightFrames to slow"""
   self.highlightFrames = Chip.SLOWHIGHLIGHT
   self.highlightColor = Colors.YELLOW

  def get_asset(self):
    """Return chip asset"""
    return self._asset
  
  def get_area_matrix(self) -> list:
    """Return chip areaMatrix"""
    return self._areaMatrix
  
  def get_inverted_matrix(self) -> list:
    """Return chip invertedMatrix"""
    return self._invertedMatrix
  
  def _invert_matrix(self) -> list:
    """Invert areaMatrix"""
    invertedMatrix = [
      [False, False, False],
      [False, False, False],
      [False, False, False]
    ]
    for row in range(len(invertedMatrix)):
      for col in range(len(invertedMatrix[row])):
        c = len(invertedMatrix[row]) - (col + 1)
        invertedMatrix[row][col] = self._areaMatrix[row][c]
    return invertedMatrix

class Folder:
  def __init__(self, chips : list):
    self._chips = chips
  
  def shuffle(self) -> None:
    """Shuffle chips list"""
    swaps = len(self._chips) * 2
    maxIndex = len(self._chips) - 1
    for i in range(swaps):
      index1 = randint(0, maxIndex)
      index2 = randint(0, maxIndex)
      while index1 == index2:
        index2 = randint(0, maxIndex)
      self._swap(index1, index2)
  
  def _swap(self, index1 : int, index2 : int) -> None:
    """Swap chips at the given indices"""
    chip1 = self._chips[index1]
    chip2 = self._chips[index2]
    self._chips[index1] = chip2
    self._chips[index2] = chip1
  
  def draw(self) -> Chip:
    """Return chip at index 0 and place it at index -1"""
    chip = self._chips.pop(0)
    self._chips.append(chip)
    return chip
