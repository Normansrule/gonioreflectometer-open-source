OpenGonio desktop app
=====================

Start it: Windows: OpenGonio.exe · macOS: OpenGonio.app · Linux: ./OpenGonio (it opens your browser).
Inside the app, connect to the simulated machine (works everywhere) or to the machine over USB.
Runs are saved in your home folder: OpenGonio/runs.

First start on an unsigned app:
- Windows: "Windows protected your PC" -> More info -> Run anyway.
- macOS: right-click OpenGonio.app -> Open -> Open (only the first time).
- Linux: chmod +x OpenGonio, then ./OpenGonio

Phones and tablets on the same Wi-Fi: start with  OpenGonio --lan  and scan the QR code shown in the app
(top bar -> Phone). Only devices that scanned the code can control the machine. STOP always works.

The machine over USB needs the SKR Pico and the camera connected to this computer. Nothing here has been
tested on a built OpenGonio yet. Source, licence (GPL-3.0-or-later) and help: the GitHub repository.
