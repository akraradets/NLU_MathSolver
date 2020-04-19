from systems.LoggerFactory import LoggerFactory

class DeductiveSolver:
  def __init__(self):
    self.logger = LoggerFactory(self).getLogger()

  def solve(self):
    