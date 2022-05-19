
from PIL import Image, ImageDraw, ImageFont

from lib.utils.color_names import colors
from contextlib import contextmanager
from enum import Enum
import numpy as np
import matplotlib.pyplot as plt
import math
import string 

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
    
# ----------------------------------------

def convert_to_PIL(func):

    def wrapper(obj, *args, **kwargs):

        if isinstance(args[0], np.ndarray):
            newimg = Image.fromarray(args[0])
            result = func(obj, newimg, *args[1:], **kwargs)
        else:
            result = func(obj, *args, **kwargs)

        if obj.last_image is not None:
            del obj.last_image

        obj.last_image = result

        if obj.return_numpy:
            return np.array(result)
        else:
            return result

    return wrapper

def not_implemented(func):

    def wrapper(obj, *args, **kwargs):

        print()
        print(f"!! Function {func.__name__} still not implemented!")
        print()

    return wrapper

# ------------------

class Drawer:


    def __init__(self, logger):

        self.cached_image = None
        self.last_image  = None

        self.drawing_styles = dict()
        self.cur_style = None
        self.previous_style = None
        self._normalized = False

        self.return_numpy = False
        self.logger = logger

        self.snapshots = list()


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

        applied = False

        try:

            if self.previous_style is None:

                self.previous_style = self.cur_style
                
                if style_name is not None:
                    self.cur_style = style_name
                    
                applied = True

            yield None

        finally:

            if applied:

                self.cur_style = self.previous_style
                self.previous_style = None

    def set_normalized_coords(self, value):

        self._normalized = value

    @not_implemented
    def denormalize_points(self, points, shape):

        pass

    def get_circle(self, x, y, radius):

        top_left = (x - radius, y - radius)
        bottom_right = (x + radius, y + radius)
        circle_boundary = [top_left, bottom_right]
        
        return circle_boundary

    def process_labels(self, labels, points):

        # TODO: change this to a dictionary of lambda functions

        if labels == "numbers":
            labels = [str(i+1) for i in range(len(points))]

        if labels == "numbers-0":
            labels = [str(i) for i in range(len(points))]

        if labels == "letters":
            labels = string.ascii_lowercase[:len(points)]

        return labels

    @convert_to_PIL
    def keypoints(self, image, points = None, labels = None, font_size = None, normalized = False, apply_style = None):

        if labels is not None:
            labels = self.process_labels(labels, points)

        canvas = ImageDraw.Draw(image)
        font = ImageFont.truetype("arial", font_size if font_size is not None else self.style._text_font_size)

        with self.temp_style(apply_style):

            for idx, point in enumerate(points):

                circle = self.get_circle(point[0], point[1], self.style._points_size)
                canvas.ellipse(circle, fill=self.style._points_color, outline=self.style._points_outline_color, width=self.style._points_outline_thickness)

                if labels is not None and idx < len(labels):
                    
                    coords = [circle[0][0], circle[0][1]]
                    coords[0] += self.style._points_size + 10
                    coords[1] -= self.style._points_size + 10
                    
                    canvas.text(coords, labels[idx], font=font, fill=self.style._text_color)


        return image


    def get_anchor_coordinates(self, image_size, text_size, box_coords, position, inner, box_thickness, margin):

        half_margin = margin/2.0

        if "left" in position:

            box_xmin = box_coords[0] 
            box_xmax = box_xmin + text_size[0] + margin

            if inner:
                box_xmin += box_thickness
                box_xmax += box_thickness

            x_coord = box_xmin + half_margin

        elif "center" in position:
            x_coord = box_coords[2]/2.0 - text_size[0]/2.0
            box_xmin = x_coord - half_margin
            box_xmax = box_xmin + text_size[0] + margin

        elif "right" in position:

            box_xmin = box_coords[2] - text_size[0] - margin 
            box_xmax = box_coords[2]

            if inner:
                box_xmin -= box_thickness
                box_xmax -= box_thickness

            x_coord = box_xmin + half_margin
        else:
            raise ValueError("wrong x position")

        if "top" in position:
            if inner:

                box_ymin = box_coords[1] + box_thickness 
                box_ymax = box_ymin + text_size[1] + margin 

                y_coord = box_ymin + half_margin
            else:
                box_ymin = box_coords[1] - text_size[1] - margin 
                box_ymax = box_coords[1]

                y_coord = box_ymin + half_margin
        elif "bottom" in position:
            if inner:

                box_ymin = box_coords[3] - box_thickness - text_size[1] - margin
                box_ymax = box_coords[3] - box_thickness 

                y_coord = box_ymin + half_margin
            else:
                box_ymin = box_coords[3]
                box_ymax = box_ymin + text_size[1] + margin 
                
                y_coord = box_ymin + half_margin
        else:
            raise ValueError("wrong y position")

        bg_box_coords = [box_xmin, box_ymin, box_xmax, box_ymax]

        return (int(x_coord), int(y_coord)), bg_box_coords


    @convert_to_PIL
    def box(self, image, point_tl, point_br, font_size = None, margin = 5, color = None, text_color = None, position = "top left", label = None, inner = False, normalized = False, apply_style = None):

        image = image.convert("RGBA")

        canvas = ImageDraw.Draw(image)

        with self.temp_style(apply_style):

            box_color = color if color is not None else self.style._line_color

            canvas.rectangle(list(point_tl + point_br), fill=self.style._box_fill_color, outline=box_color, width=self.style._line_thickness)

            if label is not None:

                font = ImageFont.truetype("arial", font_size if font_size is not None else self.style._text_font_size)

                txt_image = Image.new('RGBA', image.size, (0,0,0,0))

                prompt_draw = ImageDraw.Draw(txt_image)

                text_size = font.getsize(label)
                prompt_size = (text_size[0], text_size[1])
                coords, box_coords = self.get_anchor_coordinates(image.size, prompt_size, list(point_tl + point_br), position, inner, self.style._line_thickness, margin)

                text_fill_color = color if color is not None else self.style._text_fill_color
                prompt_draw.rectangle(box_coords, fill=text_fill_color)

                text_real_color = text_color if text_color is not None else self.style._text_color
                prompt_draw.text(coords, label, fill=text_real_color, font=font)

                image = Image.alpha_composite(image, txt_image)    

        return image

    @convert_to_PIL
    def segments(self, image, segments, thickness = None, normalized = False, apply_style = None):

        with self.temp_style(apply_style):

            canvas = ImageDraw.Draw(image)

            for segment in segments:

                real_thickness = thickness if thickness  is not None else self.style._line_thickness
                canvas.line(segment, fill=self.style._line_color, width=real_thickness)

            return image

    def get_coordinates(self, image_size, text_size, alignment, margin):

        half_margin = margin/2.0

        if "left" in alignment:
            x_coord = half_margin
            box_xmin = 0
            box_xmax = text_size[0]+margin
        elif "center" in alignment:
            x_coord = image_size[0]/2.0 - text_size[0]/2.0
            box_xmin = x_coord - half_margin
            box_xmax = box_xmin + text_size[0] + margin
        elif "right" in alignment:
            x_coord = image_size[0] - text_size[0] - half_margin
            box_xmin = image_size[0] - text_size[0] - margin
            box_xmax = image_size[0]
        else:
            raise ValueError("wrong x alignment")

        if "top" in alignment:
            y_coord = half_margin
            box_ymin = 0
            box_ymax = text_size[1]+margin
        elif "middle" in alignment:
            y_coord = image_size[1]/2.0 - text_size[1]/2.0
            box_ymin = y_coord - half_margin
            box_ymax = box_ymin + text_size[1] + margin
        elif "bottom" in alignment:
            box_ymin = image_size[1] - text_size[1] - margin
            box_ymax = image_size[1]

            y_coord = box_ymin + half_margin
        else:
            raise ValueError("wrong y alignment")

        box_coords = [box_xmin, box_ymin, box_xmax, box_ymax]

        return (int(x_coord), int(y_coord)), box_coords

    @convert_to_PIL
    def text_anchor(self, image, margin = 20, font_size = None, text_show = "empty", position = None, alignment = "bottom center", normalized = False, apply_style = None):

        image = image.convert("RGBA")

        with self.temp_style(apply_style):

            font = ImageFont.truetype("arial", font_size if font_size is not None else self.style._text_font_size)

            txt_image = Image.new('RGBA', image.size, (0,0,0,0))

            prompt_draw = ImageDraw.Draw(txt_image)

            text_size = font.getsize(text_show)
            prompt_size = (text_size[0], text_size[1])

            coords, box_coords = self.get_coordinates(image.size, prompt_size, alignment, margin)

            prompt_draw.rectangle(box_coords, fill=self.style._text_fill_color)
            prompt_draw.text(coords, text_show, fill=self.style._text_color, font=font)

        
        image = Image.alpha_composite(image, txt_image)    

        return image

    def snapshot(self, image):
        self.snapshots.append(image.copy())

    def snapshot(self):
        self.snapshots.append(self.last_image)

    def show_snapshots(self):
        for snap in self.snapshots:
            self.show(snap)

    @convert_to_PIL
    def text(self, image, coords = None, margin = 30, font_size = None, text_show = "empty", position = None, alignment = "bottom center", normalized = False, apply_style = None):

        image = image.convert("RGBA")

        with self.temp_style(apply_style):
    
            font = ImageFont.truetype("arial", font_size if font_size is not None else self.style._text_font_size)

            # text_size = font.getsize(text_show)
            # prompt_size = (text_size[0]+margin, text_size[1]+margin)
            # prompt_img = Image.new('RGBA', prompt_size, self.style._text_fill_color)
            # prompt_draw = ImageDraw.Draw(prompt_img)
            # half_margin = margin // 2
            # prompt_draw.text((half_margin, half_margin), text_show, font=font, fill=self.style._text_color)
            # # coords = self.get_coordinates(image.size, prompt_img.size, alignment)
            # image.paste(prompt_img, coords)

            half_margin = margin // 2

            txt_image = Image.new('RGBA', image.size, (0,0,0,0))
            prompt_draw = ImageDraw.Draw(txt_image)

            text_size = font.getsize(text_show)

            box_coords = [coords[0] - half_margin, coords[1] - half_margin, coords[0] + text_size[0] + half_margin, coords[1] + text_size[1] + half_margin]

            prompt_draw.rectangle(box_coords, fill=self.style._text_fill_color)
            prompt_draw.text(coords, text_show, fill=self.style._text_color, font=font)

            image = Image.alpha_composite(image, txt_image)

        return image

    @convert_to_PIL
    @not_implemented
    def overlay(self, image, text_show, position, offset_x, offset_y, normalized = False, apply_style = None):

        pass
    
    @convert_to_PIL
    @not_implemented
    def side_text(self, image, text, side = "right", apply_style = None):

        pass

    @convert_to_PIL
    @not_implemented
    def side_barplot(self, image, text, side = "right", apply_style = None):

        pass

    @convert_to_PIL
    @not_implemented
    def side_plot(self, image, text, side = "right", apply_style = None):

        pass

    @convert_to_PIL
    def mask(self, image, mask_show = None, color = None, apply_style = None):

        mask_show = mask_show.convert("L")

        if isinstance(mask_show, np.ndarray):
            mask_show = Image.fromarray(mask_show)

        mask_real_color = color if color is not None else self.style._mask_color

        mask_color = Image.new('RGB', mask_show.size, mask_real_color)

        image = Image.composite(mask_color, image, mask_show)

        return image        

    @convert_to_PIL
    def polygon(self, image, points = None, draw_points = False, normalized = False, apply_style = None):

        canvas = ImageDraw.Draw(image)

        with self.temp_style(apply_style):

            points_tuples = [tuple(p) for p in points]

            canvas.polygon(points_tuples, fill=self.style._box_fill_color)

            list_of_points = list(points) + points[:2]

            canvas.line([item for sublist in list_of_points for item in sublist], fill=self.style._line_color, width=self.style._line_thickness, joint = "curve")

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

        if filled:
            canvas = ImageDraw.Draw(image)
            canvas.polygon([tuple(p2),tuple(p2+p3),tuple(p2+p4)], fill=self.style._line_color)
        else:
            tips = [[*p2, *(p2+p3)], [*p2, *(p2+p4)]]
            image = self.segments(image, tips)

        return image

    @convert_to_PIL
    def arrow(self, image, points = None, filled = False, tip_length = 25, normalized = False, apply_style = None):

        with self.temp_style(apply_style):

            image = self.segments(image, [[*points[0], *points[1]]])
            image = self.arrowhead(image, points, filled, tip_length)

        return image

    @convert_to_PIL
    def skeleton(self, image, joints = None, bones = None, labels = None, font_size = None, normalized = False, apply_style = None):

        real_bones = list()

        with self.temp_style(apply_style):
        
            for bone in bones:
                if bone is not None:
                    real_bones.append([*joints[bone[0]],*joints[bone[1]]])

            image = self.segments(image, real_bones)
            image = self.keypoints(image, joints, labels, font_size = font_size)

        return image
        
    @convert_to_PIL
    def arrow_and_text(self, image, label, offset_x, offset_y, points, normalized = False, apply_style = None):

        pass

    def show(self, image, draw_axis = False):

        plt.imshow(image)

        if not draw_axis:
            plt.axis('off')
            plt.tight_layout()

        plt.show()