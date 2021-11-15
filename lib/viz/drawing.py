
from PIL import Image, ImageDraw, ImageFont

from lib.utils.color_names import colors
from contextlib import contextmanager
from enum import Enum
import numpy as np
import matplotlib.pyplot as plt

# ----------------------------------------

class Positions(Enum):

    TOPLEFT = 1
    TOP = 2
    TOPRIGHT = 3
    RIGHT = 4
    BOTTOMRIGHT = 5
    BOTTOM = 6
    BOTTOMLEFT = 7
    LEFT = 8
    CENTER = 9

# class AnchorPositions(Enum):

#     TOPLEFT = 1
#     TOPRIGHT = 2
#     BOTTOMRIGHT = 3
#     BOTTOMLEFT = 4

class LoggingLevel(Enum):

    DEBUG = 1
    INFO = 2
    WARNING = 3
    ERROR = 4
    CRITICAL = 5

# ----------------------------------------

# def convert_to_PIL(img)
def convert_to_PIL(func):

    def Inner(obj, *args, **kwargs):

        # print(type(args[0]))

        if isinstance(args[0], np.ndarray):
            newimg = Image.fromarray(args[0])
            result = func(obj, newimg, *args[1:], **kwargs)
        else:
            result = func(obj, *args, **kwargs)

        if obj.return_numpy:
            return np.array(result)
        else:
            return result

    return Inner


# ------------------

class Logger:

    def __init__(self, level = LoggingLevel.WARNING):

        self.header_styles = ["--- DEBUG: {} ---",
                              "--- INFO: {} ---",
                              "--! WARNING: {} ---",
                              "-!! ERROR: {} ---",
                              "!!! CRITICAL: {} ---"] 

        self.logging_level = level

    def header_styles(self, styles = []):

        if isinstance(styles, list):

            if len(list) == 5:
                print("assisgning")

                self.header_styles = styles
            else:

                print("List long less than 5")

        elif isinstance(styles, str):

            print("Asssignign")

            self.header_styles = [styles] * len(self.header_styles)

        else:

            print("ERROR NOT ASSIGNIGN")
            

    def set_logging_level(self, level):

        pass

    def display(self, min_level, text):

        if self.logging_level < min_level:
            return

        print(self.header_styles[self.logging_level-1].format(text))

    def debug(self, message):

        self.display(LoggingLevel.INFO, message)

    def info(self, message):

        self.display(LoggingLevel.INFO, message)

    def warning(self, message):

        self.display(LoggingLevel.WARNING, message)

    def error(self, message):

        self.display(LoggingLevel.ERROR, message)

    def critical(self, message):

        self.display(LoggingLevel.CRIICAL, message)


class DrawingParams:
    
    def __init__(self, kwargs):

        # self._color = colors[drawing_color]
        # self._bg_color = None
        # self._box_color = None
        # self._alpha = 1.0
        # self._font_size = 12
        # self._thickness = thickness if thickness is not None else 1 
        # self._linestyle = linestyle if linestyle is not None else '-'

        # self.anchor_preferred = Positions.TOPLEFT
        # self.anchor_force = False

        self._line_color = None
        self._line_thickness = None 
        self._line_style = None

        self._text_color = None
        self._text_fill_color = None
        self._text_font_size = None
        self._text_font = None

        self._points_color = None
        self._points_size = None
        self._points_fill_color = None

        self._box_fill_color = None
        self._box_text_anchor = None
        self._box_text_inside = None

        self._arrow_color = None
        self._arrow_thickness = None
        self._arrow_angle = None
        self._arrow_fill_color = None

        self.initialize(**kwargs)


    def initialize(self, **kwargs):

        for entry in kwargs.items():
            attrname = f"_{entry[0]}"
            if hasattr(self, attrname):
                setattr(self, attrname, entry[1])
            else:
                print(f"field {entry[0]} not available")


    def update(self, kwargs):

        self.initialize(**kwargs)


    @property
    def color(self, primitive): 
        return self._color

    @color.setter
    def color(self, name):

        if name in colors:
            self._color = colors[name]
        else:
            print("not found, kept old ")

    @property
    def bg_color(self): 
        return self._bg_color

    @bg_color.setter
    def bg_color(self, name):

        if name in colors:
            self._bg_color = colors[name]
        else:
            print("not found, kept old ")

    @property
    def box_color(self): 
        return self._box_color

    @box_color.setter
    def box_color(self, name):

        if name in colors:
            self._box_color = colors[name]
        else:
            print("not found, kept old ")

    @property
    def thickness(self): 
        return self._thickness

    @thickness.setter
    def thickness(self, value):

        if isinstance(value, int):
            self._thickness = value
        else:
            raise ValueError("value error")

    @property
    def font_size(self): 
        return self._font_size

    @font_size.setter
    def font_size(self, value):

        if isinstance(value, int):
            self._font_size = value
        else:
            raise ValueError("value error")

    def dump_style(self, filename):

        pass
    
    def load_style(self, filename):

        pass

class Drawer:


    def __init__(self):

        self.cached_image = None
        self.last_image  = None

        self.drawing_styles = dict()
        self.cur_style = None
        self._normalized = False

        self.return_numpy = False

    @property
    def style(self):

        return self.drawing_styles[self.cur_style]
            
    def add_style(self, style_name, kwargs):

        params = DrawingParams(kwargs)

        self.drawing_styles[style_name] = params

    def update_style(self, style_name, kwargs):

        self.drawing_styles[style_name].update(kwargs)

    def set_style(self, style_name):

        if style_name in self.drawing_styles.keys():
            self.cur_style = style_name
        else:
            print("style not found")

    @contextmanager
    def temp_style(self, style_name):

        try:
            previous_style = self.cur_style
            
            if style_name is not None:
                self.cur_style = style_name
                
        finally:
            self.cur_style = previous_style

    def set_normalized_coords(self, value):

        self._normalized = value

    def denormalize_points(self, points, shape):

        pass

    def keypoints(self, image, points, normalized = False, style = None):

        if self._normalized or normalized:
            points = self.denormalize_points(points, image.shape)

        with self.temp_style(style):
            pass

    @convert_to_PIL
    def box(self, image, point_tl, point_br, position = None, label = None, inner = False, normalized = False, apply_style = None):

        canvas = ImageDraw.Draw(image)

        # with self.temp_style(apply_style):
        canvas.rectangle(list(point_tl + point_br), fill=self.style._box_fill_color, outline=self.style._line_color, width=self.style._line_thickness)

        if label is not None:

            self.text(image)


        return image

    @convert_to_PIL
    def segments(self, image, segments, normalized = False, style = None):

        pass

    @convert_to_PIL
    def text(self, image, text_show = None, position = None, alignment = None, normalized = False, style = None):

        # DEBUG, prints on the bottom center of the image

        font = ImageFont.truetype("arial", 14)

        text_size = font.getsize("tentative text")
        prompt_size = (text_size[0]+10, text_size[1]+10)
        prompt_img = Image.new('RGBA', prompt_size, "black")
        prompt_draw = ImageDraw.Draw(prompt_img)
        prompt_draw.text((5, 5), "tentative text", font=font)
        image.paste(prompt_img, (int((image.size[0]/2)-(prompt_img.size[0]/2)), image.size[1]-prompt_img.size[1]))

        return image

    @convert_to_PIL
    def corner_text(self, image, text_show, position, normalized = False, style = None):

        pass

    @convert_to_PIL
    def overlay(self, image, text_show, position, offset_x, offset_y, normalized = False, style = None):

        pass

    @convert_to_PIL
    def side_text(self, image, text, side = "right", style = None):

        pass

    @convert_to_PIL
    def side_barplot(self, image, text, side = "right", style = None):

        pass

    @convert_to_PIL
    def side_plot(self, image, text, side = "right", style = None):

        pass

    @convert_to_PIL
    def mask(self, image, mask_show, style = None):

        pass

    @convert_to_PIL
    def polygon(self, image, points, normalized = False, style = None):

        pass

    @convert_to_PIL
    def arrow(self, image, points, normalized = False, style = None):

        pass

    @convert_to_PIL
    def arrow_and_text(self, image, label, offset_x, offset_y, points, normalized = False, style = None):

        pass

    def show(self, img, draw_axis = False):

        plt.imshow(img)

        if not draw_axis:
            plt.axis('off')
            plt.tight_layout()

        plt.show()