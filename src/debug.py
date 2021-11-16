
from lib.viz.drawing import Drawer, Logger, LoggingLevel
from PIL import Image
import numpy as np


import os
import sys

rootpath = os.path.join(os.path.dirname(__file__), '..')
sys.path.append(rootpath)

# --------------------------------------

img = np.zeros((480,640,3), dtype=np.uint8)

logger = Logger()
drawer = Drawer(logger = logger)

# --- STYLES SETUP

my_style = {"line color": "blue",
            "box fill color": "white",
            "line thickness": 3,
            "text fill color": "blue",
            "points color": "red",
            "points outline color": "yellow",
            "points outline thickness": 2, 
            "points size": 5, 
            "text color": "yellow"}

drawer.add_style("prova", my_style)

my_style = {"line color": "red",
            "box fill color": None,
            "line thickness": 5,
            "text fill color": "red",
            "text color": "white"}

drawer.add_style("second", my_style)

# --- DRAWING CALLS

drawer.set_style("prova")
img = drawer.box(img, (20,20), (70,70))

drawer.set_style("second")
# drawer.return_numpy = True

img = drawer.box(img, (55,155), (210,310), text_show="dog", font_size=20)
img = drawer.box(img, (335,5), (510,210), text_show="elephant", position="bottom right", font_size=20, inner=True)
img = drawer.text_anchor(img, text_show = "tentative", alignment = "bottom center")

segments = [[(300,300),(550,420)], [(450, 420), (550, 100)]]
img = drawer.segments(img, segments)

drawer.set_style("prova")
img = drawer.text_anchor(img, text_show = "2", alignment = "top right")

points = [[120,320], [520,300]]
points_labels = ["1", "2", ]
img = drawer.keypoints(img, points, labels = points_labels)


joints = [[350,150],
          [400,100],
          [450,150],
          [400,250],
          [365,300],
          [435,300]]

bones = [[0,1],
         [1,2],
         [1,3],
         [3,4],
         [3,5]]

labels = ["lh", "head", "rh", "hip", "lf", "rf"]
 
img = drawer.skeleton(img, joints = joints, bones = bones, labels = labels)

points = [[180,50],
          [250,50],
          [300,120],
          [220,70],
          [200,120]]

drawer.update_current_style({"line color": "green"})

img = drawer.arrow(img, points = [[150, 250], [240, 240]])
img = drawer.arrow(img, points = [[50, 300], [290, 290]])

drawer.update_current_style({"line thickness": 6})

img = drawer.polygon(img, points = points)

drawer.update_current_style({"line thicknss": 6})

# --- VISUALIZATION

drawer.show(img)
