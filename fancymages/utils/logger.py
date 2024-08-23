from enum import Enum

class LoggingLevel(int, Enum):

    DEBUG = 1
    INFO = 2
    WARNING = 3
    ERROR = 4
    CRITICAL = 5


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

