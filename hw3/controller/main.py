import math
import sys
import time
import vrep

from occupancy_grid import *
from cleanup import *
from robot import *
from motion_panning import *

from matplotlib.patches import Circle, Polygon

# debugging function
def report(msg):
  print (msg, file=sys.stderr)

# cleanup function
cleaner = CleanUp()
def exit(code):
  cleaner.cleanup()
  sys.exit(code)

# establish connection
host = "127.0.0.1"
port = 20000

report ("Connecting to {}:{}".format(host, port))
clientID = vrep.simxStart(host, port, True, True, 3000, 5)
if clientID == -1:
  report ("Cannot connect V-REP remoteAPI server")
  exit(1)
cleaner.register('stop connection', lambda: vrep.simxFinish(clientID))
report ("Connect established")

# connect function
def connect(targetName):
  global exit, report
  returnCode, handle = vrep.simxGetObjectHandle(clientID, targetName, vrep.simx_opmode_oneshot_wait)
  if returnCode == -1:
    report("Cannot connect to {}".format(targetName))
    exit(1)
  return handle

# connect robot
robotHandle = connect("Pioneer_p3dx")
leftMotor   = connect("Pioneer_p3dx_leftMotor")
rightMotor  = connect("Pioneer_p3dx_rightMotor")

# set motor
def setMotor(motor, speed):
  vrep.simxSetJointTargetVelocity(clientID, motor, speed, vrep.simx_opmode_oneshot_wait)

setMotor(leftMotor, 0)
setMotor(rightMotor, 0)

# connect vision sensor
sensorHandle = connect("Vision_sensor")
_, sensorRange = vrep.simxGetObjectFloatParameter(clientID, sensorHandle, vrep.sim_visionfloatparam_far_clipping, vrep.simx_opmode_oneshot_wait)
report("Sensor Range = {}".format(sensorRange))

# fetch stage
stageHandle = connect("Stage")
_, stageMinX = vrep.simxGetObjectFloatParameter(clientID, stageHandle, vrep.sim_objfloatparam_modelbbox_min_x, vrep.simx_opmode_oneshot_wait)
_, stageMinY = vrep.simxGetObjectFloatParameter(clientID, stageHandle, vrep.sim_objfloatparam_modelbbox_min_y, vrep.simx_opmode_oneshot_wait)
_, stageMaxX = vrep.simxGetObjectFloatParameter(clientID, stageHandle, vrep.sim_objfloatparam_modelbbox_max_x, vrep.simx_opmode_oneshot_wait)
_, stageMaxY = vrep.simxGetObjectFloatParameter(clientID, stageHandle, vrep.sim_objfloatparam_modelbbox_max_y, vrep.simx_opmode_oneshot_wait)
stageWidth  = stageMaxX - stageMinX
stageHeight = stageMaxY - stageMinY

# create occupancy grid
GRID_SIZE = 100
grid = OccupancyGrid(GRID_SIZE, stageWidth, stageHeight)
grid.draw()
grid.show()
cleaner.register('show grid', grid.cleanup)

# create robot
robot = Robot(math.pi / 2.0, sensorRange, lambda x: setMotor(leftMotor, x), lambda x: setMotor(rightMotor, x))

# create motion panning
motion = MotionPanning(grid, robot)

# robot grid token
robotCircleToken = Circle((0, 0), 2, color='green')
robotVisionToken = Polygon([[0, 0]], True, color='red', alpha=0.5)

grid.add_obj(robotCircleToken)
grid.add_obj(robotVisionToken)

# enable sensor streaming
vrep.simxGetObjectPosition(clientID, sensorHandle, stageHandle, vrep.simx_opmode_streaming)
vrep.simxGetObjectOrientation(clientID, robotHandle, stageHandle, vrep.simx_opmode_streaming)
vrep.simxGetVisionSensorDepthBuffer(clientID, sensorHandle, vrep.simx_opmode_streaming)

try:
  while vrep.simxGetConnectionId(clientID) != -1 and not grid.finish:
    # read sensor position
    returnCode, position = vrep.simxGetObjectPosition(clientID, sensorHandle, stageHandle, vrep.simx_opmode_buffer)
    if returnCode == vrep.simx_error_noerror:
      (x, y, _) = position
      # adjust by stage size
      x, y = (x - stageMinX) / stageWidth, (y - stageMinY) / stageHeight
      robot.update_position((x, y, None))
      robotCircleToken.center = grid.position((x, y))

    # read robot orientation
    returnCode, orientation = vrep.simxGetObjectOrientation(clientID, robotHandle, stageHandle, vrep.simx_opmode_buffer)
    if returnCode == vrep.simx_error_noerror:
      (_, _, angle) = orientation
      robot.update_angle(angle)

    # read depth data
    returnCode, resolution, data = vrep.simxGetVisionSensorDepthBuffer(clientID, sensorHandle, vrep.simx_opmode_buffer)
    if returnCode == vrep.simx_error_noerror:
      # get positions from rays
      walls = robot.gen_wall_position(data, stageWidth, stageHeight)
      if len(walls) == 0:
        continue
      robotVisionToken.set_xy(list(map(grid.position, walls)))

      # update grid
      grid.update_grid(walls, sensorRange)

    # update image
    grid.draw()

    # update motion panning state
    motion.update()

    # delay time
    time.sleep(0.05)

except KeyboardInterrupt:
  print ("KeyBoardInterrupt")

exit(0)
