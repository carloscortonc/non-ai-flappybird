from pynput.keyboard import Key, Listener

def on_press(key, onclose):
  if key == Key.esc:
    print("[keyboard-listenner] [key=ESC] ending")
    onclose()

def init(onclose):
  listener = Listener(on_press=lambda e : on_press(e, onclose))
  listener.start()
  