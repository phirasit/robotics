class Vector:
  @staticmethod
  def minus(p, q):
    return p[0] - q[0], p[1] - q[1]

  @staticmethod
  def cross(p, q):
    return p[0] * q[1] - p[1] * q[0]

  @staticmethod
  def isLeft(r, p, q):
    return Vector.cross(Vector.minus(r, p), Vector.minus(q, p)) < 0

  @staticmethod
  def distance(p):
    return (p[0] ** 2 + p[1] ** 2) ** 0.5
