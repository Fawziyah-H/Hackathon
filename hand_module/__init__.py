# initial setup by Ashild Kummen, modified by Chenuka Ratwatte , Ali Hassan
from .helpers.draw import Draw
from .gestures.gesture import Gesture
from .hand import Hand
from .gestures.scroll import Scroll
import datetime
from .tools.framecounter import framecounter
import mediapipe as mp
from .tools.area_of_interest import AreaOfInterest
import logging
import sys
import cv2
from data.usage_data_hands import usageData
from win32gui import GetWindowText, GetForegroundWindow



class HandSetup:
    def __init__(
            self,
            nHands,
            handedness,
            joystickToggleMode,
            joystickActivationFrames,
            joystickUp,
            joystickDown,
            joystickLeft,
            joystickRight,
            edgePan,
            cursorControl=True,
            sensitivity=0.14,
            smoothing=4,
            scroll_speed=1,
            screen_config={"arrangement": "SingleScreen"},
            usecase="classic",
            showHandTracking=False,
            activateArrowKey=False,
            dragWithIndex=False,
            joystickMode="wrist",
            joystickInput="wasd",
            FingerRadius=5,
            UpArrowConfig="Key Press",
            DownArrowConfig="Key Press",
            LeftArrowConfig="Key Press",
            RightnArrowConfig="Key Press",
            MouseSensitivity=1.0,
    ):
        # initialise mouse based on use case
        self.frame_counter = framecounter()
        if cursorControl and usecase == "classic":

            from .events.desktop_mouse_classic import DesktopMouseClassic

            self.mouse = DesktopMouseClassic(
                dragWithIndex=dragWithIndex,
                cursorControl=cursorControl,
                mouse_smoothing=smoothing)

        # For the Puzzle Setting
        elif usecase == "puzzle":
            from .events.desktop_mouse_puzzle import DesktopMousePuzzle
            from .gestures.arrow_keys import ArrowController
            from .events.Desktop_keyboard import Button, Display
            from .tools.speech_to_text import speechToText
            self.mouse = DesktopMousePuzzle(
                dragWithIndex=dragWithIndex,
                cursorControl=cursorControl,
                mouse_smoothing=smoothing,
                activateArrowKey=activateArrowKey,
            )

        elif usecase == "actiongames":
            from .gestures.wrist_angle import WristAngle
            from .gestures.palmtap import PalmTap
            from events.gaming_mouse import GamingMouse
            from events.gaming_joystick import GamingJoystick
            from .gestures.primitives.pinch import Pinch
        elif usecase == "nav3d":
            from .events.desktop_mouse_touch import DesktopMouseTouch
            from .tools.zoom import Zoom
            from .tools.joystick import Joystick
            from .tools.speech_to_text import speechToText
            self.mouse = DesktopMouseTouch(FingerRadius=FingerRadius,MouseSensitivity=MouseSensitivity)
        else:
            from .events.desktop_mouse import DesktopMouse
            self.mouse = DesktopMouse()

        self.cursorControl = cursorControl
        self.scroll_speed = scroll_speed

        self.nHands = nHands
        self.screen_config = screen_config
        self.showHandTracking = showHandTracking in ["True", "true"]

        print(datetime.datetime.now(), "- Dominant hand is " + handedness)
        # Creating hand tracker
        self.domHand = Hand(handedness, "domhand", pinch_sensitivity=sensitivity)
        self.offHand = None
        if self.nHands == 2:
            offHand_leftorright = "Left" if handedness == "Right" else "Right"
            self.offHand = Hand(
                offHand_leftorright, "offhand", pinch_sensitivity=sensitivity
            )

        self.usecase = usecase
        self.activateArrowKey = activateArrowKey
        # creating mouse cursor
        self.gestures = Gesture(self.domHand, self.offHand, usecase=self.usecase)

        # For the 3d navigation usecase instantiate all the tools
        if self.usecase == 'nav3d':
            self.zoom = Zoom(self.gestures)
            self.joystick = Joystick(self.gestures, joystickToggleMode, joystickActivationFrames, joystickUp,joystickDown, joystickLeft, joystickRight)
            self.speech_to_text = speechToText(self.gestures)

        if self.usecase == "actiongames":
            self.edgePan = edgePan
            self.joystickMode = joystickMode
            self.joystickInput = joystickInput
            print("Joystick mode:", self.joystickMode, "Input mode: ", self.joystickInput, "Edge panning: ",
            self.edgePan)
            self.pinch = Pinch()  # init pinch tracking
            self.offpinch = Pinch()
            if joystickInput == "analogue":
                self.wrist_angle = WristAngle(x_range=0.5, y_range=0.7)
            else:
                self.wrist_angle = WristAngle()
            self.palm_tap = PalmTap()
            self.mouse = GamingMouse()
            self.joystick = GamingJoystick(joystickInput=joystickInput)
        else:
            # disabled in gaming mode
            self.scroll = Scroll()


        if self.usecase == "puzzle":
            self.ArrowController = ArrowController()
            self.handedness = handedness
            self.UpArrowConfig = UpArrowConfig
            self.DownArrowConfig = DownArrowConfig
            self.LeftArrowConfig = LeftArrowConfig
            self.RightnArrowConfig = RightnArrowConfig
            self.Display = Display()
            self.keys = [["Q", "W", "E", "R", "T", "Y", "U", "I", "O"],
                         ["A", "S", "D", "F", "G", "H", "J", "K", "L"],
                         ["Z", "X", "C", "V", "B", "N", "M", "P"],
                         [",", ".", " ", "<"]]
            self.buttonList = []
            self.speech_to_text = speechToText(self.gestures)
            if handedness == "Left":
                for i in range(len(self.keys)):
                    for j, key in enumerate(self.keys[i]):
                        self.buttonList.append(Button([60 * j + 90, 70 * i + 50], key))

            if handedness == "Right":
                for i in range(len(self.keys)):
                    for j, key in enumerate(self.keys[i]):
                        self.buttonList.append(Button([60 * j + 25, 70 * i + 50], key))


        # For the 3d navigation usecase instantiate all the tools
        if self.usecase == "nav3d":
            from .tools.zoom import Zoom
            from .tools.joystick import Joystick
            from .tools.speech_to_text import speechToText

            self.zoom = Zoom(self.gestures)
            self.joystick = Joystick(self.gestures, joystickToggleMode, joystickActivationFrames, joystickUp,
                                     joystickDown, joystickLeft, joystickRight)
            self.speech_to_text = speechToText(self.gestures)

        # getting mediapipe tools
        self.hands = mp.solutions.hands.Hands(
            min_detection_confidence=0.6,
            min_tracking_confidence=0.6,
            max_num_hands=self.nHands,
        )

        self.initialised = False  # changes to true once initialise() has been run

        self.isScrolling = False

    def initialise(self, cap):
        """Initialisations that need camera to have already started."""
        # getting area of interest
        if self.cursorControl:
            self.aoi = AreaOfInterest(cap, self.screen_config)
        else:
            self.aoi = None
        # Creating instance of drawer class (helper) for writing/drawing on camera

        self.initialised = True

        self.draw = Draw(cap)
        print("Initialised.")

    def processFrame(self, cap, image):
        """processes data from a single frame to be drawn onto the screen."""
        # Initialising area of interest if not already initialised
        self.frame_counter.update()

        if not self.initialised:
            self.initialise(cap)

        # Processing video with mediapipe hands:
        # Flip the image horizontally for a later selfie-view display, and convert the BGR image to RGB.
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        image.flags.writeable = False
        camdata = self.hands.process(image)

        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)





        # initialising dictionary for raw mediapipe data
        handdata_raw = {
            "Left": None,
            "Right": None,
        }

        if camdata.multi_handedness:  # If hand(s) present in frame
            for i in range(0, len(camdata.multi_handedness)):  # For each hand

                # Get raw data from Mediapipe hands
                handdata_raw[
                    camdata.multi_handedness[i].classification[0].label
                ] = camdata.multi_hand_landmarks[i]

                # draw hand interestpoints on screen
                if self.showHandTracking:
                    self.draw.draw_hand_connections(
                        camdata.multi_hand_landmarks[i],
                        image,
                        camdata.multi_handedness[i].classification[0].label,
                        self.domHand,
                        self.offHand,
                    )


        # Updating Hand object(s) by feeding in raw data.
        self.domHand.update(handdata_raw[self.domHand.leftorright])
        if self.nHands == 2:
            self.offHand.update(handdata_raw[self.offHand.leftorright])


        if self.usecase == "puzzle":
            pass
        else:
            if self.cursorControl:
                # update area of interest
                Top_Aoi, Buttom_Aoi = self.draw.draw_area_of_interest(image, self.aoi)  # drawing area of interest
            if (self.cursorControl == True) & (self.domHand.is_idle() == False):
                dist_to_screen = self.aoi.update(self.domHand)
                self.draw.draw_distance(image, dist_to_screen)

                # drawing idle state on screen
                self.draw.draw_idle_states(image, self.domHand, self.offHand)

        # Updating Gestures
        self.gestures.run_gestures()

        # If the user wishes to use 3d navigation run the relevant tools
        if self.usecase == "nav3d":
            # run Zoom tool
            if (self.nHands == 2 and self.offHand.is_idle() == False):
                self.zoom.run_zoom(self.domHand, self.offHand)

            # run Joystick tool
            if not self.zoom.is_in_zoom_mode:
                self.joystick.run_joystick(self.offHand)
                self.draw.draw_joystick(image, self.joystick)

            # run speech recognition
            self.speech_to_text.run_speech_recognition()
            self.draw.draw_mic_status(image, self.speech_to_text)

        # setting variables to false first:
        is_left_clicked, is_right_clicked, is_double_clicked = False, False, False
        event_str = ""




        # Other code for processing data can go here:
        if (self.domHand.is_idle() == False or self.isScrolling):

            if self.usecase=="puzzle":
                pass
            else:
                # dominant hand is active:
                # clicking activities
                is_left_clicked = self.gestures.get_gesture("index_pinch", "domhand").is_active
                is_right_clicked = self.gestures.get_gesture("middle_pinch", "domhand").is_active
                is_double_clicked = self.gestures.get_gesture("double_pinch", "domhand").is_active
        # Gaming off hand controls
        if self.usecase == "actiongames":
            if handdata_raw[self.offHand.leftorright] != None:
                self.offpinch.run(self.offHand)
                self.wrist_angle.update_angle(self.offHand, self.offpinch.is_pinched_index)
                # print(self.joystickMode)
                if self.joystickMode == "wrist":
                    x_axis = self.wrist_angle.x
                    y_axis = self.wrist_angle.z
                else:
                    x_axis = self.offHand.pinky_base.x
                    y_axis = self.offHand.pinky_base.y

                self.joystick.update(gesture=self.offpinch.is_pinched_index, x_axis=x_axis,
                                     y_axis=y_axis, joystickMode=self.joystickMode)
                # draw joystick on screen
                cv2.circle(image, (int(100 + (80 * x_axis)), int(400 + (80 * y_axis))), 10,
                           (0, 0, 255), -1)
                cv2.circle(image, (100, 400), 80, (0, 0, 255), 3)

            else:
                self.joystick.clear()
                if self.joystickInput == "analogue":
                    self.joystick.gamepad_zero()

        if (self.domHand.is_idle() == False or self.isScrolling): # dominant hand is active:

            # check for scroll
            if self.usecase == "actiongames":  # robs use case name goes here
                self.pinch.run(self.domHand)
                self.palm_tap.update_tap(self.domHand)
                domx, domy = self.aoi.basic_convert(self.domHand.pinky_base.x, self.domHand.pinky_base.y)
                self.mouse.update_gaming_mouse(x=domx,
                                               y=domy,
                                               is_left_clicked=self.pinch.is_pinched_index,
                                               is_right_clicked=self.palm_tap.is_tapped_middle,
                                               edge_pan=self.edgePan,
                                               absx=self.domHand.pinky_base.x,
                                               absy=self.domHand.pinky_base.y
                                               )

            else:
                # clicking activities
                is_left_clicked = self.gestures.get_gesture("index_pinch", "domhand").is_active
                is_right_clicked = self.gestures.get_gesture("middle_pinch", "domhand").is_active
                is_double_clicked = self.gestures.get_gesture("double_pinch", "domhand").is_active

            # check for scroll
            if self.usecase != "actiongames":  # robs use case name goes here
                self.isScrolling = self.scroll.detect_scroll(self.domHand)
            if self.usecase == "classic" and self.cursorControl:
                event_str = self.mouse.processMovement(
                    image=image,
                    domhand=self.domHand,
                    aoi=self.aoi,
                    draw=self.draw,
                    is_left_clicked=is_left_clicked,
                    is_right_clicked=is_right_clicked,
                    is_double_clicked=is_double_clicked,
                    isScrolling=self.isScrolling,
                    scroll_speed=self.scroll_speed,
                    scroll_direction=self.scroll.direction,
                )
            # For the Puzzle Setting, looks at if arrow keys was enabled
            elif self.usecase == "puzzle" and self.cursorControl:

                if self.activateArrowKey in ["True","true"]:




                    is_Active = self.gestures.get_gesture("offHand_fist", "offhand").is_active
                    mode=self.gestures.Mode(is_Active)

                else:

                    mode="Cursor"

                if mode=="Keyboard":
                    keyactivate = self.gestures.get_gesture("ring_pinch", "domhand").is_active
                    self.Display.Button_display(image,self.buttonList)
                    self.Display.Button_selection(image, self.buttonList,self.domHand,keyactivate,
                                                  self.aoi.cam_width,self.aoi.cam_height )
                    self.ArrowController.OnscrenStatus(mode, image)
                if mode=="ArrowKey":

                    Down, Up, Right, Left = self.gestures.get_gesture_arrow(self.domHand,
                                                    self.handedness,
                                                    self.RightnArrowConfig)
                    self.ArrowController.ArrowKeyInput(Down, Up, Right, Left,self.UpArrowConfig,self.DownArrowConfig,
                                                                     self.LeftArrowConfig,
                                                                   self.RightnArrowConfig)
                    self.ArrowController.OnscrenStatus(mode, image)

                if mode == "Cursor":

                    # dominant hand is active:
                    # clicking activities
                    is_left_clicked = self.gestures.get_gesture("index_pinch", "domhand").is_active
                    is_right_clicked = self.gestures.get_gesture("middle_pinch", "domhand").is_active
                    is_double_clicked = self.gestures.get_gesture("double_pinch", "domhand").is_active
                    # update area of interest
                    if (self.cursorControl == True) & (self.domHand.is_idle() == False):
                        Top_Aoi, Buttom_Aoi = self.draw.draw_area_of_interest(image,
                                                                              self.aoi)  # drawing area of interest

                    # run speech recognition
                    self.speech_to_text.run_speech_recognition()
                    self.draw.draw_mic_status(image, self.speech_to_text)

                    dist_to_screen = self.aoi.update(self.domHand)
                    self.draw.draw_distance(image, dist_to_screen)

                    # drawing idle state on screen
                    self.draw.draw_idle_states(image, self.domHand, self.offHand)


                    # check if the hand is inside the AOI
                    if (self.domHand.palm_center.x * self.aoi.cam_width + 10 > Top_Aoi[0]
                            and self.domHand.palm_center.x * self.aoi.cam_width - 10 < Buttom_Aoi[0]
                            and self.domHand.palm_center.y * self.aoi.cam_height + 10 > Top_Aoi[1]
                            and self.domHand.palm_center.y * self.aoi.cam_height - 10 < Buttom_Aoi[1]
                    ):
                        event_str = self.mouse.processMovement(
                            image=image,
                            domhand=self.domHand,
                            aoi=self.aoi,
                            draw=self.draw,
                            is_left_clicked=is_left_clicked,
                            is_right_clicked=is_right_clicked,
                            is_double_clicked=is_double_clicked,
                            isScrolling=self.isScrolling,
                            scroll_speed=self.scroll_speed,
                            scroll_direction=self.scroll.direction,
                        )
        
        if self.usecase =='nav3d':
            if (self.isScrolling and self.mouse.drag == False):  # prevent simultaneous drag and scroll
                self.mouse.scroll_events(speed=self.scroll_speed, direction=self.scroll.direction)
            else:
                #get cursor positions
                x_dom, y_dom = self.aoi.convert_xy(self.domHand.pinky_base.x, self.domHand.pinky_base.y)
                is_cursor_active = not self.domHand.is_idle()
                self.mouse.update_desktop_cursor(x_dom, y_dom, is_cursor_active)
                is_offhand_clicked = self.gestures.get_gesture("index_pinch", "offhand").is_active
                if self.offHand.is_idle() == False and self.nHands == 2:
                    x_off, y_off = self.aoi.convert_xy(self.offHand.pinky_base.x, self.offHand.pinky_base.y)
                    self.mouse.update_offhand_position(x_off,y_off,is_offhand_clicked)
                
                #update clicking variables
                if is_cursor_active:
                    is_left_clicked = self.gestures.get_gesture("index_pinch", "domhand").is_active
                    is_right_clicked = self.gestures.get_gesture("middle_pinch", "domhand").is_active
                    is_double_clicked = self.gestures.get_gesture("ring_pinch", "domhand").is_active
                    is_panning =self.gestures.get_gesture("dbgun", "domhand").is_active
                    self.mouse.update_desktop_click_events(is_left_clicked, is_right_clicked, is_double_clicked,is_offhand_clicked, is_panning)



        # Log frame-by-frame usage data
        if self.usecase == "classic" and self.cursorControl:
            usageData.addTimeData(
                x=round(self.mouse.cursor_xy[0], 2),
                y=round(self.mouse.cursor_xy[1], 2),
                distanceToCam=round(self.aoi.distanceToCam, 2),
                window=GetWindowText(GetForegroundWindow()),
                left_click=(event_str == "left"),
                right_click=(event_str == "right"),
                double_click=(event_str == "double"),
                drag=self.mouse.Drag,
                scroll=self.isScrolling,
                scrollDirection=(self.scroll.direction if self.isScrolling else "none"),
            )
        
        if self.usecase == "classic" and not self.cursorControl:
            # eye tracking with hand gesture need; cursorControl == False
            self.mouse.update_desktop_click_events(is_left_clicked, is_right_clicked, is_double_clicked)
            self.draw.debug_variable(
                image,
                "Click status",
                (is_left_clicked or is_right_clicked),
            )


        if self.usecase == "puzzle" and self.cursorControl:
            usageData.addTimeData(
                x=round(self.mouse.cursor_xy[0], 2),
                y=round(self.mouse.cursor_xy[1], 2),
                distanceToCam=round(self.aoi.distanceToCam, 2),
                window=GetWindowText(GetForegroundWindow()),
                left_click=(event_str == "left"),
                right_click=(event_str == "right"),
                double_click=(event_str == "double"),
                drag=self.mouse.Drag,
                scroll=self.isScrolling,
                scrollDirection=(self.scroll.direction if self.isScrolling else "none"),
            )

        return image
