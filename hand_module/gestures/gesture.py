from .rabbit import Rabbit
from .gun import Gun
from .index_pinch import IndexPinch
from .middle_pinch import MiddlePinch
from .ring_pinch import RingPinch
from .double_pinch import DoublePinch
from ..hand import Hand
from .offHand_fist import Fist
import math

#Gesture Class Designed by Chenuka Ratwatte

class Gesture:
    def __init__(self, domhand: Hand, offhand: Hand, usecase="classic"):

        self.domhand_gestures = {}
        self.offhand_gestures = {}

        # Dominant Hand gestures
        self.domhand_gestures["index_pinch"] = IndexPinch(domhand.pinch)
        self.domhand_gestures["middle_pinch"] = MiddlePinch(domhand.pinch)
        self.domhand_gestures["double_pinch"] = DoublePinch(domhand.pinch)

        if usecase == "classic":
            pass
        elif usecase == "nav3d":
            self.domhand_gestures["rabbit"] = Rabbit(domhand.pinch)
            self.domhand_gestures["ring_pinch"] = RingPinch(domhand.pinch)
            self.domhand_gestures["dbgun"] = Gun(domhand.folded, "double")

            # Off Hand gestures

            self.offhand_gestures["rabbit"] = Rabbit(offhand.pinch)
            self.offhand_gestures["dbgun"] = Gun(offhand.folded, "double")
            self.offhand_gestures["index_pinch"] = IndexPinch(offhand.pinch)
        # Combo gestures, maybe you will have more complicated ones that you can place below


        elif usecase == "puzzle":
            self.is_active_previous = False
            self.Modes = {0: "Cursor", 1: "ArrowKey", 2: "Keyboard"}
            self.is_active_counter = 0
            self.offhand_gestures["dbgun"] = Gun(offhand.folded, "double")
            self.domhand_gestures["ring_pinch"] = RingPinch(domhand.pinch)

             # Off Hand gestures
            self.offhand_gestures["offHand_fist"] = Fist(offhand.folded)


    def run_gestures(self):
        # Update domhand gestures
        for gesture in self.domhand_gestures.values():
            gesture.run()

        # Update offhand gestures
        for gesture in self.offhand_gestures.values():
            gesture.run()

    def get_gesture(self, gesture_name: str, hand_name: str):
        if hand_name == "domhand":
            return self.domhand_gestures[gesture_name]
        elif hand_name == "offhand":
            return self.offhand_gestures[gesture_name]


    def get_gesture_arrow(self,domhand: Hand ,handedness,RightnArrowConfig):

        x2=(domhand.middle_tip.x +domhand.ring_tip.x)/2
        y2=(domhand.middle_tip.y +domhand.ring_tip.y)/2
        x1=domhand.wrist.x
        y1=domhand.wrist.y

        angle= 90 - math.atan((y2-y1)/(x2-x1))*180/math.pi



        DownArrow = True if (domhand.middle_tip.y > domhand.thumb_base.y
                             and domhand.ring_tip.y > domhand.thumb_base.y ) else  False

        if RightnArrowConfig == "Key Down":
            UpArrow = True if ((((domhand.middle_tip.z + domhand.ring_tip.z)/2) > 0)
                               and (angle<15  or angle >175) ) else False
        if RightnArrowConfig == "Key Press":
            UpArrow = True if ((((domhand.middle_tip.z + domhand.ring_tip.z)/2) > 0)
                               and (angle<20  or angle >170) ) else False





        if handedness =="Right":
            RightArrow = True if (domhand.index_base.x>domhand.wrist.x) else False
            LeftArrow= True if (domhand.pinky_upperj.x<domhand.wrist.x) else False

            if LeftArrow is True or RightArrow is True:
                UpArrow= False

        if handedness =="Left":

            LeftArrow = True if (domhand.index_base.x<domhand.wrist.x) else False
            RightArrow= True if (domhand.pinky_upperj.x>domhand.wrist.x) else False

            if LeftArrow is True or RightArrow is True:
                UpArrow = False





        return (DownArrow, UpArrow, RightArrow, LeftArrow  )


    def Mode(self,is_active):



        if  (is_active is True
            and self.is_active_previous is False
            ):
            self.is_active_counter  +=1

        if self.is_active_counter  ==3:
            self.is_active_counter  =0

        Mode =self.Modes[self.is_active_counter]


        self.is_active_previous=is_active

        return Mode