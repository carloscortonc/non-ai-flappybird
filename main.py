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
last_jump = 0
def onupdate(u):
  global previous, last_jump
  diff = u["bird"] - previous
  # print(u)
  offset = 0
  if diff >= 0:
    offset = 13 + 1.9e-17 * (diff ** 12)
  else:
    offset = 12e-2 * (diff ** 3)
  bird_position = u["bird"] + round(offset)
  if diff != 0 and last_jump > 2 and bird_position > u["pipe"]:
    press(" ")
    print("[JUMP]", last_jump, diff, bird_position, u["pipe"], u, offset)
    last_jump = 0
    time.sleep(0.07)
  last_jump += 1
  previous = u["bird"]

# initial jump to start the game
press(" ")

key_listener.init(lambda: os._exit(0))
sceneProcessor = SceneProcessor(onupdate)
