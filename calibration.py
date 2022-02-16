import cv2 
import mediapipe as mp
from hand import Hand
from Scissor import Scissor
from geom_tools import distance_xyz

class Calibrate():

    def __init__(self):
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

        self.lowest_pressure = 0
        self.highest_pressure = 0
        self.counter = 0

        self.scissor = Scissor()

    def calibrate_pressure(self):
        while self.cap.isOpened():
            success, image = self.cap.read()
            
            # Flip on horizontal
            image = cv2.flip(image, 1)
            camdata = self.hands.process(image)

            #cal = Calibrate(image)
            #cal.calibrate_pressure()

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

                if self.lowest_pressure == 0 or self.highest_pressure == 0:
                    calibrate = False
                    if self.rightHand.index_base.x != 0:
                        self.scissor.run(self.rightHand)
                        calibrate = self.scissor.clicked
                    
                    if calibrate:
                        self.counter += 1
                    
                    if self.counter == 1:
                        self.lowest_pressure = palm_height

                    if self.counter == 10:
                        self.highest_pressure = palm_height

            title_text = "Calibrating Pressure"
            cv2.putText(image,title_text,(50,50),cv2.FONT_HERSHEY_SIMPLEX,1,(255,0,0),3)

            text = str(self.lowest_pressure) + ", " + str(self.highest_pressure)
            cv2.putText(image,text,(50,80),cv2.FONT_HERSHEY_SIMPLEX,0.8,(255,0,0),2)
            
            cv2.imshow('Hand Tracking', image)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        self.cap.release()
        cv2.destroyAllWindows()

    def get_low(self):
        return self.lowest_pressure

    def get_high(self):
        return self.highest_pressure
