
from PIL import Image, ImageDraw, ImageFont

from lib.utils.color_names import colors
from contextlib import contextmanager
from enum import Enum
import numpy as np
import matplotlib.pyplot as plt
import math

from lib.utils.processing import suggest, similar

# ----------------------------------------

class Positions(int, Enum):

    TOPLEFT = 1
    TOP = 2
    TOPRIGHT = 3
    LEFT = 4
    CENTER = 5
    RIGHT = 6
    BOTTOMLEFT = 7
    BOTTOM = 8
    BOTTOMRIGHT = 9

class LoggingLevel(int, Enum):

    DEBUG = 1
    INFO = 2
    WARNING = 3
    ERROR = 4
    CRITICAL = 5

# ----------------------------------------

# def convert_to_PIL(img)
def convert_to_PIL(func):

    def Inner(obj, *args, **kwargs):

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

        self.logging_level = level

    def display(self, min_level, text):

        if min_level < self.logging_level:
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
    
    def __init__(self, logger, kwargs):

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
        self._points_outline_color = None
        self._points_outline_thickness = None

        self._box_fill_color = None
        self._box_text_anchor = None
        self._box_text_inside = None

        self._arrow_color = None
        self._arrow_thickness = None
        self._arrow_angle = None
        self._arrow_fill_color = None

        self._mask_color = None

        self.logger = logger

        self.initialize(**kwargs)


    def initialize(self, **kwargs):

        for entry in kwargs.items():
            attrname = f"_{entry[0].replace(' ', '_')}"
            if hasattr(self, attrname):
                setattr(self, attrname, entry[1])
            else:
                self.logger.warning(f"field {entry[0]} not found")
                aaa = suggest(self.__dict__.keys(), entry[0], similar)
                aaa = [a.replace('_', ' ').strip() for a in aaa]
                self.logger.warning(f"maybe you meant: {', '.join(aaa)}")


    def update(self, kwargs):

        self.initialize(**kwargs)


    # @property
    # def color(self, primitive): 
    #     return self._color

    # @color.setter
    # def color(self, name):

    #     if name in colors:
    #         self._color = colors[name]
    #     else:
    #         print("not found, kept old ")

    # @property
    # def bg_color(self): 
    #     return self._bg_color

    # @bg_color.setter
    # def bg_color(self, name):

    #     if name in colors:
    #         self._bg_color = colors[name]
    #     else:
    #         print("not found, kept old ")

    # @property
    # def box_color(self): 
    #     return self._box_color

    # @box_color.setter
    # def box_color(self, name):

    #     if name in colors:
    #         self._box_color = colors[name]
    #     else:
    #         print("not found, kept old ")

    # @property
    # def thickness(self): 
    #     return self._thickness

    # @thickness.setter
    # def thickness(self, value):

    #     if isinstance(value, int):
    #         self._thickness = value
    #     else:
    #         raise ValueError("value error")

    # @property
    # def font_size(self): 
    #     return self._font_size

    # @font_size.setter
    # def font_size(self, value):

    #     if isinstance(value, int):
    #         self._font_size = value
    #     else:
    #         raise ValueError("value error")

    def dump_style(self, filename):

        pass
    
    def load_style(self, filename):

        pass

class Drawer:


    def __init__(self, logger):

        self.cached_image = None
        self.last_image  = None

        self.drawing_styles = dict()
        self.cur_style = None
        self._normalized = False

        self.return_numpy = False
        self.logger = logger

    @property
    def style(self):

        return self.drawing_styles[self.cur_style]
            
    def add_style(self, style_name, kwargs):

        params = DrawingParams(self.logger, kwargs)

        self.drawing_styles[style_name] = params

    def update_style(self, style_name, kwargs):

        self.drawing_styles[style_name].update(kwargs)

    def update_current_style(self, kwargs):

        self.drawing_styles[self.cur_style].update(kwargs)


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

    def get_circle(self, x, y, radius):

        top_left = (x - radius, y - radius)
        bottom_right = (x + radius, y + radius)
        twoPointList = [top_left, bottom_right]
        
        return twoPointList

    @convert_to_PIL
    def keypoints(self, image, points = None, labels = None, font_size = 24, normalized = False, style = None):

        # if self._normalized or normalized:
        #     points = self.denormalize_points(points, image.shape)

        # with self.temp_style(style):
        #     pass

        canvas = ImageDraw.Draw(image)
        font = ImageFont.truetype("arial", font_size)

        for idx, point in enumerate(points):

            circle = self.get_circle(point[0], point[1], self.style._points_size)
            canvas.ellipse(circle, fill=self.style._points_color, outline=self.style._points_outline_color, width=self.style._points_outline_thickness)

            if labels is not None and idx < len(labels):
                
                coords = [circle[0][0], circle[0][1]]
                coords[0] += self.style._points_size + 10
                coords[1] -= self.style._points_size + 10
                
                canvas.text(coords, labels[idx], font=font, fill=self.style._text_color)


        return image

    def get_anchor_coordinates(self, image_size, text_size, box_coords, position, inner):

        if "left" in position:
            x_coord = box_coords[0]
        elif "center" in position:
            x_coord = box_coords[2]/2.0 - text_size[0]/2.0
        elif "right" in position:
            x_coord = box_coords[2] - text_size[0]
        else:
            raise ValueError("wrong x position")

        if "top" in position:
            if inner:
                y_coord = box_coords[1]
            else:
                y_coord = box_coords[1] - text_size[1]
        elif "bottom" in position:
            if inner:
                y_coord = box_coords[3] - text_size[1]
            else:
                y_coord = box_coords[3]
        else:
            raise ValueError("wrong y position")

        return (int(x_coord), int(y_coord))


    @convert_to_PIL
    def box(self, image, point_tl, point_br, font_size = 12, margin = 5, position = "top left", text_show = None, inner = False, normalized = False, apply_style = None):

        canvas = ImageDraw.Draw(image)

        # with self.temp_style(apply_style):
        canvas.rectangle(list(point_tl + point_br), fill=self.style._box_fill_color, outline=self.style._line_color, width=self.style._line_thickness)

        if text_show is not None:

            font = ImageFont.truetype("arial", font_size)

            text_size = font.getsize(text_show)
            prompt_size = (text_size[0]+margin, text_size[1]+margin)
            prompt_img = Image.new('RGBA', prompt_size, self.style._text_fill_color)
            prompt_draw = ImageDraw.Draw(prompt_img)
            half_margin = margin // 2
            prompt_draw.text((half_margin, half_margin), text_show, font=font, fill=self.style._text_color)
            coords = self.get_anchor_coordinates(image.size, prompt_img.size, list(point_tl + point_br), position, inner)
            image.paste(prompt_img, coords)


        return image

    @convert_to_PIL
    def segments(self, image, segments, normalized = False, style = None):

        canvas = ImageDraw.Draw(image)

        for segment in segments:
            canvas.line(segment, fill=self.style._line_color, width=self.style._line_thickness)

        return image

    def get_coordinates(self, image_size, text_size, alignment):

        if "left" in alignment:
            x_coord = 0
        elif "center" in alignment:
            x_coord = image_size[0]/2.0 - text_size[0]/2.0
        elif "right" in alignment:
            x_coord = image_size[0] - text_size[0]
        else:
            raise ValueError("wrong x alignment")

        if "top" in alignment:
            y_coord = 0
        elif "middle" in alignment:
            y_coord = image_size[1]/2.0 - text_size[1]/2.0
        elif "bottom" in alignment:
            y_coord = image_size[1] - text_size[1]
        else:
            raise ValueError("wrong y alignment")

        return (int(x_coord), int(y_coord))

    @convert_to_PIL
    def text_anchor(self, image, margin = 20, font_size = 32, text_show = "empty", position = None, alignment = "bottom center", normalized = False, style = None):

        font = ImageFont.truetype("arial", font_size)

        text_size = font.getsize(text_show)
        prompt_size = (text_size[0]+margin, text_size[1]+margin)
        prompt_img = Image.new('RGBA', prompt_size, self.style._text_fill_color)
        prompt_draw = ImageDraw.Draw(prompt_img)
        half_margin = margin // 2
        prompt_draw.text((half_margin, half_margin), text_show, font=font, fill=self.style._text_color)
        coords = self.get_coordinates(image.size, prompt_img.size, alignment)
        image.paste(prompt_img, coords)

        return image

    @convert_to_PIL
    def text(self, image, coords = None, margin = 30, font_size = 32, text_show = "empty", position = None, alignment = "bottom center", normalized = False, style = None):

        font = ImageFont.truetype("arial", font_size)

        text_size = font.getsize(text_show)
        prompt_size = (text_size[0]+margin, text_size[1]+margin)
        prompt_img = Image.new('RGBA', prompt_size, self.style._text_fill_color)
        prompt_draw = ImageDraw.Draw(prompt_img)
        half_margin = margin // 2
        prompt_draw.text((half_margin, half_margin), text_show, font=font, fill=self.style._text_color)
        # coords = self.get_coordinates(image.size, prompt_img.size, alignment)
        image.paste(prompt_img, coords)

        return image

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
    def polygon(self, image, points = None, draw_points = False, normalized = False, style = None):

        canvas = ImageDraw.Draw(image)

        points_tuples = [tuple(p) for p in points]

        canvas.polygon(points_tuples, fill=self.style._box_fill_color)

        segments = list()

        for i in range(len(points)):

            i2 = (i+1) % len(points)
            segments.append([*points[i], *points[i2]])

        image = self.segments(image, segments)

        if draw_points:
            image = self.keypoints(image, points)

        return image


    def rotate_origin_only(self, xy, radians):
        
        x, y = xy
        xx = x * math.cos(radians) + y * math.sin(radians)
        yy = -x * math.sin(radians) + y * math.cos(radians)

        return xx, yy

    def arrowhead(self, image, points, filled, length):

        p1 = np.array(points[0])
        p2 = np.array(points[1])

        direction = (p1 - p2) / np.linalg.norm(p1 - p2)

        direction *= length

        radians = 0.4

        p3 = self.rotate_origin_only(direction, radians)
        p4 = self.rotate_origin_only(direction, -radians)

        tips = [[*p2, *(p2+p3)], [*p2, *(p2+p4)]]

        image = self.segments(image, tips)

        return image

    @convert_to_PIL
    def arrow(self, image, points = None, filled = False, tip_length = 25, normalized = False, style = None):

        # print([*points[0], *points[1]])

        image = self.segments(image, [[*points[0], *points[1]]])
        image = self.arrowhead(image, points, filled, tip_length)

        return image

    @convert_to_PIL
    def skeleton(self, image, joints = None, bones = None, labels = None, normalized = False, style = None):

        real_bones = list()

        for bone in bones:
            real_bones.append([*joints[bone[0]],*joints[bone[1]]])

        image = self.segments(image, real_bones)
        image = self.keypoints(image, joints, labels)

        return image
        
    @convert_to_PIL
    def arrow_and_text(self, image, label, offset_x, offset_y, points, normalized = False, style = None):

        pass

    def show(self, image, draw_axis = False):

        plt.imshow(image)

        if not draw_axis:
            plt.axis('off')
            plt.tight_layout()

        plt.show()