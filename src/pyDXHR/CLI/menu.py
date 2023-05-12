import inquirer
from pathlib import Path
import os
import sys
import trimesh
from trimesh import viewer
from trimesh.viewer import windowed
import tkinter as tk
from tkinter import filedialog

import CLI.bigfile
from CLI import *

print("pyDXHR CLI".center(80, "-"))
print("version 0.1.0".center(80, "-"))

root = tk.Tk()
root.withdraw()

# region initialize program
env_bigfile = os.getenv("PYDXHR_BIGFILE")
if env_bigfile:
    print(f"Using BIGFILE {env_bigfile}")
else:
    initialize = [
        inquirer.Confirm("dxhr_install_confirm",
                         message="Open a window to select DXHR install path",
                         default=True)
            ]
    if inquirer.prompt(initialize).get("dxhr_install_confirm"):
        file_path = filedialog.askdirectory()
    else:
        print("No install path specified. Closing program.")
        sys.exit(0)

    # check if BIGFILE is in directory
    CLI.bigfile.check_bigfile(file_path)

    sys.exit(0)

main_menu_questions = [
  inquirer.List('main_menu',
                message="Main menu",
                choices=[
                    "View IMF",
                    'View object',
                    'Extract game data',
                    'Display strings',
                    'Settings',
                    'Credits',
                ],
                carousel=True,
                autocomplete=True
                ),
]

settings_menu = [
    inquirer.List('settings_menu',
                  message="Settings",
                  choices=[
                      "View DXHR install path",
                      'Open dev menu',
                  ],
                  carousel=True,
                  autocomplete=True
                  ),
]

dev_menu = [
    inquirer.List('dev_menu',
                  message="Dev menu",
                  choices=[
                      'Unpack BIGFILE',
                      'Decompress DRM',
                      'Unpack DRM to sections',
                      'Version comparison',
                  ],
                  carousel=True,
                  autocomplete=True
                  ),
]
# questions = [
#   inquirer.Text('dxhr_install', message="DXHR install path"),
# ]
#
# answers = inquirer.prompt(questions)
# print(answers)


# print(file_path)
#
# # sample = r"..\..\output\collision\0.gltf"
# sample = r'F:\pyDXHR\masterunit\det_sarifhq\det_sarifhq\det_sarifhq.gltf'
# mesh = trimesh.load_mesh(sample)
