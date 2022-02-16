
#By Ali Hassan
import pydirectinput
import cv2
import datetime
class ArrowController:
    def __init__(
        self,
    ):

        self.Previous_is_ring_pinched=False
        self.DownArrow_Previous = False
        self.UpArrow_Previous = False
        self.LeftArrow_Previous = False
        self.RightArrow_Previous = False

        pydirectinput.FAILSAFE=False
        pydirectinput.PAUSE=False

        pydirectinput.PAUSE = 0





    def ArrowKeyInput(self,Down,Up,Right,Left,UpArrowConfig,DownArrowConfig,LeftArrowConfig, RightnArrowConfig):


        if UpArrowConfig == "Key Press":

            if self.UpArrow_Previous is False and Up is True:
                pydirectinput.press("up")
                print("Key Press: Up")
        if UpArrowConfig == "Key Down":
            if Up is True:
                pydirectinput.keyDown("up")
                pydirectinput.keyUp("down")
                pydirectinput.keyUp("left")
                pydirectinput.keyUp("right")

                print("Key Down: Up")
            else:
                pydirectinput.keyUp("up")

###-------------------------------------------------------------------------
        if DownArrowConfig == "Key Press":

            if self.DownArrow_Previous == False and Down == True:
                pydirectinput.press("down")
                print("Key Press: Down")
        if DownArrowConfig == "Key Down":
            if Down is True:
                pydirectinput.keyDown("down")
                pydirectinput.keyUp("up")
                pydirectinput.keyUp("left")
                pydirectinput.keyUp("right")

                print("Key Down: Down")
            else:
                pydirectinput.keyUp("down")

###-------------------------------------------------------------------------
        if LeftArrowConfig == "Key Press":

            if self.LeftArrow_Previous is False and Left is True:
                pydirectinput.press("left")
                print("Key Press: Left")
        if LeftArrowConfig == "Key Down":
            if Left is True:
                pydirectinput.keyDown("left")
                pydirectinput.keyUp("up")
                pydirectinput.keyUp("down")
                pydirectinput.keyUp("right")

                print("Key Down: Left")
            else:
                pydirectinput.keyUp("left")

###-------------------------------------------------------------------------
        if RightnArrowConfig == "Key Press":

            if self.RightArrow_Previous is False and Right is True:

                pydirectinput.press("right")
                print("Key Press: Right")
        if RightnArrowConfig == "Key Down":
            if Right is True:
                pydirectinput.keyDown("right")
                pydirectinput.keyUp("up")
                pydirectinput.keyUp("down")
                pydirectinput.keyUp("left")

                print("Key Down: Right")
            else:
                pydirectinput.keyUp("right")




        self.DownArrow_Previous = Down
        self.UpArrow_Previous = Up
        self.RightArrow_Previous = Right
        self.LeftArrow_Previous = Left





        if self.UpArrow_Previous == False and Up == True:
            pydirectinput.press("up")
            print("up")
        if self.RightArrow_Previous == False and Right == True:
            pydirectinput.press("right")
            print("right")
        if self.LeftArrow_Previous == False and Left == True:
            pydirectinput.press("left")
            print("left")

        self.DownArrow_Previous =Down
        self.UpArrow_Previous = Up
        self.RightArrow_Previous = Right
        self.LeftArrow_Previous = Left



    def OnscrenStatus(self,status,image):


        font = cv2.FONT_HERSHEY_SIMPLEX
        fontScale = 0.8
        fontColor = (255, 255, 255)
        lineType = 2
        position_arrow = (10, 400)

        cv2.putText(
            image,
            "Mode: "+ str(status),
            position_arrow,
            font,
            fontScale,
            fontColor,
            lineType,
        )
