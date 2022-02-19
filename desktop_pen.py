#Based off Chenuka Ratwatte's and Ali Hassan's work, modified for digital inking and pen input.

from win32api import GetSystemMetrics, error  # pip install pywin32
from pen_input import Pen
import pyautogui
from pynput.mouse import Button, Controller
import ctypes


class DesktopPenInput:
    def __init__(self, mouse_smoothing=6,FingerRadius=5,MouseSensitivity=1.0,Pressure=0,Erase=False):
        self.last_is_left_clicked = False
        self.last_is_right_clicked = False
        self.last_is_double_clicked = False
        self.last_is_offhand_clicked = False
        self.left_click_counter = 0
        self.drag = False
        self.finger_radius = FingerRadius
        self.penInput = Pen()
        self.smoothing = mouse_smoothing
        self.active_window_dimensions = None
        self.mouse_sensitivity = MouseSensitivity   # must be between a value of 0.7 and 1.6
        self.pressure = Pressure
        self.erase = Erase

        # cursor movement

        self.cursor_active = False                  # cursor active in this frame
        self.prev_cursor_active = False             # cursor active in the previous frame
        
        # finding the center of the screen
        user32 = ctypes.windll.user32
        screensize = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)
        center_x = int(screensize[0]/2)
        center_y = int(screensize[1]/2)
        
        self.origin = [center_x,center_y]           # the point the mouse was last before cursor became inactive
        self.reactivated_hand_position = [0, 0]     # the point in frame where the hand reactivates the cursor after it has been deactivated
        self.cursor_raw = [0, 0]                    # Used to find the relative position of the offhand for multi-touch on another screen
        
        self.offhand_xy = [0, 0]                    # useful for when the offhand pinch emulates the second touch point
        self.offhand_buffer_x = []
        self.offhand_buffer_y = []
        self.offhand_ref_point = [0, 0]             # Point which measured pixel movement for the offhand is relative to
        self.window_ref_point = [0, 0]              # Point at which the second touch will be made relative to


        self.cursor_buffer_x = []
        self.cursor_buffer_y = []

        self.cursor = Controller()

        self.prev = []                              # the previous cursor position

        pyautogui.FAILSAFE = False

    def update_cursor_xy(self, x, y,cursor_is_active):
        """TAKES X,Y INPUTS AND CONVERTS TO DESKTOP CURSOR MOVEMENTS"""
        self.cursor_active = cursor_is_active
        if self.prev_cursor_active is False and self.cursor_active is True:
            #Upon cursor reactivation save the new positon and clear buffers
            #On mouse move a vector relative to the new position will be added to the last known mouse position
            self.reactivated_hand_position = (x,y)
            self.cursor_buffer_x = []
            self.cursor_buffer_y = []
            print("reactivated cursor")
        elif self.prev_cursor_active is True and self.cursor_active is False:
            #save the mouse's last position before cursor deactivated
            print("deactivated cursor")
            self.origin = self.cursor.position

        if self.cursor_active:
            #value needs to be saved for calculating the offhand position
            self.cursor_raw = [x,y]
            
            # new coordinates are last known position of mouse + a vector (i.e: relative movement from the reactivated hand position)
            x_new = self.origin[0] + (x-self.reactivated_hand_position[0])*self.mouse_sensitivity
            y_new = self.origin[1] + (y-self.reactivated_hand_position[1])*self.mouse_sensitivity

            self.prev = [x_new,y_new]
            
            # prevent buffer from growing too large
            if len(self.cursor_buffer_x) >= self.smoothing + 1:
                self.cursor_buffer_x.pop(0)
                self.cursor_buffer_y.pop(0)
            self.cursor_buffer_x.append(x_new)
            self.cursor_buffer_y.append(y_new)
            self.cursor.position = (
                int(sum(self.cursor_buffer_x) / len(self.cursor_buffer_x)),
                int(sum(self.cursor_buffer_y) / len(self.cursor_buffer_y)),
            )
        self.prev_cursor_active = self.cursor_active


    def click_events(self, is_left_clicked, is_right_clicked, is_double_clicked, is_panning, is_erase):
        self.erase = is_erase

        '''This will continue a drag or ink stroke with updated coordinates and pressure'''
        if self.drag is True:
            self.penInput.update_pen_info(self.cursor.position, self.pressure)

        '''Panning using multitouch - works beautifully!'''
        if is_panning:
            second_touch = (self.cursor.position[0] + 2*self.finger_radius,self.cursor.position[1])
            self.penInput.pendown([self.cursor.position,second_touch], self.erase)

        """This will determine by frame  if the left-click will be a drag or a click"""
        if is_left_clicked is True:
            self.left_click_counter += 1

        """This will enable double click, only possible if last_is_double_clicked= True and the is_double_clicked= False """
        if self.last_is_double_clicked is False and is_double_clicked is True and is_left_clicked is False and self.last_is_left_clicked is False:
            print("double click")
            self.cursor.click(Button.left, 2)
            self.left_click_counter = 0

        """This will enable left click upon release of the pinch. Based on how long the pinch was , it will either be a left click or a release from  a drag """
        if (is_left_clicked is False and is_double_clicked is False and self.last_is_double_clicked is False and self.last_is_left_clicked is True):
            if self.left_click_counter <= 7:
                self.penInput.pentap(self.cursor.position,self.pressure,self.erase)
                self.left_click_counter = 0
            if self.left_click_counter > 6:
                self.penInput.penup(self.cursor.position)
                self.left_click_counter = 0
            self.drag = False

        """This will enable Right  click and only possible if is_double_clicked= False and the is_double_clicked= False"""
        if self.last_is_right_clicked != is_right_clicked:
            if (is_right_clicked is True and is_double_clicked is False and self.last_is_double_clicked is False):
                self.cursor.click(Button.right, 1)
                self.Click_event_lock = True
                print("Right Click")
                self.left_click_counter = 0

        """This will initialise Drag event when pinch length is more than 6 frames and self.drag is currently False"""
        if is_left_clicked is True and is_right_clicked is False and self.drag is False and self.left_click_counter > 6:
            self.penInput.pendown(self.cursor.position, self.pressure, self.erase)
            self.drag = True

        self.last_is_double_clicked = is_double_clicked
        self.last_is_left_clicked = is_left_clicked
        self.last_is_right_clicked = is_right_clicked

    def update_desktop_click_events(self, is_left_clicked, is_right_clicked, is_double_clicked, is_panning, is_erase):
        self.click_events(is_left_clicked, is_right_clicked, is_double_clicked, is_panning, is_erase)

    def update_desktop_cursor(self, x, y,cursor_is_active:bool=True):
        self.update_cursor_xy(x, y,cursor_is_active)
        self.penInput.get_previous_coordinates([int(i) for i in self.prev])

    def update_pressure(self, pressure):
        self.pressure = pressure

