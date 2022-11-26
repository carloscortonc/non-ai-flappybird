import threading
import numpy as np
import asyncio

import win32gui
import win32ui
import win32con

import cv2

PIPE_BBOX = [1185, 307, 1, 420]
BIRD_BBOX = [927, 315, 1, 550]
EXITING_PIPE_BBOX = [BIRD_BBOX[0] - 50 , PIPE_BBOX[1], 1, 1]

BIRD_MARGIN = 70
PIPE_VERTICAL_DISTANCE = 160

class SceneProcessor:
  def __init__(self, onupdate):
    self.pipe_height_last = False
    self.pipe_exit_last = False
    self.pipes = []
    self.bird_height = 0
    self.onupdate = onupdate
    threading.Thread(target=self.capture).start()

  def capture(self):
    var = True
    while var:
      # start_time = time.time()
      asyncio.run(self.captureFrame())
      # print("FPS: ", 1.0 / (time.time() - start_time))

  async def captureFrame(self):
    await asyncio.gather(
      self.capturePipeHeight(),
      self.captureExitingPipe(),
      self.captureBirdPosition()
    )
    u = {"bird": self.bird_height + BIRD_MARGIN, "pipe": self.pipes[0] + PIPE_VERTICAL_DISTANCE if self.pipes.__len__() > 0 else 320}
    self.onupdate(u)

  isPipe = lambda _, pipe, col : pipe[0][col][0] != 206

  async def capturePipeHeight(self):
    pipe = self.captureElement(PIPE_BBOX)
    if self.isPipe(pipe, 0) and not self.pipe_height_last:
      self.pipe_height_last = True
      pipe_height = 0
      while self.isPipe(pipe, pipe_height):
        if pipe_height > 442:
          cv2.imwrite("pipe_error.png", pipe)
        pipe_height += 1
      self.pipes.append(pipe_height)
    elif not self.isPipe(pipe, 0):
      self.pipe_height_last = False

  async def captureExitingPipe(self):
    exitingPipe = self.captureElement(EXITING_PIPE_BBOX)
    if not self.isPipe(exitingPipe, 0) and self.pipe_exit_last:
      self.pipe_exit_last = False
      self.pipes.pop(0)
    elif self.isPipe(exitingPipe, 0):
      self.pipe_exit_last = True

  async def captureBirdPosition(self):
    bird = self.captureElement(BIRD_BBOX)
    isBird = lambda i: np.array_equal(bird[0][i], [39, 191, 212, 255])
    self.bird_height = -1
    bird_last = False
    while True:
      if self.bird_height > 548:
        cv2.imwrite("bird_error.png", bird)
      self.bird_height += 1
      checkBird = isBird(self.bird_height)
      if not checkBird and bird_last:
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
    img.shape = (bbox[2], bbox[3], 4)
    # Free Resources
    dcObj.DeleteDC()
    cDC.DeleteDC()
    win32gui.ReleaseDC(hwnd, wDC)
    win32gui.DeleteObject(dataBitMap.GetHandle())
    return img

  def cleanup(self):
    print("cleanup")
    return True
