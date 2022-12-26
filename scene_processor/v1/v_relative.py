import threading
import numpy as np
import asyncio

import win32gui
import win32ui
import win32con

GAME_WIDTH = 479
GAME_HEIGHT = 550
GAME_BBOX = [0, 0, GAME_WIDTH, GAME_HEIGHT]
PIPE_RELATIVE = [GAME_WIDTH  - 1, 0, 1, 444]
BIRD_RELATIVE = [263, 9, 1, GAME_HEIGHT - 1]
EXITING_PIPE_RELATIVE = [BIRD_RELATIVE[0] - 35, PIPE_RELATIVE[1], 1, 1]
EXISTING_PIPE_OFFSET_UP = 20
EXISTING_PIPE_OFFSET_DOWN = 7

BIRD_MARGIN = 40
PIPE_VERTICAL_DISTANCE = 160

class SceneProcessor:
  def __init__(self, onupdate):
    self.pipe_height_last = False
    self.pipe_exit_last = False
    self.next_up = False
    self.pipes = []
    self.bird_height = 0
    self.onupdate = onupdate
    self.readDimensions()
    threading.Thread(target=self.capture).start()

  def readDimensions(self):
    screen = self.captureElement([0, 0, 1920, 1080])
    screenHeight = len(screen); screenWidth = len(screen[0])
    startX = 0; startY = 0

    isGameSky = lambda color : np.array_equal(color, [206, 197, 112, 255])
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
    var = True
    while var:
      # start_time = time.time()
      asyncio.run(self.captureFrame())
      # print("FPS: ", 1.0 / (time.time() - start_time))

  async def captureFrame(self):
    game = self.captureElement(GAME_BBOX)
    await asyncio.gather(
      self.capturePipeHeight(game),
      self.captureExitingPipe(game),
      self.captureBirdPosition(game)
    )
    u = {"bird": self.bird_height + BIRD_MARGIN, "pipe": self.pipes[0] + PIPE_VERTICAL_DISTANCE if self.pipes.__len__() > 0 else 320}
    self.onupdate(u)

  isPipe = lambda _, pipe, col, row : pipe[col][row][0] != 206

  async def capturePipeHeight(self, game):
    if self.isPipe(game, PIPE_RELATIVE[1], PIPE_RELATIVE[0]) and not self.pipe_height_last:
      self.pipe_height_last = True
      pipe_height = 0
      while self.isPipe(game, PIPE_RELATIVE[1] + pipe_height, PIPE_RELATIVE[0]):
        pipe_height += 1
      self.next_up = len(self.pipes) > 0 and self.pipes[0] > pipe_height
      self.pipes.append(pipe_height)
      print("PIPE:ADD", self.pipes, self.next_up)
    elif not self.isPipe(game, PIPE_RELATIVE[1], PIPE_RELATIVE[0]):
      self.pipe_height_last = False

  async def captureExitingPipe(self, game):
    xOffset = EXISTING_PIPE_OFFSET_UP if self.next_up else EXISTING_PIPE_OFFSET_DOWN
    isExitingPipe = self.isPipe(game, EXITING_PIPE_RELATIVE[1], EXITING_PIPE_RELATIVE[0] - xOffset)
    if not isExitingPipe and self.pipe_exit_last:
      self.pipe_exit_last = False
      self.pipes.pop(0)
      print("PIPE:REMOVE", self.pipes)
    elif isExitingPipe:
      self.pipe_exit_last = True

  async def captureBirdPosition(self, game):
    isBird = lambda i: np.array_equal(game[i + BIRD_RELATIVE[1]][BIRD_RELATIVE[0]], [39, 191, 212, 255])
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
    hwnd = None
    wDC = win32gui.GetWindowDC(hwnd)
    dcObj=win32ui.CreateDCFromHandle(wDC)
    cDC=dcObj.CreateCompatibleDC()
    dataBitMap = win32ui.CreateBitmap()
    dataBitMap.CreateCompatibleBitmap(dcObj, bbox[2], bbox[3])
    cDC.SelectObject(dataBitMap)
    cDC.BitBlt((0,0),(bbox[2], bbox[3]) , dcObj, (bbox[0],bbox[1]), win32con.SRCCOPY)
    
    signedIntsArray = dataBitMap.GetBitmapBits(True)
    img = np.frombuffer(signedIntsArray, dtype='uint8').copy()
    img.shape = (bbox[3], bbox[2], 4)
    # Free Resources
    dcObj.DeleteDC()
    cDC.DeleteDC()
    win32gui.ReleaseDC(hwnd, wDC)
    win32gui.DeleteObject(dataBitMap.GetHandle())
    return img

  def cleanup(self):
    print("cleanup")
    return True
