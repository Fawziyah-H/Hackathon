from ctypes import *
from ctypes.wintypes import *
import pydirectinput

# Touch for MotionInput designed by Chenuka Ratwatte

#Structs Needed

class POINTER_INFO(Structure):
    _fields_=[("pointerType",c_uint32),
              ("pointerId",c_uint32),
              ("frameId",c_uint32),
              ("pointerFlags",c_int),
              ("sourceDevice",HANDLE),
              ("hwndTarget",HWND),
              ("ptPixelLocation",POINT),
              ("ptHimetricLocation",POINT),
              ("ptPixelLocationRaw",POINT),
              ("ptHimetricLocationRaw",POINT),
              ("dwTime",DWORD),
              ("historyCount",c_uint32),
              ("inputData",c_int32),
              ("dwKeyStates",DWORD),
              ("PerformanceCount",c_uint64),
              ("ButtonChangeType",c_int)
              ]

class POINTER_TOUCH_INFO(Structure):
    _fields_=[("pointerInfo",POINTER_INFO),
              ("touchFlags",c_int),
              ("touchMask",c_int),
              ("rcContact", RECT),
              ("rcContactRaw",RECT),
              ("orientation", c_uint32),
              ("pressure", c_uint32)]


class Touch():
    def __init__(self,FingerRadius=5):
        #Constants

        #For touchMask
        self.TOUCH_MASK_NONE=          0x00000000 #Default
        self.TOUCH_MASK_CONTACTAREA=   0x00000001
        self.TOUCH_MASK_ORIENTATION=   0x00000002
        self.TOUCH_MASK_PRESSURE=      0x00000004
        self.TOUCH_MASK_ALL=           0x00000007

        #For touchFlag
        self.TOUCH_FLAG_NONE=          0x00000000

        #For pointerType
        self.PT_POINTER=               0x00000001#All
        self.PT_TOUCH=                 0x00000002
        self.PT_PEN=                   0x00000003
        self.PT_MOUSE=                 0x00000004

        #For pointerFlags
        self.POINTER_FLAG_NONE=        0x00000000#Default
        self.POINTER_FLAG_NEW=         0x00000001
        self.POINTER_FLAG_INRANGE=     0x00000002
        self.POINTER_FLAG_INCONTACT=   0x00000004
        self.POINTER_FLAG_FIRSTBUTTON= 0x00000010
        self.POINTER_FLAG_SECONDBUTTON=0x00000020
        self.POINTER_FLAG_THIRDBUTTON= 0x00000040
        self.POINTER_FLAG_FOURTHBUTTON=0x00000080
        self.POINTER_FLAG_FIFTHBUTTON= 0x00000100
        self.POINTER_FLAG_PRIMARY=     0x00002000
        self.POINTER_FLAG_CONFIDENCE=  0x00004000
        self.POINTER_FLAG_CANCELED=    0x00008000
        self.POINTER_FLAG_DOWN=        0x00010000
        self.POINTER_FLAG_UPDATE=      0x00020000
        self.POINTER_FLAG_UP=          0x00040000
        self.POINTER_FLAG_WHEEL=       0x00080000
        self.POINTER_FLAG_HWHEEL=      0x00100000
        self.POINTER_FLAG_CAPTURECHANGED=0x00200000

        #Touch feedback constants
        self.TOUCH_FEEDBACK_DEFAULT=   0x00000001
        self.TOUCH_FEEDBACK_INDIRECT=  0x00000002
        self.TOUCH_FEEDBACK_NONE=      0x00000003

        #Set the finger radius
        self.finger_radius = FingerRadius

        #Initialize Pointer and Touch info

        self.num_touches = 0xA  #ideally we want 10 touch points.

        #Initialising the structure for pointerInfo. IDK why but for some reason you need this bit of code
        self.pointerInfo=POINTER_INFO(pointerType=self.PT_TOUCH,
                         pointerId=0,
                         ptPixelLocation=POINT(950,540))

        #Array of fingers to be tracked
        self.contacts = (POINTER_TOUCH_INFO * self.num_touches)()
        self.initialise_contacts()

        #add buffering for each finger
        self.finger_buffer_frames = 3
        self.finger_buffer = [[0 for _ in range(self.finger_buffer_frames)] for _ in range(self.num_touches)]

        #Initialize Touch Injection
        if (windll.user32.InitializeTouchInjection(self.num_touches,self.TOUCH_FEEDBACK_DEFAULT) != 0):
            print("Initialized Touch Injection")

    def initialise_contacts(self):
        for i in range(self.num_touches):
            self.contacts[i]= POINTER_TOUCH_INFO(
                                    pointerInfo= POINTER_INFO(
                                        pointerType=self.PT_TOUCH,
                                        pointerId=0x0 + i,
                                        ptPixelLocation=POINT(950,540) #default value for where the contact will be touched
                                    ),
                                    touchFlags=self.TOUCH_FLAG_NONE,
                                    touchMask=self.TOUCH_MASK_ALL,
                                    rcContact=RECT(
                                        self.pointerInfo.ptPixelLocation.x-self.finger_radius,
                                        self.pointerInfo.ptPixelLocation.y-self.finger_radius,
                                        self.pointerInfo.ptPixelLocation.x+self.finger_radius,
                                        self.pointerInfo.ptPixelLocation.y+self.finger_radius
                                    ),
                                    orientation=90,
                                    pressure=32000) # Dean/Developers please look here regarding calligraphy and pen.

    def singletap(self,coordinates: Array):
        '''Single touch taps depending on the coordinates you send in'''
        x=coordinates[0]
        y=coordinates[1]

        self.contacts[0].pointerInfo.ptPixelLocation.x=x
        self.contacts[0].pointerInfo.ptPixelLocation.y=y

        self.contacts[0].rcContact.left=x-self.finger_radius
        self.contacts[0].rcContact.right=x+self.finger_radius
        self.contacts[0].rcContact.top=y-self.finger_radius
        self.contacts[0].rcContact.bottom=y+self.finger_radius

        self.contacts[0].pointerInfo.pointerFlags=(self.POINTER_FLAG_DOWN|self.POINTER_FLAG_INRANGE|self.POINTER_FLAG_INCONTACT)

        if (windll.user32.InjectTouchInput(1, byref(self.contacts[0]))==0):
            print(" Failed with Error: "+ FormatError())

        #Pull Up
        self.contacts[0].pointerInfo.pointerFlags=self.POINTER_FLAG_UP
        if (windll.user32.InjectTouchInput(c_uint32(1),byref(self.contacts[0]))==0):
            print("Failed with Error: "+FormatError())
        else:
            print("Tap Succeeded!")

        self.mousejiggle(coordinates)
    
    def touchdown(self,coordinates:Array):
        '''Initialises a touch down event depending on the fingers in contact'''
        fingers = (POINTER_TOUCH_INFO * len(coordinates))()
        
        for i,coordinate in enumerate(coordinates):
            self.finger_buffer[i].pop(0)
            self.finger_buffer[i].append(1)
            x=coordinate[0]
            y=coordinate[1]

            self.contacts[i].pointerInfo.ptPixelLocation.x=x
            self.contacts[i].pointerInfo.ptPixelLocation.y=y

            self.contacts[i].rcContact.left=x-self.finger_radius
            self.contacts[i].rcContact.right=x+self.finger_radius
            self.contacts[i].rcContact.top=y-self.finger_radius
            self.contacts[i].rcContact.bottom=y+self.finger_radius

            if sum(self.finger_buffer[i]) > 1:
                self.contacts[i].pointerInfo.pointerFlags=(self.POINTER_FLAG_UPDATE|self.POINTER_FLAG_INRANGE|self.POINTER_FLAG_INCONTACT)
            else:
                self.contacts[i].pointerInfo.pointerFlags=(self.POINTER_FLAG_DOWN|self.POINTER_FLAG_INRANGE|self.POINTER_FLAG_INCONTACT)
                print("finger " +str(i)+ " touchdown")

            fingers[i] = self.contacts[i]
        
        #reset flags on unsed touch points
        for i in range(len(fingers),self.num_touches):
            if self.contacts[i].pointerInfo.pointerFlags!=self.POINTER_FLAG_UP:
                self.contacts[i].pointerInfo.pointerFlags=self.POINTER_FLAG_UP
                self.finger_buffer[i].pop(0)
                self.finger_buffer[i].append(0)
                print("released finger " + str(i))

        if(windll.user32.InjectTouchInput(c_uint32(len(fingers)), byref(fingers))==0):
            print("Failed with Error: " + FormatError())
            self.touchup(coordinates[0])


    def touchup(self,coordinates: Array):
        for i in range(self.num_touches):
            if self.contacts[i].pointerInfo.pointerFlags != self.POINTER_FLAG_UP:
                self.contacts[i].pointerInfo.pointerFlags=self.POINTER_FLAG_UP
        print("released all touch")
        self.finger_buffer = [[0 for _ in range(self.finger_buffer_frames)] for _ in range(self.num_touches)]

        #lift up any downed fingers
        windll.user32.InjectTouchInput(self.num_touches, byref(self.contacts))

        self.mousejiggle(coordinates)

    def mousejiggle(self,coordinates:Array):
        '''The mouse cursor dissapears after touch is made, this is annoying so we shall move the mouse a little to reactivate it'''
        pydirectinput.moveTo(coordinates[0],y=coordinates[1])

