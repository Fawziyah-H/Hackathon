from textwrap import wrap
from tkinter import *
import tkinter.ttk as tkk
from calibration import Calibrate
from inking import DigitalInking

#default values for settings
low = 0.15
high = 0.25
domHand = "Right"

#fonts and colours used
bgcolour = '#A4DEFF'
btncolour = '#FFF0F5'
titleFont = "Freestyle Script"
btnFont = "Calibri"

#consulted https://www.geeksforgeeks.org/tkinter-application-to-switch-between-different-page-frames/
class Menu(Tk):
    def __init__(self, *args, **kwargs):
        Tk.__init__(self, *args, **kwargs)
        container = Frame(self)
        container.pack(fill=BOTH,expand=1)
        self.wm_title("Digital Inking with Gesture Recognition")
        self.geometry("800x600")

        container.grid_rowconfigure(0, weight = 1)
        container.grid_columnconfigure(0, weight = 1)

        self.frames = {}
        pages = (MainMenu, SettingPage, HelpPage)
        for F in pages:
            frame = F(container,self)
            frame['bg'] = bgcolour
            self.frames[F] = frame
            frame.grid(row = 0, column = 0, sticky ="nsew")

        self.showFrame(MainMenu)

    def showFrame(self,cont):
        frame = self.frames[cont]
        frame.tkraise()


class MainMenu(Frame):
    def __init__(self, parent, controller):
        Frame.__init__(self,parent)

        title = tkk.Label(self, text="Digital Inking", font=(titleFont,70), background=bgcolour)
        title.place(x=200,y=40)

        inkingButton = Button(self, text="Start Inking", command=self.startInking, background=btncolour, font=(btnFont,20))
        inkingButton.place(x=300, y=210)

        settingsBtn = Button(self,text="Settings",command=lambda: controller.showFrame(SettingPage), background=btncolour, font=(btnFont,20))
        settingsBtn.place(x=325,y=310)

        helpBtn = Button(self,text="Help",command=lambda: controller.showFrame(HelpPage), background=btncolour, font=(btnFont,20))
        helpBtn.place(x=350,y=410)

    def startInking(self):
        global high,low,domHand
        inking = DigitalInking(low,high,domHand)
        inking.ink()

class SettingPage(Frame):
    def __init__(self,parent,controller):
        Frame.__init__(self,parent)
        global domHand

        title = tkk.Label(self, text="Settings", font=("Segoe Print",45), background=bgcolour)
        title.place(x=250,y=30)

        calibrateButton = Button(self, text="Calibrate Pressure",command=self.clickCalibrate, background=btncolour, font=(btnFont,20))
        calibrateButton.place(x=265,y=220)

        self.selected = StringVar()
        self.selected.set(domHand)
        domHandFrm = LabelFrame(self,text="Dominant Hand", font=("Verdana",15), bg=btncolour)
        leftHand = Radiobutton(domHandFrm,text="Left",font=("Verdana",12),bg=btncolour,value="Left",variable=self.selected, command=self.selectDomHand)
        leftHand.grid(column=0, row=0, padx=5, pady=5)
        rightHand = Radiobutton(domHandFrm,text="Right",value="Right",font=("Verdana",12),bg=btncolour,variable=self.selected, command=self.selectDomHand)
        rightHand.grid(column=1, row=0, padx=5, pady=5)
        domHandFrm.place(x=300,y=350)

        backBtn = Button(self, text="Back", command=lambda: controller.showFrame(MainMenu), background=btncolour, font=(btnFont,12))
        backBtn.place(x=50,y=500)
   
    def selectDomHand(self):
        global domHand
        domHand = self.selected.get()
    
    def clickCalibrate(self):
        global high,low,domHand
        cal = Calibrate(dominant=domHand)
        cal.calibrate_pressure()
        low = cal.get_low()
        high = cal.get_high()

class HelpPage(Frame):
    def __init__(self, parent, controller):
        Frame.__init__(self,parent)
        title = tkk.Label(self, text="Help", font=("Segoe Print",45), background=bgcolour)
        title.place(x=300,y=25)

        backBtn = Button(self, text="Back", command=lambda: controller.showFrame(MainMenu), background=btncolour, font=(btnFont,12))
        backBtn.place(x=50,y=500)

        txt = Text(self, width=40, height=10, font=("Calibri",15), bg=bgcolour, bd=0, wrap=WORD)
        txt.place(x=130,y=150)
        txt.insert(INSERT, "How to use:\n\n1. Configure Settings to your preference\n2. Click the Start Inking button\n3. Open a Windows Inking application (e.g: Paint 3D)\
            \n4. To draw, pinch your thumb and index finger and move your hand\n5. To use eraser, pinch your middle finger and thumb")
        txt.configure(state='disabled')

    
app = Menu()   
app.mainloop()