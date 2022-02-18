import cv2 
import mediapipe as mp
from hand import Hand
from simple_pinch import SimplePinch
from geom_tools import distance_xyz

class Calibrate():

    def __init__(self, dominant):
        self.cap = cv2.VideoCapture(0,cv2.CAP_DSHOW)
        self.cap.set(3, 640)
        self.cap.set(4, 480)

        self.dominant = dominant

        self.handdata_raw = {
        "Left": None,
        "Right": None
        }

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


        self.lowest_pressure = 0
        self.highest_pressure = 0
        self.counter = 0
        self.calibrated = False

        self.pinch = SimplePinch()

    def display_instruction(self, image):
        overlay = image.copy()
        cv2.rectangle(overlay,(45,20),(480,60),(255,255,255),cv2.FILLED)
        alpha = 0.5
        cv2.addWeighted(overlay, alpha, image, 1 - alpha, 0, image)
        msg = "Raise dominant hand to calibrate pressure"
        cv2.putText(image,msg,(50,50),cv2.FONT_HERSHEY_SIMPLEX,0.6,(0,0,0),2)

    def calibrate(self,image, palm_height):
        overlay = image.copy()
        cv2.rectangle(overlay,(45,20),(500,90),(255,255,255),cv2.FILLED)
        alpha = 0.6
        cv2.addWeighted(overlay, alpha, image, 1 - alpha, 0, image)
        msg1 = "do one pinch at 0 depth, then one pinch at max depth"
        cv2.putText(image,msg1,(50,50),cv2.FONT_HERSHEY_SIMPLEX,0.5,(0,0,255),2)

        calibrate = False
        if self.domHand.index_base.x != 0:
            self.pinch.run(self.domHand)
            calibrate = self.pinch.clicked
        
        if calibrate:
            self.counter += 1
        
            if self.counter == 2:
                if self.lowest_pressure == 0:
                    self.lowest_pressure = palm_height

                else:
                    self.highest_pressure = palm_height

        else:
            self.counter = 0

        if self.lowest_pressure == 0 or self.highest_pressure == 0:
            self.calibrated = False 
        else:
            self.calibrated = True

        msg2 = "min: " + str(round(self.lowest_pressure,5)) + "      max: " + str(round(self.highest_pressure,5))
        cv2.putText(image,msg2,(50,80),cv2.FONT_HERSHEY_SIMPLEX,0.5,(0,0,255),2)



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

            if not camdata.multi_handedness and self.highest_pressure == 0:
                self.display_instruction(image)

            if camdata.multi_handedness:  # If hand(s) present in frame
                for i in range(0, len(camdata.multi_handedness)):  # For each hand

                    # Get raw data from Mediapipe hands
                    handdata_raw[
                        camdata.multi_handedness[i].classification[0].label
                    ] = camdata.multi_hand_landmarks[i]
                
                self.domHand.update(handdata_raw[self.dominant])

                palm_height = distance_xyz(self.domHand.middle_base, self.domHand.wrist)

                if not self.calibrated:
                    self.calibrate(image, palm_height)
                else:
                    msg = "Depth calibration done"
                    cv2.putText(image,msg,(50,50),cv2.FONT_HERSHEY_SIMPLEX,0.6,(0,127,0),2)
            
            cv2.imshow('Digital Inking - Calibration', image)
            cv2.waitKey(1)
            if cv2.getWindowProperty("Digital Inking - Calibration", cv2.WND_PROP_VISIBLE) < 1:
                break

        self.cap.release()
        cv2.destroyAllWindows()

    def get_low(self):
        return self.lowest_pressure

    def get_high(self):
        return self.highest_pressure
