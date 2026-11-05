"""Mute Chrome while Filmora is playing via the Spacebar shortcut.

This tool tracks Spacebar presses, NOT Filmora's actual transport status.
For Windows only.
"""
import atexit
import ctypes
import threading
from ctypes import wintypes

import psutil
from pynput import keyboard
from pycaw.pycaw import AudioUtilities

user32 = ctypes.WinDLL("user32", use_last_error=True)
user32.GetForegroundWindow.restype = wintypes.HWND
user32.GetWindowThreadProcessId.argtypes = (wintypes.HWND, ctypes.POINTER(wintypes.DWORD))
user32.GetWindowThreadProcessId.restype = wintypes.DWORD

lock = threading.Lock()
playing = False
saved_mute = {}
pressed = set()


def filmora_focused():
    hwnd = user32.GetForegroundWindow()
    if not hwnd:
        return False
    pid = wintypes.DWORD()
    user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
    try:
        proc = psutil.Process(pid.value)
        # Some Filmora windows may be hosted by an auxiliary Filmora process.
        return "filmora" in proc.name().lower()
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        return False


def chrome_sessions():
    for session in AudioUtilities.GetAllSessions():
        try:
            if session.Process and session.Process.name().lower() == "chrome.exe":
                yield session
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass


def mute_chrome():
    count = 0
    for session in chrome_sessions():
        try:
            audio = session.SimpleAudioVolume
            pid = session.Process.pid
            if pid not in saved_mute:
                saved_mute[pid] = bool(audio.GetMute())
            audio.SetMute(1, None)
            count += 1
        except Exception as exc:
            print(f"Couldn't mute Chrome session: {exc}")
    return count


def restore_chrome():
    # Restore only sessions whose original state we captured.
    for session in chrome_sessions():
        try:
            pid = session.Process.pid
            if pid in saved_mute:
                session.SimpleAudioVolume.SetMute(int(saved_mute[pid]), None)
        except Exception as exc:
            print(f"Couldn't restore Chrome session: {exc}")
    saved_mute.clear()


def toggle():
    global playing
    with lock:
        playing = not playing
        if playing:
            count = mute_chrome()
            print(f"Filmora: PLAY -> Chrome muted ({count} audio session(s)).")
        else:
            restore_chrome()
            print("Filmora: PAUSE -> Chrome audio restored.")


def emergency_restore():
    global playing
    with lock:
        playing = False
        restore_chrome()
        print("Emergency restore complete. State reset to PAUSE.")


def on_press(key):
    # Ignore key auto-repeat while Space is held down.
    if key in pressed:
        return
    pressed.add(key)
    if key == keyboard.Key.space and filmora_focused():
        toggle()
    elif key == keyboard.Key.f10 and keyboard.Key.ctrl_l in pressed and keyboard.Key.alt_l in pressed:
        emergency_restore()


def on_release(key):
    pressed.discard(key)


atexit.register(emergency_restore)

if __name__ == "__main__":
    print("Filmora Chrome Mute Tool")
    print("Space in Filmora: toggle Chrome mute (Filmora receives Space normally).")
    print("Ctrl+Alt+F10: emergency restore; Ctrl+C here: exit.")
    print("Start with Filmora paused. Click Play manually? State may be out of sync.")
    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()
