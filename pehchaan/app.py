# imports - compatibility packages
from __future__ import absolute_import

# imports - standard packages
from collections import defaultdict
try:
    import Tkinter as tk
except ImportError:
    import tkinter as tk
import pickle

# imports - third party
from PIL import Image, ImageDraw
import numpy as np

# imports - pehchaan
from pehchaan import AppConfig
from pehchaan._util.const import ABSPATH_MODEL_DHCD_SVC, ABSPATH_ENCODER_DHCD, DHCD_INPUT_SIZE
from pehchaan._util import _get_version_string, _image_to_input

class App(object):
    class Frame(tk.Tk):
        BUTTON_CLEAR   = 'clear'
        BUTTON_PREDICT = 'predict'

        def __init__(self,
                     master     = None,
                     windowSize = (AppConfig.WINDOW_WIDTH, AppConfig.WINDOW_HEIGHT)):
            self.master     = master
            self.windowSize = windowSize

            tk.Frame.__init__(self, master)
            self.createUI()

        def createUI(self):
            currrow       = 0
            width, height = self.windowSize
            self.canvas   = tk.Canvas(self.master,
                                      width              = width,
                                      height             = width,
                                      highlightthickness = 0,
                                      background         = AppConfig.CANVAS_BACKGROUND_COLOR)
            self.canvas.grid(row        = currrow,
                             column     = 0,
                             columnspan = 2,
                             sticky     = tk.E + tk.W)
            currrow      += 1
            self.canvas.bind('<B1-Motion>', lambda event: self.paintPoint(event.x, event.y, thickness = 6))

            self.createPILImage()

            self.button    = defaultdict(tk.Button)
            self.button[App.Frame.BUTTON_CLEAR]   = tk.Button(self.master,
                                                              text    = App.Frame.BUTTON_CLEAR.capitalize(),
                                                              command = self.clear)
            self.button[App.Frame.BUTTON_CLEAR].grid(row    = currrow,
                                                     column = 0,
                                                     sticky = tk.E + tk.W)

            self.button[App.Frame.BUTTON_PREDICT] = tk.Button(self.master,
                                                              text    = App.Frame.BUTTON_PREDICT.capitalize())
            self.button[App.Frame.BUTTON_PREDICT].grid(row    = currrow,
                                                       column = 1,
                                                       sticky = tk.E + tk.W)
            currrow      += 1

            self.output   = tk.Canvas(self.master,
                                      width              = width,
                                      height             = width,
                                      highlightthickness = 0,
                                      background         = '#FFFFFF')
            self.output.grid(row        = currrow,
                             column     = 0,
                             columnspan = 2,
                             sticky     = tk.E + tk.W)

        def setOutput(self, output):
            width, height = self.windowSize
            self.clearOutput()

            self.output.create_text(width/2, height * 0.25 / 2,
                                    font = 'Helvetica 30',
                                    text = output)

        def clearCanvas(self):
            self.canvas.delete('all')

        def clearOutput(self):
            self.output.delete('all')

        def paintPoint(self, x, y,
                       thickness = 0,
                       color     = '#FFFFFF'):
            a, b   = x - thickness, y - thickness
            c, d   = x + thickness, y + thickness
            points = [a, b, c, d]

            self.canvas.create_oval(points, fill = color)
            self.imageDraw.ellipse (points, color)

        def clear(self):
            self.clearCanvas()
            self.clearOutput()
            self.createPILImage()

        def createPILImage(self):
            width, height  = self.windowSize
            self.image     = Image.new('RGB', (width, width), AppConfig.CANVAS_BACKGROUND_COLOR)
            self.imageDraw = ImageDraw.Draw(self.image)

    def __init__(self,
                 windowSize = (AppConfig.WINDOW_WIDTH, AppConfig.WINDOW_HEIGHT)):
        self.root       = tk.Tk()
        self.windowSize = windowSize

        self.root.title('{name} v{version}'.format(
            name    = AppConfig.NAME,
            version = _get_version_string()
        ))
        width, height   = self.windowSize
        self.root.geometry('{width}x{height}'.format(width = width, height = height))
        self.root.resizable(width  = False,
                            height = False)

        self.frame      = App.Frame(self.root, self.windowSize)
        self.frame.button[App.Frame.BUTTON_PREDICT].config(command = self.predict)

        with open(ABSPATH_MODEL_DHCD_SVC, 'rb') as f:
            self.model   = pickle.load(f)

        with open(ABSPATH_ENCODER_DHCD, 'rb') as f:
            self.encoder = pickle.load(f)

    def predict(self):
        image = self.frame.image
        image.thumbnail(DHCD_INPUT_SIZE, Image.BICUBIC)

        arr   = _image_to_input(image)
        arr   = np.reshape(arr, (1, arr.size))
        out   = self.model.predict(arr)
        sym   = self.encoder.inverse_transform(out[0])

        self.frame.setOutput(sym)

    def run(self):
        self.root.mainloop()
