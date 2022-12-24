import numpy as np
import dxcam

GAME_WIDTH = 479
GAME_HEIGHT = 550
GAME_BBOX = [0, 0, GAME_WIDTH, GAME_HEIGHT]
PIPE_RELATIVE = [GAME_WIDTH  - 1, 0, 1, 444]
BIRD_RELATIVE = [206, 9, 1, GAME_HEIGHT - 1]
EXITING_PIPE_RELATIVE = [BIRD_RELATIVE[0] - 1, PIPE_RELATIVE[1], 1, 1]
EXISTING_PIPE_OFFSET_UP = 25
EXISTING_PIPE_OFFSET_DOWN = 14

PIPE_SEPARATION = 160
BIRD_MARGIN = 64

class SceneProcessor:
  def __init__(self, onupdate):
    self.cam = dxcam.create()
    self.pipe_height_last = False
    self.pipe_exit_last = False
    self.pipes = []
    self.bird_height = 0
    self.next_up = False
    self.onupdate = onupdate
    # read game dimensions
    self.readDimensions()
    # start capturing process
    self.capture()

  def readDimensions(self):
    screen = self.cam.grab()
    screenHeight = len(screen); screenWidth = len(screen[0])
    startX = 0; startY = 0

    isGameSky = lambda color : np.array_equal(color, [112, 197, 206])
    try:
      # find x value
      while(not isGameSky(screen[round(screenHeight / 2)][startX])):
        startX += 1
      GAME_BBOX[0] = startX
      # find y value
      while(not isGameSky(screen[startY][round(screenWidth / 2)])):
        startY += 1
      GAME_BBOX[1] = startY
    except IndexError:
      print("Error locating game dimensions")
      exit(1)
    print("GAME DIMENSIONS:", GAME_BBOX)

  def capture(self):
    while True:
      self.captureFrame()

  def captureFrame(self):
    game = self.captureElement(GAME_BBOX)
    if game is None:
      return
    self.capturePipeHeight(game)
    self.captureExitingPipe(game)
    self.captureBirdPosition(game)

    bird = self.bird_height + BIRD_MARGIN
    pipe = self.pipes[0] + PIPE_SEPARATION if self.pipes.__len__() > 0 else 320
    self.onupdate({ "bird": bird, "pipe": pipe})

  isPipe = lambda _, pipe, col, row : pipe[col][row][2] != 206

  def capturePipeHeight(self, game):
    if self.isPipe(game, PIPE_RELATIVE[1], PIPE_RELATIVE[0]) and not self.pipe_height_last:
      self.pipe_height_last = True
      pipe_height = 0
      while self.isPipe(game, pipe_height + PIPE_RELATIVE[1], PIPE_RELATIVE[0]):
        pipe_height += 1
      self.next_up = len(self.pipes) > 0 and self.pipes[0] > pipe_height
      self.pipes.append(pipe_height)
      print("[PIPE:ADD]", self.pipes)
    elif not self.isPipe(game, PIPE_RELATIVE[1], PIPE_RELATIVE[0]):
      self.pipe_height_last = False

  def captureExitingPipe(self, game):
    xOffset = EXISTING_PIPE_OFFSET_UP if self.next_up else EXISTING_PIPE_OFFSET_DOWN
    isExitingPipe = self.isPipe(game, EXITING_PIPE_RELATIVE[1], EXITING_PIPE_RELATIVE[0] - xOffset)
    if not isExitingPipe and self.pipe_exit_last:
      self.pipe_exit_last = False
      self.pipes.pop(0)
      print("[PIPE:REMOVE]", self.pipes)
    elif isExitingPipe:
      self.pipe_exit_last = True

  def captureBirdPosition(self, game):
    isBird = lambda i: np.array_equal(game[i + BIRD_RELATIVE[1]][BIRD_RELATIVE[0]], [212, 191, 39])
    bheight = -1
    bird_last = False
    while True:
      bheight += 1
      try:
        checkBird = isBird(bheight)
      except IndexError:
        break
      if not checkBird and bird_last:
        self.bird_height = bheight
        break
      elif checkBird:
        bird_last = True

  def captureElement(self, bbox):
    return self.cam.grab(region=(bbox[0], bbox[1], bbox[0] + bbox[2], bbox[1] + bbox[3]))

  def cleanup(self):
    print("cleanup")
    return True
