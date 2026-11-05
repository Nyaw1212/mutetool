# Filmora Chrome Mute Tool

Windows-only prototype. When **Filmora is focused**, pressing **Spacebar** alternates between muting Chrome's Windows audio sessions and restoring their previous mute states. Space still goes to Filmora.

**Important:** This is a *key-press toggle*, not playback-state detection. Start while Filmora is paused. Clicking the Play/Pause button, pressing Space elsewhere, or having Chrome open new audio sessions can cause imperfect behavior. It mutes **all Chrome audio**, not just YouTube. The tool doesn't capture keystrokes or send them anywhere.

## First run in PowerShell

```powershell
cd "$HOME\Downloads"
git clone https://github.com/Nyaw1212/mutetool.git
cd .\mutetool
py -m pip install -r requirements.txt
py .\filmora_audio.py
```

If you already cloned it:

```powershell
cd "$HOME\Downloads\mutetool"
git pull origin main
py -m pip install -r requirements.txt
py .\filmora_audio.py
```

Test: start Filmora **paused** and open a YouTube video in Chrome, then switch to Filmora and press Space. Chrome should mute. Press Space again to restore Chrome audio. Stop with Ctrl+C in PowerShell. **Ctrl+Alt+F10** is an emergency restore while the script is running. If audio stays muted after a crash, unmute Chrome using Windows Volume Mixer.

Run this in a regular user PowerShell window; don't run as administrator unless Filmora itself is elevated.
