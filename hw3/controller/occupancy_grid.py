import math
import matplotlib.pyplot as plt
import numpy as np

from vector import Vector
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon


class OccupancyGrid:
  def __init__(self, N, width, height):
    super()
    self.N    = N
    self.width = width
    self.height = height

    self.grid = np.array([[0.0] * N for _ in range(N)])
    self.obj  = []
    self.first_draw = True
    self.finish = False
    self.fig, self.ax = plt.subplots(1)
    self.fig.canvas.mpl_connect('close_event', self.__onClick)

  def __onClick(self, event):
    self.finish = True

  def add_obj(self, obj):
    self.ax.add_patch(obj)
    self.obj.append(obj)

  """
  def update_grid(self, r, c, data):
    for i in range(min(len(data), self.N-r)):
      for j in range(min(len(data[i]), self.N-c)):
        self.grid[r+i][c+j] += data[i][j]
  """

  def update_grid(self, pos, sensorRange):
    pos = [( \
      max(0, min(self.N-1, math.floor(p[0] * self.N))), \
      max(0, min(self.N-1, math.floor(p[1] * self.N))) \
    ) for p in pos]
    xs = [p[0] for p in pos]
    ys = [p[1] for p in pos]
    minX, maxX = min(xs), max(xs)
    minY, maxY = min(ys), max(ys)
    polygon = Polygon(pos)
    robotX, robotY = pos[0]
    w = self.width / self.N
    h = self.height / self.N
    for y in range(minY, maxY+1):
      for x in range(minX, maxX+1):
        if polygon.contains(Point(x, y)):
          # inside polygon
          self.grid[y][x] -= 0.2

    # highlight current position
    for i in range(-1, 2):
      for j in range(-1, 2):
        self.grid[robotY+i][robotX+j] -= 0.2

    # highlight wall
    for (x, y) in pos[1:]:
      if Vector.distance(((x - robotX) * w, (y - robotY) * h)) < sensorRange:
        self.grid[y][x] += 0.3

  def position(self, pos):
    return pos[0] * self.N + 0.5, pos[1] * self.N + 0.5

  @staticmethod
  def __sigmoid(x):
    return 1 / (1 + math.exp(-x))

  def draw(self):
    self.ax.clear()
    for obj in self.obj:
      self.ax.add_patch(obj)

    grid = np.vectorize(self.__sigmoid)(self.grid)
    im = self.ax.imshow(grid, cmap='gray_r', vmin=0, vmax=1)
    if self.first_draw:
      self.fig.colorbar(im, orientation='horizontal')
      self.first_draw = False

    plt.xlim(0, self.N-1)
    plt.ylim(0, self.N-1)
    plt.draw()
    plt.pause(0.02)

  def show(self):
    plt.ion()
    plt.show()

  def cleanup(self):
    self.finish = True
    self.show()
    plt.ioff()
    plt.show()


