import mediapipe as mp
import cv2
from .xyz import xyz
from ..hand import Hand
from ..tools.joystick import Joystick
from ..tools.speech_to_text import speechToText


class Draw:
    def __init__(self, cap):
        # Params for writing text:
        self.font = cv2.FONT_HERSHEY_SIMPLEX
        self.fontScale = 0.8
        self.fontColor = (255, 255, 255)
        self.blueColor = (255, 0, 0)
        self.lineType = 2
        self.frameheight = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
        self.framewidth = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        self.conn_actv_clr = (255, 0, 0)
        self.conn_idle_clr = (10, 40, 10)
        self.join_actv_clr = (0, 0, 255)
        self.join_idle_clr = (30, 30, 90)

        # mediapipe tools
        self.mp_drawing = mp.solutions.drawing_utils  # mediapipe drawing tool
        self.mp_hands = mp.solutions.hands

    def draw_hand_connections(
        self, hand_landmarks, image, label, domhand: Hand, offhand: Hand
    ):
        # draw hands on camera for easier visualisation of whether mediapipe is detecting any hands

        if label == domhand.leftorright:
            hand_used = domhand
        else:
            hand_used = offhand

        if hand_used.is_idle():
            joint_colour = self.join_idle_clr
            connection_colour = self.conn_idle_clr
        else:
            joint_colour = self.join_actv_clr
            connection_colour = self.conn_actv_clr

        self.mp_drawing.draw_landmarks(
            image,
            hand_landmarks,
            self.mp_hands.HAND_CONNECTIONS,
            self.mp_drawing.DrawingSpec(color=joint_colour),
            self.mp_drawing.DrawingSpec(color=connection_colour),
        )

    def debug_variable(self, image, variable_name, variable):
        # draw hands on camera for easier visualisation of whether mediapipe is detecting any hands
        cv2.putText(
            image,
            variable_name + ": " + str(variable),
            (10, 400),
            self.font,
            self.fontScale,
            self.fontColor,
            self.lineType,
        )

    def draw_idle_states(self, image, domHand: Hand, offHand: Hand):
        # writing whether each hand (right and left) is in an idle state or not.
        if domHand.leftorright == "Right":
            right_state = "Idle" if domHand.is_idle() else "Active"
            if offHand != None:
                left_state = "Idle" if offHand.is_idle() else "Active"
            else:
                left_state = "None"
        elif domHand.leftorright == "Left":
            left_state = "Idle" if domHand.is_idle() else "Active"
            if offHand != None:
                right_state = "Idle" if offHand.is_idle() else "Active"
            else:
                right_state = "None"

        position_right = (10, 30)
        position_left = (10, 70)
        cv2.putText(
            image,
            "Right: " + right_state,
            position_right,
            self.font,
            self.fontScale,
            self.fontColor,
            self.lineType,
        )
        cv2.putText(
            image,
            "Left: " + left_state,
            position_left,
            self.font,
            self.fontScale,
            self.fontColor,
            self.lineType,
        )

    def draw_area_of_interest(self, image, aoi):
        cv2.rectangle(image, aoi.top_left, aoi.bottom_right, self.blueColor, 1)
        position_text = (
            int(aoi.bottom_right[0] - aoi.cam_width / 20),
            int(aoi.bottom_right[1] + aoi.cam_height / 20),
        )
        cv2.putText(
            image, "AOI", position_text, self.font, self.fontScale, self.blueColor, 1
        )
        return (aoi.top_left, aoi.bottom_right)

    def draw_distance(self, image, dist_to_screen):
        # draw hands on camera for easier visualisation of whether mediapipe is detecting any hands
        if dist_to_screen is not None:
            dist_to_screen = round(dist_to_screen, 2)
        cv2.putText(
            image,
            "Distance to screen" + ": " + str(dist_to_screen),
            (10, 440),
            self.font,
            self.fontScale,
            self.fontColor,
            self.lineType,
        )

    def draw_joystick(self, image, joystick: Joystick):
        # Will draw the joystick on screen if the user wants it
        # I.E - joystick mode is on
        if joystick.is_in_joystick_mode:
            self.draw_joystick_deadzone(
                image, joystick.deadzone_center, joystick.deadzone_diameter
            )
            self.draw_joystick_line(
                image, joystick.deadzone_center, joystick.head_center
            )
            self.draw_joystick_head(
                image, joystick.head_center, joystick.deadzone_diameter
            )

    def draw_joystick_deadzone(self, image, center: xyz, diameter):
        # Draws the joystick deadzone, as a white circle.
        height = int(self.frameheight * center.y)
        width = int(self.framewidth * center.x)
        center_tuple = (width, height)
        pixel_diameter = diameter * self.frameheight
        radius = int(pixel_diameter / 2)
        try:
            cv2.circle(image, center_tuple, radius, self.fontColor, self.lineType)
        except:
            print("error in drawing joystick deadzone")

    def draw_joystick_line(self, image, deadzone: xyz, head: xyz):
        # Draws a line between the deadzone and the joystick head so the two are associated to each other by the user
        start = (int(self.framewidth * deadzone.x), int(self.frameheight * deadzone.y))
        end = (int(self.framewidth * head.x), int(self.frameheight * head.y))
        cv2.line(image, start, end, self.fontColor, self.lineType)

    def draw_joystick_head(self, image, center: xyz, diameter):
        # Draws the Joystick head
        height = int(self.frameheight * center.y)
        width = int(self.framewidth * center.x)
        center_tuple = (width, height)
        pixel_diameter = (diameter * self.frameheight) - 10
        radius = int(pixel_diameter / 2)
        if radius < 0:
            radius = 30
        try:
            cv2.circle(image, center_tuple, radius, self.blueColor, -1)
        except:
            print("error in drawing joystick")

    def draw_mic_status(self,image,stt: speechToText):
        if stt.status == "Ready":
            text_to_display = "Recording gesture detected. Please wait..."
        elif stt.status == "Recording":
            text_to_display = "Listening. Please start speaking"
        elif stt.status == "Processing":
            text_to_display = "Processing.... Please wait"
        elif stt.status == None or stt.status == "Finished":
            text_to_display = ":"
        else:
            text_to_display = stt.status

        cv2.putText(
            image,
            text_to_display,
            (10, int(self.frameheight) - 10),
            self.font,
            self.fontScale,
            self.fontColor,
            self.lineType,
        )
