ROWS = 3
COLS = 6

class Matrix:
  def __init__(self, data : list):
    self._matrix = data
  
  def append(self, list : list) -> None:
    self._matrix.append(list)

  def clear(self) -> None:
    rows = len(self._matrix)
    for row in range(rows):
      self._matrix[row] = [False]*len(self._matrix[row])

  def __getitem__(self, key : int):
    return self._matrix[key]
  
  def __str__(self) -> str:
    string = "[ "
    for row in range(len(self._matrix)):
      for col in range(len(self._matrix[row])):
        if self._matrix[row][col]:
          string += "1 "
        else:
          string += "0 "
      if not (row == len(self._matrix)-1):
        string += "\n  "
    string += "]\n"
    return string
  
  def __len__(self) -> int:
    return len(self._matrix)


class Chain:
  def __init__(self):
    self._matrixList = []
  
  def append(self, matrix : Matrix) -> None:
    self._matrixList.append(matrix)

  def clear(self) -> None:
    self._matrixList.clear()

  def pop(self, index : int) -> Matrix:
    return self._matrixList.pop(index)

  def __getitem__(self, key : int) -> Matrix:
    return self._matrixList[key]
  
  def __str__(self) -> str:
    string = "[\n"
    for matrix in self._matrixList:
      string += str(matrix) + ",\n"
    string += "]"
    return string

  def __len__(self) -> int:
    return len(self._matrixList)

class ParallelChains:
  def __init__(self):
    self._chainDict = {}

  def add_chain(self, key, chain : Chain) -> None:
    """Add chain at key if key not already used"""
    if not key in self._chainDict.keys():
      self._chainDict[key] = chain

  def clear(self) -> None:
    self._chainDict.clear()

  def merge(self, index : int) -> Matrix:
    mergedMatrix = Matrix([])
    for row in range(ROWS):
      mergedRow = []
      for key in self.keys():
        mergedRow += self._chainDict[key][index][row]
      mergedMatrix.append(mergedRow)
    return mergedMatrix

  def __len__(self):
    if len(self.keys()) == 0:
      return 0
    firstChainKey = tuple(self.keys())[0]
    length = len(self._chainDict[firstChainKey])
    return length

  def __getitem__(self, key) -> Chain:
    return self._chainDict[key]

  def __setitem__(self, key, chain : Chain) -> None:
    self._chainDict[key] = chain

  def keys(self):
    return self._chainDict.keys()