import inquirer
import trimesh
from trimesh import viewer
from trimesh.viewer import windowed
import tkinter as tk
from tkinter import filedialog

root = tk.Tk()
root.withdraw()

file_path = filedialog.askopenfilename()
print(file_path)

# sample = r"..\..\output\collision\0.gltf"
sample = r'F:\pyDXHR\masterunit\det_city\det_sarif_industries\det_sarif_industries.gltf'
mesh = trimesh.load_mesh(sample)


questions = [
  inquirer.List('size',
                message="What size do you need?",
                choices=['Jumbo', 'Large', 'Standard', 'Medium', 'Small', 'Micro'],
            ),
]

answers = inquirer.prompt(questions)

if answers["size"] == "Standard":
    trimesh.viewer.SceneViewer(mesh, resolution=(800, 800))
