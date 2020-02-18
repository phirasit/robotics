import math

class Robot:
  def __init__(self, FOV, sensorRange, setLeftMotor, setRightMotor):
    super()
    self.FOV           = FOV
    self.sensorRange   = sensorRange
    self.setLeftMotor  = setLeftMotor
    self.setRightMotor = setRightMotor

    self.x = self.y = None
    self.angle = None

  def position(self):
    return self.x, self.y

  def has_info(self):
    return self.x != None and self.y != None and self.angle != None

  def update_position(self, position):
    self.x, self.y, self.z = position

  def update_angle(self, angle):
    self.angle = angle

  def gen_wall_position(self, depth, width, height):
    if not self.has_info():
      return []

    n = len(depth)
    positions = [(self.x, self.y)]
    for i, d in enumerate(depth):
      angle = (i / (n-1) - 0.5) * self.FOV
      d2 = d * math.tan(angle)
      x = self.x + (d * math.cos(self.angle) + d2 * math.cos(self.angle + math.pi / 2)) / width
      y = self.y + (d * math.sin(self.angle) + d2 * math.sin(self.angle + math.pi / 2)) / height
      positions.append((x, y))
    return positions


