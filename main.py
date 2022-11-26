import key_listener
# from scene_processor.v1 import SceneProcessor
from scene_processor.v3.v_sync import SceneProcessor
import os
from pyautogui import press
import win32com.client as comctl

# Gain focus on flappy-bird chrome tab
wsh = comctl.Dispatch("WScript.Shell")
wsh.AppActivate("Play Flappy Bird")

def onupdate(u):
  # print(u)
  if u["bird"] > u["pipe"]:
    press(" ")

# wait for web-window to acquire focus
press(" ")

key_listener.init(lambda: os._exit(0))
sceneProcessor = SceneProcessor(onupdate)
