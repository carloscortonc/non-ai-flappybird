from PIL import ImageGrab
import numpy as np
import mss
import time

import win32gui
import win32ui
import win32con
import dxcam

def timing(f):
  def wrap(*args, **kwargs):
    time1 = time.time()
    ret = f(*args, **kwargs)
    time2 = time.time()
    print('{:s} function took {:.3f} ms'.format(
      f.__name__, (time2-time1)*1000.0))
    return ret
  return wrap

TEST_BBOX = [927, 315, 1, 550]

@timing
def imagegrab():
  np.array(ImageGrab.grab(bbox=[TEST_BBOX[0], TEST_BBOX[1], TEST_BBOX[0] + TEST_BBOX[2], TEST_BBOX[1]+TEST_BBOX[3]]))

# https://stackoverflow.com/questions/3586046/fastest-way-to-take-a-screenshot-with-python-on-windows
@timing
def captureElement():
  hwnd = None
  wDC = win32gui.GetWindowDC(hwnd)
  dcObj=win32ui.CreateDCFromHandle(wDC)
  cDC=dcObj.CreateCompatibleDC()
  dataBitMap = win32ui.CreateBitmap()
  dataBitMap.CreateCompatibleBitmap(dcObj, TEST_BBOX[2], TEST_BBOX[3])
  cDC.SelectObject(dataBitMap)
  cDC.BitBlt((0,0),(TEST_BBOX[2], TEST_BBOX[3]) , dcObj, (TEST_BBOX[0], TEST_BBOX[1]), win32con.SRCCOPY)
  
  signedIntsArray = dataBitMap.GetBitmapBits(True)
  img = np.frombuffer(signedIntsArray, dtype='uint8').copy()
  img.shape = (TEST_BBOX[2], TEST_BBOX[3], 4)
  # Free Resources
  dcObj.DeleteDC()
  cDC.DeleteDC()
  win32gui.ReleaseDC(hwnd, wDC)
  win32gui.DeleteObject(dataBitMap.GetHandle())

# good for cross-platform
@timing
def msstest():
  with mss.mss() as sct:
    np.array(sct.grab({'top': TEST_BBOX[1], 'left': TEST_BBOX[0], 'width': TEST_BBOX[2], 'height': TEST_BBOX[3]}))

cam = dxcam.create()
@timing
def dxcamtest():
  cam.grab(region=[TEST_BBOX[0], TEST_BBOX[1], TEST_BBOX[0] + TEST_BBOX[2], TEST_BBOX[1]+TEST_BBOX[3]])

imagegrab()
captureElement()
msstest()
dxcamtest()
