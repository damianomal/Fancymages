
from lib.viz.drawing import Drawer
from lib.utils.logger import Logger

import numpy as np
import os
import sys

from PIL import Image

rootpath = os.path.join(os.path.dirname(__file__), '..')
sys.path.append(rootpath)

# --------------------------------------

img = np.zeros((480,640,3), dtype=np.uint8)

logger = Logger()
drawer = Drawer(logger = logger)

# --- STYLES SETUP

my_style = {"line color": "blue",
            "box fill color": "gray",
            "line thickness": 3,
            "text fill color": "transparent",
            "points color": "red",
            "points outline color": "yellow",
            "points outline thickness": 2, 
            "text font size": 20,
            "points size": 5, 
            "text color": "yellow",
            "mask color": (0,220,0) }

drawer.add_style("first", my_style)

my_style = {"line color": "red",
            "box fill color": None,
            "line thickness": 5,
            "text fill color": "red",
            "text font size": 30,
            "text color": "white"}

drawer.add_style("second", my_style)

# ---- Image Loading ----

img = Image.open("assets/sample.jpg")
msk = Image.open("assets/mask.png")

# ---- Base Image  ----

drawer.show(img)

# --- DRAWING CALLS

drawer.set_style("first")

# ---- Segmentation Mask + Snapshot ----

img = drawer.mask(img, msk)

drawer.snapshot()

# ---- Bounding Boxes ----

drawer.set_style("second")

img = drawer.box(img, (449,93), (449+169,93+398), label="person")
img = drawer.box(img, (607,53), (607+210,53+427), label="person", position="top right")
img = drawer.box(img, (734,364), (734+89,364+127), label="dog", position="bottom right", inner = True, color="blue")

drawer.snapshot()

# ---- Top Right Overlay ----

drawer.update_current_style({"text fill color": "green"})

img = drawer.text_anchor(img, text_show = "24", alignment = "top right", font_size = 40)

# ---- Bottom Overlay Caption ----

drawer.update_current_style({"text fill color": "black"})

img = drawer.text_anchor(img, text_show = "Sample Very Long Caption Text", alignment = "bottom center", font_size = 24)

# ---- Skeleton (pose) ----

drawer.set_style("first")

joints = [[526,136], #0 
          [517,128], #1
          [510,134], #2
          [535,128], #3
          [540,135], #4
          [523,165], #5
          [488,175], #6
          [483,232], #7
          [464,293], #8
          [559,174], #9
          [578,229], #10
          [606,267], #11
          [527,273], #12
          [508,292], #13
          [506,371], #14
          [516,450], #15
          [550,291], #16
          [541,372], #17
          [541,467], #18
          ]

bones = [[0,1], #0 
         [1,2], #1
         [0,3], #2
         [3,4], #3
         [0,5], #4
         [5,6], #5
         [6,7], #6
         [7,8], #7
         [5,9], #8
         [9,10], #9
         [10,11], #10
         [5,12], #11
         [12,13], #12
         [13,14], #13
         [14,15], #14
         [12,16], #15
         [16,17], #16
         [17,18], #17
         ]

img = drawer.skeleton(img, joints = joints, bones = bones, font_size = 20)

# ---- Segments + Text ---

drawer.set_style("second")

segments = [[(18,40),(35,20)], [(18,62), (65,20)], [(18,90), (115,20)]]

for i, segment in enumerate(segments):
    img = drawer.segments(img, [segment], thickness=(i+1)*2)

drawer.update_current_style({"text fill color": "transparent"})

img = drawer.text(img, coords=(110,45), text_show="segments")

# ---- Keypoints + Text ---

drawer.set_style("first")

points = [[30,175], [67,140], [81,160], [126,150]]

img = drawer.keypoints(img, points, labels = "numbers", font_size = 20)

drawer.update_current_style({"text fill color": "transparent"})
drawer.update_current_style({"text color": "white"})

img = drawer.text(img, coords = (170,148), text_show = "keypoints", font_size = 30)

# ---- Boxes + Text ---

drawing_base_x = 30
drawing_base_y = 220
drawing_offset = 20
drawing_size = 40

img = drawer.box(img, 
                 (drawing_base_x,drawing_base_y), 
                 (drawing_base_x+drawing_size,drawing_base_y+drawing_size))

drawer.update_current_style({"box fill color": "white"})
img = drawer.box(img, 
                 (drawing_base_x+drawing_offset,drawing_base_y+drawing_offset), 
                 (drawing_base_x+drawing_offset+drawing_size,drawing_base_y+drawing_offset+drawing_size), 
                 color = "red")

drawer.update_current_style({"box fill color": None})
img = drawer.box(img, 
                 (drawing_base_x+drawing_offset*2,drawing_base_y+drawing_offset*2), 
                 (drawing_base_x+drawing_offset*2+drawing_size,drawing_base_y+drawing_offset*2+drawing_size), 
                 color = "green")

img = drawer.text(img, coords = (140,242), text_show = "filled/empty boxes", font_size = 30)

# ---- Polygons + Text ----

drawing_base_x = 0
drawing_base_y = 315

drawer.update_current_style({"box fill color": "yellow", "line thickness": 7})

points = [[60,drawing_base_y+20],
          [90,drawing_base_y+45],
          [80,drawing_base_y+90],
          [50,drawing_base_y+80],
          [20,drawing_base_y+40]]

img = drawer.polygon(img, points = points)

drawer.update_current_style({"box fill color": None, "line thickness": 3, "points size": 3})

drawing_base_x = 85

points = [[drawing_base_x+60,drawing_base_y+20],
          [drawing_base_x+90,drawing_base_y+45],
          [drawing_base_x+80,drawing_base_y+90],
          [drawing_base_x+50,drawing_base_y+80],
          [drawing_base_x+20,drawing_base_y+40]]

img = drawer.polygon(img, points = points, draw_points = True)

drawer.update_current_style({"line color": "purple"})

drawing_base_x = 170

points = [[drawing_base_x+60,drawing_base_y+20],
          [drawing_base_x+90,drawing_base_y+45],
          [drawing_base_x+65,drawing_base_y+68],
          [drawing_base_x+80,drawing_base_y+90],
          [drawing_base_x+50,drawing_base_y+80],
          [drawing_base_x+40,drawing_base_y+55],
          [drawing_base_x+20,drawing_base_y+40]]

img = drawer.polygon(img, points = points)

img = drawer.text(img, coords = (283,353), text_show = "polygons", font_size = 30)

# ---- Arrows + Text ----

drawing_base_y = 430

drawer.update_current_style({"line color": "green"})

img = drawer.arrow(img, points = [[20, drawing_base_y+30], [80, drawing_base_y+20]])
img = drawer.arrow(img, points = [[110, drawing_base_y+38], [35, drawing_base_y+75]])
img = drawer.arrow(img, points = [[94, drawing_base_y+80], [172, drawing_base_y+34]], filled=True)

img = drawer.text(img, coords = (200,465), text_show = "arrows", font_size = 30)

# --- VISUALIZATION

drawer.show(img)

# --- TODO: add functionality to draw ciclying classes

drawer.overlay(None, None, None, None, None)