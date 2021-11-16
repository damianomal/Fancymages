
from PIL import Image, ImageDraw, ImageFont

from lib.utils.color_names import colors
from contextlib import contextmanager
from enum import Enum
import numpy as np
import matplotlib.pyplot as plt
import math

from lib.viz.parameters import DrawingParams

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

def convert_to_PIL(func):

    def wrapper(obj, *args, **kwargs):

        if isinstance(args[0], np.ndarray):
            newimg = Image.fromarray(args[0])
            result = func(obj, newimg, *args[1:], **kwargs)
        else:
            result = func(obj, *args, **kwargs)

        if obj.return_numpy:
            return np.array(result)
        else:
            return result

    return wrapper

# ------------------

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
                
            yield None

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

        image = image.convert("RGBA")

        canvas = ImageDraw.Draw(image)

        with self.temp_style(apply_style):

            canvas.rectangle(list(point_tl + point_br), fill=self.style._box_fill_color, outline=self.style._line_color, width=self.style._line_thickness)

            if text_show is not None:

                # font = ImageFont.truetype("arial", font_size)

                # text_size = font.getsize(text_show)
                # prompt_size = (text_size[0]+margin, text_size[1]+margin)
                # prompt_img = Image.new('RGBA', prompt_size, self.style._text_fill_color)
                # prompt_draw = ImageDraw.Draw(prompt_img)
                # half_margin = margin // 2
                # prompt_draw.text((half_margin, half_margin), text_show, font=font, fill=self.style._text_color)
                # coords = self.get_anchor_coordinates(image.size, prompt_img.size, list(point_tl + point_br), position, inner)
                # image.paste(prompt_img, coords)

                font = ImageFont.truetype("arial", font_size)

                txt_image = Image.new('RGBA', image.size, (0,0,0,0))

                prompt_draw = ImageDraw.Draw(txt_image)

                text_size = font.getsize(text_show)
                prompt_size = (text_size[0]+margin, text_size[1]+margin)
                half_margin = margin // 2
                coords = self.get_anchor_coordinates(image.size, prompt_size, list(point_tl + point_br), position, inner)

                box_coords = [coords[0]-half_margin, coords[1]-half_margin, coords[0]+prompt_size[0], coords[1]+prompt_size[1]]
                prompt_draw.rectangle(box_coords, fill=self.style._text_fill_color)

                prompt_draw.text(coords, text_show, fill=self.style._text_color, font=font)

                image = Image.alpha_composite(image, txt_image)    

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

        # font = ImageFont.truetype("arial", font_size)

        # text_size = font.getsize(text_show)
        # prompt_size = (text_size[0]+margin, text_size[1]+margin)
        # prompt_img = Image.new('RGBA', prompt_size, self.style._text_fill_color)
        # prompt_draw = ImageDraw.Draw(prompt_img)
        # half_margin = margin // 2
        # prompt_draw.text((half_margin, half_margin), text_show, font=font, fill=self.style._text_color)
        # coords = self.get_coordinates(image.size, prompt_img.size, alignment)
        # image.paste(prompt_img, coords)


        font = ImageFont.truetype("arial", font_size)

        txt_image = Image.new('RGBA', image.size, (0,0,0,0))

        prompt_draw = ImageDraw.Draw(txt_image)

        text_size = font.getsize(text_show)
        prompt_size = (text_size[0]+margin, text_size[1]+margin)
        half_margin = margin // 2
        # coords = self.get_anchor_coordinates(image.size, prompt_size, list(point_tl + point_br), position, inner)
        coords = self.get_coordinates(image.size, prompt_size, alignment)

        box_coords = [coords[0]-half_margin, coords[1]-half_margin, coords[0]+prompt_size[0], coords[1]+prompt_size[1]]
        prompt_draw.rectangle(box_coords, fill=self.style._text_fill_color)

        prompt_draw.text(coords, text_show, fill=self.style._text_color, font=font)

        image = Image.alpha_composite(image, txt_image)    

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