
from lib.viz.drawing import Drawer
from PIL import Image
import numpy as np

# --------------------------------------


# def deco(func):

#     def Inner(obj, *args, **kwargs):

#         # def wrapper(**kwargs):
 
#         print(kwargs)
#         print("DEBUG:", obj._a)

#         func(obj, **kwargs)

#         print("DEBUG:", obj._a)
             
#         # return wrapper


#     return Inner

# class thisclass:

#     def __init__(self):

#         self._a = None
#         self._b = None

#     @deco
#     def m(self, **kwargs):

#         for entry in kwargs.items():
#             attrname = f"_{entry[0]}"
#             if hasattr(self, attrname):
#                 setattr(self, attrname, entry[1])
#             else:
#                 print(f"field {entry[0]} not available")

# --------------------------------------



# item = thisclass()

# print(item._a, item._b)

# # item.m(a = 4, b = 1)
# item.m(**{"a": 4, "b": 1})

# print(item._a, item._b)


drawer = Drawer()

my_style = {"line_color": "blue",
            "box_fill_color": "white",
            "line_thickness": 2}

drawer.add_style("prova", my_style)

my_style = {"line_color": "red",
            "box_fill_color": "yellow",
            "line_thickness": 5}

drawer.add_style("second", my_style)

img = np.zeros((200,200,3), dtype=np.uint8)

drawer.set_style("prova")
img = drawer.box(img, (20,20), (50,50))

# print("type(img):", type(img))

drawer.set_style("second")
drawer.return_numpy = True

img = drawer.box(img, (35,35), (70,70), label = "a")

# img = drawer.text(img, None, None, None)

# print("type(img):", type(img))

drawer.show(img)
