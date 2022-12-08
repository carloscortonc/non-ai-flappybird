import key_listener
# from scene_processor.v1 import SceneProcessor
from scene_processor.v3.v_sync import SceneProcessor
import os
from pyautogui import press
import win32com.client as comctl
import time

# Gain focus on flappy-bird chrome tab
wsh = comctl.Dispatch("WScript.Shell")
wsh.AppActivate("Play Flappy Bird")

previous = 0
def onupdate(u):
  global previous
  diff = u["bird"] - previous
  # print(diff)
  offset = 0
  if diff >= 0:
    offset = 1.77e-17 * (diff ** 12)
  else:
    offset = 20e-2 * (diff ** 3)
  if diff != 0 and u["bird"] + offset > u["pipe"]:
    press(" ")
    time.sleep(0.07)
  previous = u["bird"]

# initial jump to start the game
press(" ")

key_listener.init(lambda: os._exit(0))
sceneProcessor = SceneProcessor(onupdate)
