import sys

class CleanUp:
  def __init__(self):
    super()
    self.func = []

  def register(self, tag, f):
    self.func.append((tag, f))

  def pop(self):
    tag, f = self.func.pop()
    print (tag, '...', end=' ', file=sys.stderr)
    sys.stderr.flush()
    f()
    print ('done', file=sys.stderr)

  def cleanup(self):
    print ('start cleanup' , file=sys.stderr)
    while len(self.func) > 0:
      self.pop()
    print ('finish cleanup', file=sys.stderr)
