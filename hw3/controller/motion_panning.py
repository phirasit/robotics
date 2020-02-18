import math
import random
from vector import Vector

MOTION_PANNING_INIT      = 0
MOTION_PANNING_GO        = 1
MOTION_PANNING_ROTATE    = 2
MOTION_PANNING_FIND_PATH = 3
MOTION_PANNING_ROTATE    = 4
MOTION_PANNING_FINISH    = 5

class MotionPanning:
  def __init__(self, grid, robot):
    super()

    self.state = MOTION_PANNING_INIT
    self.grid  = grid
    self.robot = robot

    self.parent = dict()
    self.target = None

  def update(self):
    if self.state == MOTION_PANNING_INIT:
      self.state_init()
    elif self.state == MOTION_PANNING_GO:
      self.state_go()
    elif self.state == MOTION_PANNING_FIND_PATH:
      self.state_find_path()
    elif self.state == MOTION_PANNING_ROTATE:
      self.state_rotate()
    elif self.state == MOTION_PANNING_FINISH:
      self.state_finish()
    else:
      raise 'Invalid Motion Panning State: {}'.format(self.state)

  def state_init(self):
    if self.robot.has_info():
      self.target = self.robot.position()
      print (self.target)
      self.parent[self.target] = None
      self.state  = MOTION_PANNING_GO

  def is_wall(self, x, y):
    x = math.floor(x * self.grid.N)
    y = math.floor(y * self.grid.N)
    return self.grid.grid[y][x] > 0.3

  def is_empty(self, x, y):
    x = math.floor(x * self.grid.N)
    y = math.floor(y * self.grid.N)
    return self.grid.grid[y][x] < -0.3

  def is_undecided(self, x, y):
    return not self.is_wall(x, y) and not self.is_empty(x, y)

  def state_go(self):
    if Vector.distance(Vector.minus(self.robot.position(), self.target)) < 1e-2:
      self.state = MOTION_PANNING_FIND_PATH
      return

    self.target_angle = math.atan2(self.target[1] - self.robot.y, self.target[0] - self.robot.x)
    if self.rotate():
      return

    x, y = self.target
    dist = Vector.minus(self.robot.position(), (x, y))
    if self.is_wall(x, y) and Vector.distance(dist) < self.robot.sensorRange / 2:
      self.robot.setLeftMotor(0)
      self.robot.setRightMotor(0)
      self.state = MOTION_PANNING_FIND_PATH
    else:
      self.robot.setLeftMotor(1)
      self.robot.setRightMotor(1)

  def state_find_path(self):
    rotate_angle = None
    target = None
    for i in range(50):
      angle = math.pi * (2 * random.random() - 1.0)
      vx = math.cos(angle)
      vy = math.sin(angle)
      m  = max(self.grid.N * abs(vx), self.grid.N * abs(vy))
      vx, vy = vx / m, vy / m
      x, y = self.robot.position()
      while 0 <= x and x < 1 and 0 <= y and y < 1:
        x, y = x + vx, y + vy
        if self.is_wall(x, y):
          break
        if self.is_undecided(x, y):
          p = Vector.minus(self.robot.position(), (x, y))
          dist = Vector.distance((p[0] * self.grid.width, p[1] * self.grid.height))
          if dist < self.robot.sensorRange:
            rotate_angle = angle
          elif dist < 2 * self.robot.sensorRange:
            target = (x, y)
          break
      if rotate_angle is not None:
        break

    print ("find_path", rotate_angle, target)
    if rotate_angle is not None:
      self.target_angle = rotate_angle
      self.state = MOTION_PANNING_ROTATE
    elif target is not None:
      self.parent[target] = self.target
      self.target = target
      self.state  = MOTION_PANNING_GO
    elif self.parent[self.target] is not None:
      self.target = self.parent[self.target]
      self.state  = MOTION_PANNING_GO
    else:
      self.state  = MOTION_PANNING_FINISH

  def state_rotate(self):
    if not self.rotate():
      self.state = MOTION_PANNING_FIND_PATH

  def rotate(self):
    angle_dist = self.target_angle - self.robot.angle
    if abs(angle_dist) < 1e-1:
      return False
    if angle_dist < 0: angle_dist += 2 * math.pi
    if angle_dist < math.pi:
      angle_dist = (angle_dist) / math.pi
      self.robot.setLeftMotor(0)
      self.robot.setRightMotor(0.1 + angle_dist * 0.4)
    else:
      angle_dist = (angle_dist - math.pi) / math.pi
      self.robot.setLeftMotor(0.1 + angle_dist * 0.4)
      self.robot.setRightMotor(0)
    return True

  def state_finish(self):
    # do nothing
    pass

  def __str__(self):
    return "<<MotionPanning>>"


