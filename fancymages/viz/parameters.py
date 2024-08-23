

from lib.utils.processing import suggest, similar


class DrawingParams:
    
    def __init__(self, logger, kwargs):

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

        self._mask_color = None

        self.logger = logger

        self.initialize(**kwargs)


    def preprocess(self, entries):

        polished = dict()

        for entry in entries.items():
            if entry[1] == "transparent":
                polished.update({entry[0]: (0,0,0,0)})
            else:
                polished.update({entry[0]: entry[1]})

        return polished

    def initialize(self, **kwargs):

        entries = self.preprocess(kwargs)

        for entry in entries.items():
            attrname = f"_{entry[0].replace(' ', '_')}"
            if hasattr(self, attrname):
                setattr(self, attrname, entry[1])
            else:
                self.logger.warning(f"field {entry[0]} not found")
                candidates = suggest(self.__dict__.keys(), entry[0], similar)
                candidates = [cand.replace('_', ' ').strip() for cand in candidates]
                self.logger.warning(f"maybe you meant: {', '.join(candidates)}")


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