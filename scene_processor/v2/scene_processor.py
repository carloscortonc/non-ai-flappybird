import threading
import numpy as np
import dxcam

PIPE_BBOX = [1190, 306, 1, 444]
BIRD_BBOX = [925, 315, 1, 550]
EXITING_PIPE_BBOX = [BIRD_BBOX[0], PIPE_BBOX[1], 1, 1]

PIPE_SEPARATION = 160

class SceneProcessor:
  def __init__(self, onupdate):
    self.cam = dxcam.create()
    self.pipe_height_last = False
    self.pipe_exit_last = False
    self.pipes = []
    self.bird_height = 0
    self.onupdate = onupdate
    threading.Thread(target=self.capture).start()

  def capture(self):
    var = True
    while var:
      self.captureFrame()
      # var = False

  def captureFrame(self):
    # self.capturePipeHeight()
    # self.captureExitingPipe()
    self.captureBirdPosition()
    u = {"bird": self.bird_height, "pipe": self.pipes[0] + PIPE_SEPARATION if self.pipes.__len__() > 0 else 320}
    self.onupdate(u)

  isPipe = lambda _, pipe, col : pipe[col][0][2] != 206

  def capturePipeHeight(self):
    pipe = self.captureElement(PIPE_BBOX)
    if pipe is None:
      return
    if self.isPipe(pipe, 0) and not self.pipe_height_last:
      self.pipe_height_last = True
      pipe_height = 0
      while self.isPipe(pipe, pipe_height):
        pipe_height += 1
      self.pipes.append(pipe_height)
    elif not self.isPipe(pipe, 0):
      self.pipe_height_last = False

  def captureExitingPipe(self):
    exitingPipe = self.captureElement(EXITING_PIPE_BBOX)
    if exitingPipe is None:
        return
    if not self.isPipe(exitingPipe, 0) and self.pipe_exit_last:
      self.pipe_exit_last = False
      self.pipes.pop(0)
    elif self.isPipe(exitingPipe, 0):
      self.pipe_exit_last = True

  def captureBirdPosition(self):
    bird = self.captureElement(BIRD_BBOX)
    if bird is None:
        return
    isBird = lambda i: np.array_equal(bird[i][0], [212, 191, 39])
    self.bird_height = -1
    bird_last = False
    while True:
      self.bird_height += 1
      checkBird = isBird(self.bird_height)
      if not checkBird and bird_last:
        break
      elif checkBird:
        bird_last = True

  def captureElement(self, bbox):
    return self.cam.grab(region=(bbox[0], bbox[1], bbox[0] + bbox[2], bbox[1] + bbox[3]))

  def cleanup(self):
    print("cleanup")
    return True
