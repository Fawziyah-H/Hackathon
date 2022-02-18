from tkinter import *
import tkinter.font as font
import tkinter.ttk as tkk
from calibration import Calibrate
from inking import DigitalInking


#default values for settings
low = 0.15
high = 0.25
domHand = "Right"


#consulted https://www.geeksforgeeks.org/tkinter-application-to-switch-between-different-page-frames/
class Menu(Tk):
    def __init__(self, *args, **kwargs):
        Tk.__init__(self, *args, **kwargs)
        container = Frame(self)
        container.pack(fill=BOTH,expand=1)
        self.wm_title("Digital Inking with Gesture Recognition")
        self.geometry("500x400")

        container.grid_rowconfigure(0, weight = 1)
        container.grid_columnconfigure(0, weight = 1)
        container.grid_rowconfigure(2, weight = 1)
        container.grid_columnconfigure(2, weight = 1)

        self.frames = {}
        pages = (MainMenu, SettingPage)
        for F in pages:
            frame = F(container,self)
            self.frames[F] = frame
            frame.grid(row = 0, column = 0, sticky ="nsew")

        self.showFrame(MainMenu)

    def showFrame(self,cont):
        frame = self.frames[cont]
        frame.tkraise()


class MainMenu(Frame):
    def __init__(self, parent, controller):
        Frame.__init__(self,parent)
        #self.low = 0
        #self.high = 0

        title = tkk.Label(self, text="Digital Inking", font=("Verdana",35))
        title.grid(row = 0, column = 4, padx = 10, pady = 10)

        inkingButton = Button(self, text="Start Inking", command=self.startInking)
        inkingButton['font'] = font.Font(size=20)
        inkingButton.grid(row = 1, column = 4, padx = 10, pady = 10)
        #inkingButton.place(x=150, y=200)

        settingsBtn = Button(self,text="Settings",command=lambda: controller.showFrame(SettingPage))
        settingsBtn['font'] = font.Font(size=20)
        settingsBtn.grid(row = 2, column = 4, padx = 10, pady = 10)

    def startInking(self):
        global high,low,domHand
        """if low == 0 and high == 0:
            low = 0.15
            high = 0.25"""
        inking = DigitalInking(low,high,domHand)
        inking.ink()

class SettingPage(Frame):
    def __init__(self,parent,controller):
        Frame.__init__(self,parent)
        global domHand

        title = tkk.Label(self, text="Settings", font=("Verdana",35))
        title.grid(row = 0, column = 2, padx = 10, pady = 10)
        calibrateButton = Button(self, text="Calibrate Pressure",command=self.clickCalibrate)
        calibrateButton['font'] = font.Font(size=20)
        calibrateButton.grid(row = 2, column = 2, padx = 10, pady = 10)

        self.selected = StringVar()
        self.selected.set(domHand)
        domHandFrm = tkk.LabelFrame(self)
        domHandFrm['text'] = "Dominant Hand"
        leftHand = tkk.Radiobutton(domHandFrm,text="Left",value="Left",variable=self.selected, command=self.selectDomHand)
        leftHand.grid(column=0, row=0, padx=5, pady=5)
        rightHand = tkk.Radiobutton(domHandFrm,text="Right",value="Right",variable=self.selected, command=self.selectDomHand)
        rightHand.grid(column=1, row=0, padx=5, pady=5)
        domHandFrm.grid(row = 3, column = 2, padx = 10, pady = 10)


        backBtn = Button(self, text="Back", command=lambda: controller.showFrame(MainMenu))
        backBtn.grid(row = 4, column = 1, padx = 10, pady = 10)

        
    def selectDomHand(self):
        global domHand
        domHand = self.selected.get()
        #print("New dom:", str(domHand))
    
    def clickCalibrate(self):
        global high,low,domHand
        cal = Calibrate(dominant=domHand)
        cal.calibrate_pressure()
        low = cal.get_low()
        high = cal.get_high()

"""
class Window(Frame):

    def __init__(self, master=None):
        Frame.__init__(self, master)        
        self.master = master

        # widget can take all window
        self.pack(fill=BOTH, expand=1)

        self.myFont = font.Font(size=20)

        self.low = 0
        self.high = 0
"""

    
app = Menu()   
app.mainloop()