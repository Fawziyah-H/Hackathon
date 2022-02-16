from tkinter import *
import tkinter.font as font
from calibration import Calibrate
from inking import DigitalInking

class Window(Frame):

    def __init__(self, master=None):
        Frame.__init__(self, master)        
        self.master = master

        # widget can take all window
        self.pack(fill=BOTH, expand=1)

        self.myFont = font.Font(size=20)

        self.low = 0
        self.high = 0

        calibrateButton = Button(self, text="Calibrate Pressure",command=self.clickCalibrate)
        calibrateButton['font'] = self.myFont
        calibrateButton.place(x=100, y=80)

        inkingButton = Button(self, text="Start Inking", command=self.startInking)
        inkingButton['font'] = self.myFont
        inkingButton.place(x=150, y=200)

    def clickCalibrate(self):
        cal = Calibrate()
        cal.calibrate_pressure()
        self.low = cal.get_low()
        self.high = cal.get_high()

    def startInking(self):
        if self.low == 0 and self.high == 0:
            self.low = 0.15
            self.high = 0.25
        inking = DigitalInking(self.low,self.high)
        inking.ink()
        
root = Tk()
app = Window(root)
root.wm_title("Tkinter button")
root.geometry("500x400")
root.mainloop()