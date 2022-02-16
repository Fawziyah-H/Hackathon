from ..helpers.xyz import xyz
from ..helpers.geom_tools import distance_xy, distance_xyz, angle_xy
from ..hand import Hand
from ..gestures.gesture import Gesture
from pynput.keyboard import Controller
import logging


class Joystick:
    def __init__(self, gestures: Gesture,joystick_toggle_mode = False,activation_frames = 5,joystick_up = 'y',joystick_down = 'b',joystick_left = 'g',joystick_right = 'h'):
        # MotionInput gestures (used to id when to start the joystick)
        self.off_hand_rabbit = gestures.get_gesture("rabbit", "offhand")
        self.dom_hand_rabbit = gestures.get_gesture("rabbit", "domhand")

        # User settings (stop frames must be less than start frames)
        self.toggle_mode_on = joystick_toggle_mode
        self.start_frames = activation_frames
        self.stop_frames = self.start_frames
        if self.toggle_mode_on:
            self.start_frames *= 4
            self.stop_frames = self.start_frames
        self.joystick_smoothening = 5
        self.max_distance_to_deadzone_ratio = 1

        # Other variables for use in functions
        self.is_in_joystick_mode = False
        self.deadzone_center = xyz(0, 0, 0)
        self.deadzone_diameter = 0
        self.is_out_of_deadzone = False
        self.joystick_recognition_buffer = [0 for i in range(self.start_frames)]
        self.prev_mode = False
        self.head_angle = 0
        self.head_center = xyz(0, 0, 0)
        self.palm_distance_from_center = 0
        self.max_distance_from_center = 0

        # Variables needed for treating the joystick as a d-pad or WASD key array
        self.keyboard = Controller()
        self.up = joystick_up
        self.right = joystick_right
        self.down = joystick_down
        self.left = joystick_left
        self.d_pad_buffer = [None for i in range(self.joystick_smoothening)]
        self.current_string_combo = None
        self.current_keys_pressed = set()

    def update_joystick_mode_toggle(self, offhand: Hand):
        # Updates the joystick mode if toggle mode is on:
        # A boolean value which is used to identify when and when not the joystick is being used.
        self.joystick_recognition_buffer.pop(0)

        if (
            self.off_hand_rabbit.is_active
            and not self.dom_hand_rabbit.is_active
            and self.prev_mode == False
        ):
            self.joystick_recognition_buffer.append(1)
        elif self.off_hand_rabbit.is_active and self.prev_mode == True:
            self.joystick_recognition_buffer.append(-1)
        else:
            self.joystick_recognition_buffer.append(0)

        if sum(self.joystick_recognition_buffer) == self.start_frames:
            self.is_in_joystick_mode = True
            if self.prev_mode == False:
                print("Entered joystick mode")
        elif (
            offhand.is_idle()
            or sum(self.joystick_recognition_buffer) == -self.stop_frames
        ):
            self.is_in_joystick_mode = False
            if self.prev_mode == True:
                print("Exited joystick mode")

    def update_joystick_mode(self, offhand: Hand):
        # Updates the joystick mode if toggle mode is off:
        # A boolean value which is used to identify when and when not the joystick is being used.
        self.joystick_recognition_buffer.pop(0)

        if self.off_hand_rabbit.is_active and not self.dom_hand_rabbit.is_active:
            self.joystick_recognition_buffer.append(1)
            if sum(self.joystick_recognition_buffer) == self.start_frames:
                self.is_in_joystick_mode = True
                if not self.prev_mode:
                    print("Entered Joystick mode")
        else:
            self.joystick_recognition_buffer.append(0)
            if (
                offhand.is_idle()
                or sum(self.joystick_recognition_buffer)
                <= self.start_frames - self.stop_frames
            ):
                self.is_in_joystick_mode = False
                if self.prev_mode:
                    print("Exited Joystick mode")

    def update_joystick_deadzone(self, offhand: Hand):
        # The joystick deadzone is an area in which the joystick head can move, but nothing happens.
        # Can be used to controlhow sensitive the joystick is.The center of this is the "center" of the joystick
        # This function also sets how far the onscreen head can appear from the center i.e: "max_distance_from_center"
        if self.prev_mode == False:
            self.deadzone_center.x = offhand.palm_center.x
            self.deadzone_center.y = offhand.palm_center.y
            self.deadzone_diameter = distance_xyz(offhand.pinky_base, offhand.wrist) / 2
            self.max_distance_from_center = (
                self.deadzone_diameter * self.max_distance_to_deadzone_ratio
            )

    def update_head_angle(self, offhand: Hand):
        # sets the direction to an angle in degrees relative to a horizontal axis going through the deadzone center
        # 0 degrees points right, 90 degrees points down, 180 degrees points left and, 270 points up
        # This function is for future use, if more analogue input is required compared to a simple d_pad mapping
        if self.is_out_of_deadzone == True:
            self.head_angle = angle_xy(self.deadzone_center, offhand.palm_center)
        else:
            self.head_angle = 0

    def update_is_out_of_deadzone(self, offhand: Hand):
        # detects if the joystick head is out of the deadzone (thus allowing the joystick to start controlling things)
        self.palm_distance_from_center = distance_xy(
            self.deadzone_center, offhand.palm_center
        )
        if self.palm_distance_from_center > self.deadzone_diameter:
            self.is_out_of_deadzone = True
        else:
            self.is_out_of_deadzone = False

    def update_head_center(self, offhand: Hand):
        # Updates the location of the joystick head
        # This function is for openCV, we want to define where and where not the joystick head can be
        if self.palm_distance_from_center > self.max_distance_from_center:
            # get relative vector from joystick center
            x_rel = offhand.palm_center.x - self.deadzone_center.x
            y_rel = offhand.palm_center.y - self.deadzone_center.y
            # scale these to match the max distance the joystick head can travel
            x_scaled = (
                x_rel / self.palm_distance_from_center
            ) * self.max_distance_from_center
            y_scaled = (
                y_rel / self.palm_distance_from_center
            ) * self.max_distance_from_center
            # reobtain the absolute coordinates
            self.head_center.x = x_scaled + self.deadzone_center.x
            self.head_center.y = y_scaled + self.deadzone_center.y
        else:
            # just track the thumb if joystick head in bounds
            self.head_center = offhand.palm_center

    def d_pad_move(self):
        # This function is used to handle the actual keypresses
        # when the d_pad_buffer is full with the same value we should execute the new logic
        if self.d_pad_buffer.count(self.d_pad_buffer[0]) == len(self.d_pad_buffer):
            self.current_string_combo = self.d_pad_buffer[0]
        self.release_unactivated_keys()
        self.press_activated_keys()

    def release_unactivated_keys(self):
        keys_to_release = []

        # identify keys to be released, put them in an array
        for key_pressed in self.current_keys_pressed:
            if (
                self.current_string_combo is None
                or key_pressed not in self.current_string_combo
            ):
                keys_to_release.append(key_pressed)

        # release those keys and update the record of keys currently pressed
        for key in keys_to_release:
            self.keyboard.release(key)
            self.current_keys_pressed.remove(key)

    def press_activated_keys(self):
        # Press any new keys that need to be pressed (don't re-press already pressed ones)
        if self.current_string_combo is not None:
            for char in self.current_string_combo:
                if char not in self.current_keys_pressed:
                    self.keyboard.press(char)
                    self.current_keys_pressed.add(char)

    def find_d_pad_direction(self):
        # resolve angle into a dpad direction

        if self.is_out_of_deadzone:

            x_skew = (
                self.head_center.x - self.deadzone_center.x
            ) / self.max_distance_from_center
            y_skew = (
                self.head_center.y - self.deadzone_center.y
            ) / self.max_distance_from_center
            letters_to_press = ""

            if y_skew >= 0.5:
                letters_to_press += self.down
            elif y_skew <= -0.5:
                letters_to_press += self.up

            if x_skew >= 0.5:
                letters_to_press += self.right
            elif x_skew <= -0.5:
                letters_to_press += self.left

            self.d_pad_buffer.append(letters_to_press)
            self.d_pad_buffer.pop(0)
        else:
            self.d_pad_buffer.append(None)
            self.d_pad_buffer.pop(0)

    def clear_variables(self):
        # reset some variables once the user has finished using the joystick

        self.deadzone_diameter = 0
        self.head_angle = 0
        self.palm_distance_from_center = 0
        self.is_in_joystick_mode = False
        self.is_out_of_deadzone = False
        self.d_pad_buffer.append(None)
        self.d_pad_buffer.pop(0)
        self.max_distance_from_center = 0
        self.head_center.x = 0
        self.head_center.y = 0

        for key in self.current_keys_pressed:
            self.keyboard.release(key)
        self.current_keys_pressed.clear()
        self.current_string_combo = None

    def run_joystick(self, offhand: Hand):
        # Main function, run this in camera input to use the joystick

        if self.toggle_mode_on:
            self.update_joystick_mode_toggle(offhand)
        else:
            self.update_joystick_mode(offhand)
        if self.is_in_joystick_mode:
            self.update_joystick_deadzone(offhand)
            self.update_is_out_of_deadzone(offhand)
            self.update_head_center(offhand)
            self.find_d_pad_direction()
            self.d_pad_move()
        else:
            self.clear_variables()
        self.prev_mode = self.is_in_joystick_mode
