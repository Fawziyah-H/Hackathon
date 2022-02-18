import cv2 
import mediapipe as mp
from desktop_pen import DesktopPenInput
from hand import Hand
from simple_pinch import SimplePinch
from geom_tools import distance_xyz
from win32api import GetSystemMetrics
from win32con import SM_CXVIRTUALSCREEN, SM_CYVIRTUALSCREEN

class DigitalInking():

    def __init__(self, lowest_pressure, highest_pressure, dominant):
        self.cap = cv2.VideoCapture(0,cv2.CAP_DSHOW)
        self.cap.set(3, 640)
        self.cap.set(4, 480)

        self.screen_width = GetSystemMetrics(SM_CXVIRTUALSCREEN)
        self.screen_height = GetSystemMetrics(SM_CYVIRTUALSCREEN)

        self.handdata_raw = {
        "Left": None,
        "Right": None
        }

        self.dominant = dominant

        self.hands = mp.solutions.hands.Hands(
                min_detection_confidence=0.6,
                min_tracking_confidence=0.6,
                max_num_hands=1,
            )

        if self.dominant == "Right":
            self.domHand = Hand(self.handdata_raw['Right'])
        elif self.dominant == "Left":
            self.domHand = Hand(self.handdata_raw['Left'])
        #NOTE might need else statement for invalid domHand value?

        self.counter = 0

        self.pinch = SimplePinch()
        self.mouse = DesktopPenInput()

        self.highest_pressure = highest_pressure
        self.lowest_pressure = lowest_pressure

    def ink(self):
        while self.cap.isOpened():
            success, image = self.cap.read()
            
            # Flip on horizontal
            image = cv2.flip(image, 1)
            camdata = self.hands.process(image)

            handdata_raw = {
            "Left": None,
            "Right": None
            }

            if camdata.multi_handedness:  # If hand(s) present in frame
                for i in range(0, len(camdata.multi_handedness)):  # For each hand

                    # Get raw data from Mediapipe hands
                    handdata_raw[
                        camdata.multi_handedness[i].classification[0].label
                    ] = camdata.multi_hand_landmarks[i]
                
                self.domHand.update(handdata_raw[self.dominant])

                palm_height = distance_xyz(self.domHand.middle_base, self.domHand.wrist)
                
                depth_range = self.highest_pressure - self.lowest_pressure
                increment = depth_range / 1024

                if palm_height <= self.lowest_pressure:
                    new_pressure = 0
                elif palm_height >= self.highest_pressure:
                    new_pressure = 1024
                else:
                    new_pressure = (palm_height - self.lowest_pressure) / increment

                clicked = False
                if self.domHand.index_base.x != 0:
                    self.pinch.run(self.domHand)
                    clicked = self.pinch.clicked

                newX = self.domHand.index_tip.x * self.screen_width
                newY = self.domHand.index_tip.y * self.screen_height

                self.mouse.update_desktop_cursor(newX,newY)
                self.mouse.update_pressure(int(new_pressure))
                self.mouse.update_desktop_click_events(clicked,False,False,False)

            cv2.imshow('Digital Inking', image)
            cv2.waitKey(1)
            if cv2.getWindowProperty("Digital Inking", cv2.WND_PROP_VISIBLE) < 1:
                break

        self.cap.release()
        cv2.destroyAllWindows()