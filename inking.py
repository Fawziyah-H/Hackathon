import cv2 
import mediapipe as mp
from desktop_pen import DesktopPenInput
from hand import Hand
from simple_pinch import SimplePinch
from geom_tools import distance_xyz

class DigitalInking():

    def __init__(self, lowest_pressure, highest_pressure):
        self.cap = cv2.VideoCapture(0,cv2.CAP_DSHOW)
        self.cap.set(3, 640)
        self.cap.set(4, 480)

        self.handdata_raw = {
        "Left": None,
        "Right": None
        }

        self.hands = mp.solutions.hands.Hands(
                min_detection_confidence=0.6,
                min_tracking_confidence=0.6,
                max_num_hands=1,
            )

        self.rightHand = Hand(self.handdata_raw['Right'])
        self.leftHand = Hand(self.handdata_raw['Left'])

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
                
                self.rightHand.update(handdata_raw['Right'])

                palm_height = distance_xyz(self.rightHand.middle_base, self.rightHand.wrist)
                
                depth_range = self.highest_pressure - self.lowest_pressure
                increment = depth_range / 1024

                if palm_height <= self.lowest_pressure:
                    new_pressure = 0
                elif palm_height >= self.highest_pressure:
                    new_pressure = 1024
                else:
                    new_pressure = (palm_height - self.lowest_pressure) / increment

                clicked = False
                if self.rightHand.index_base.x != 0:
                    self.pinch.run(self.rightHand)
                    clicked = self.pinch.clicked

                self.mouse.update_desktop_cursor(self.rightHand.index_tip.x*640, self.rightHand.index_tip.y*480)
                self.mouse.update_pressure(int(new_pressure))
                self.mouse.update_desktop_click_events(clicked,False,False,False)

            text = str(self.lowest_pressure) + ", " + str(self.highest_pressure)
            cv2.putText(image,text,(50,50),cv2.FONT_HERSHEY_SIMPLEX,0.7,(255,0,0),2)

            cv2.imshow('Hand Tracking', image)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        self.cap.release()
        cv2.destroyAllWindows()