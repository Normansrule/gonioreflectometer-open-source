// Written by tools/site_data.py (`make build`): do not edit by hand.
window.SITE = {
 "stages": [
  {
   "id": "00",
   "folder": "00-plan",
   "title": "Plan",
   "goal": "Know what you are building, why, and what to buy.",
   "milestones": [
    "Read and decide",
    "Software runs on the laptop",
    "CAD and printer ready"
   ],
   "steps": 12,
   "hours": 6.7,
   "cost": 63.96
  },
  {
   "id": "01",
   "folder": "01-power",
   "title": "Power",
   "goal": "Wall adapter, e-stop box, wire and lever connectors on the bench, each checked; the power plate printed.",
   "milestones": [
    "Order and check power parts",
    "Wire the power",
    "First power-on"
   ],
   "steps": 8,
   "hours": 2.5,
   "cost": 54.26
  },
  {
   "id": "02",
   "folder": "02-controller",
   "title": "Controller and buttons",
   "goal": "SKR Pico, keypads, cables, the motor 5-pack and the endstops on the bench; your ESP32-S3 as the hub.",
   "milestones": [
    "Order controller parts",
    "One motor turns from the laptop",
    "Keypads work with the laptop",
    "Controller box closed"
   ],
   "steps": 12,
   "hours": 4.5,
   "cost": 70.84
  },
  {
   "id": "03",
   "folder": "03-frame",
   "title": "Frame",
   "goal": "Nine printed tiles bolted into one 600 mm deck; every mount already has its pilot hole.",
   "milestones": [
    "Print and join the deck",
    "Assemble the frame"
   ],
   "steps": 5,
   "hours": 2.8,
   "cost": 22.45
  },
  {
   "id": "04",
   "folder": "04-light-arm",
   "title": "Light arm (M4)",
   "goal": "Light arm turns smoothly on the ring.",
   "milestones": [
    "Ring drive built",
    "Light arm homes and repeats"
   ],
   "steps": 9,
   "hours": 5.4,
   "cost": 77.43
  },
  {
   "id": "05",
   "folder": "05-table",
   "title": "Table (M3)",
   "goal": "Sample table turns on its fixed bolt axle without wobble.",
   "milestones": [
    "Table axis built",
    "Table homes and repeats"
   ],
   "steps": 7,
   "hours": 3.2,
   "cost": 23.56
  },
  {
   "id": "06",
   "folder": "06-camera-light",
   "title": "Camera and light",
   "goal": "Sharp, fixed-exposure image centred on the sample.",
   "milestones": [
    "Camera sees the zero point",
    "Lamp on and safe",
    "Mirror test",
    "First reflectance curves"
   ],
   "steps": 11,
   "hours": 5.8,
   "cost": 111.91
  },
  {
   "id": "07",
   "folder": "07-calibrate",
   "title": "Calibrate → game material",
   "goal": "Only the lamp lights the sample.",
   "milestones": [
    "Dark box",
    "Camera response and angle calibration",
    "Brightness calibration",
    "First game material"
   ],
   "steps": 11,
   "hours": 4.8,
   "cost": 39.78
  },
  {
   "id": "08",
   "folder": "08-tilt",
   "title": "Tilt (M2)",
   "goal": "Sample tilts without leaving the zero point.",
   "milestones": [
    "Tilt yoke built and homed",
    "Full isotropic scan"
   ],
   "steps": 8,
   "hours": 3.8,
   "cost": 16.68
  },
  {
   "id": "09",
   "folder": "09-spin",
   "title": "Spin (M1)",
   "goal": "Sample spins on its own axis (direct drive).",
   "milestones": [
    "Spin wired and homed",
    "Anisotropic material measured"
   ],
   "steps": 5,
   "hours": 2.3,
   "cost": 11.99
  },
  {
   "id": "10",
   "folder": "10-color",
   "title": "Colour add-ons (optional)",
   "goal": "Colour spectrum of the spot at the zero point; camera stays for images.",
   "milestones": [
    "Spectral sensor (optional kit)",
    "LED bank and polarizers (optional kit)"
   ],
   "steps": 8,
   "hours": 5.5,
   "cost": 0.0
  },
  {
   "id": "11",
   "folder": "11-scan-capture",
   "title": "3D scan: capture",
   "goal": "Scan camera fixed at 650 mm, object held securely; nothing on the measuring side moves.",
   "milestones": [
    "Scan hardware",
    "Camera position calibrated",
    "First full scan"
   ],
   "steps": 7,
   "hours": 2.5,
   "cost": 2.33
  },
  {
   "id": "12",
   "folder": "12-scan-mesh",
   "title": "3D scan: mesh",
   "goal": "Shape from silhouettes in minutes.",
   "milestones": [
    "Quick 3D preview",
    "Full mesh"
   ],
   "steps": 6,
   "hours": 2.2,
   "cost": 0.0
  },
  {
   "id": "13",
   "folder": "13-object-material",
   "title": "Material on the 3D model",
   "goal": "Colour per texel from the scan photos.",
   "milestones": [
    "Textures on the mesh",
    "Object in a game engine"
   ],
   "steps": 4,
   "hours": 6.0,
   "cost": 0.0
  },
  {
   "id": "14",
   "folder": "14-laptop-app",
   "title": "Laptop app",
   "goal": "Connect, jog, home, live camera and run a plan in one browser page.",
   "milestones": [
    "Control page",
    "Presets and resume"
   ],
   "steps": 6,
   "hours": 16.0,
   "cost": 0.0
  },
  {
   "id": "15",
   "folder": "15-standalone",
   "title": "Standalone (no laptop)",
   "goal": "OLED shows menu and progress (both modes).",
   "milestones": [
    "Panel screen",
    "Pi Zero station set up",
    "Job with no laptop",
    "Laptop collects and verifies"
   ],
   "steps": 8,
   "hours": 2.8,
   "cost": 0.0
  },
  {
   "id": "16",
   "folder": "16-release",
   "title": "Release",
   "goal": "A new builder can finish stage 06 from the docs alone.",
   "milestones": [
    "Docs complete",
    "Public release"
   ],
   "steps": 6,
   "hours": 4.2,
   "cost": 0.0
  },
  {
   "id": "17",
   "folder": "17-upgrades",
   "title": "Upgrades (optional)",
   "goal": "Same fit with fewer photos.",
   "milestones": [
    "Adaptive sampling",
    "Space carving",
    "Compare with MERL / RGL data",
    "Battery power"
   ],
   "steps": 7,
   "hours": 17.2,
   "cost": 0.0
  }
 ],
 "plan_usd": 495.19,
 "cap_usd": 630.0,
 "steps": 140,
 "hours": 98.2,
 "parts": 83,
 "evidence": [
  {
   "claim": "In-plane and out-of-plane BRDF, white light, flat samples ≤ 50 mm",
   "evidence": "simulated end to end (`make sim`)"
  },
  {
   "claim": "Absolute BRDF against a polytetrafluoroethylene (PTFE) reference, camera response, lamp drift checks",
   "evidence": "simulated; uncertainty not characterized"
  },
  {
   "claim": "Repeatability ≤ 0.1° per axis",
   "evidence": "modeled (step size); not measured"
  },
  {
   "claim": "No part collisions over every axis' travel",
   "evidence": "modeled (CAD sweep + mixed poses)"
  },
  {
   "claim": "AS7341 spectral readings (8 visible bands + clear + NIR)",
   "evidence": "not characterized (firmware untested)"
  },
  {
   "claim": "Colour LED bank (stage 10)",
   "evidence": "blocked: driver circuit unsafe as designed, do not power"
  },
  {
   "claim": "3D scan: visual hull",
   "evidence": "simulated"
  },
  {
   "claim": "3D scan: photometric stereo",
   "evidence": "simulated; needs the blocked LED bank"
  },
  {
   "claim": "24 V wall adapter, 3 A: 1.3 A peak draw",
   "evidence": "modeled from listing values"
  },
  {
   "claim": "Electrical safety",
   "evidence": "not certified (only 24 V inside the machine: wall adapter with short-circuit protection per its listing, e-stop, limit switch)"
  }
 ]
};
