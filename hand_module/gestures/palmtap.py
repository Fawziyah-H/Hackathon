# basic palmtap gesture
# By Robert Shaw

from ..helpers.xyz import xyz
from ..helpers.geom_tools import distance_xy, distance_xyz
from win32api import GetSystemMetrics  # pip install pywin32
import pydirectinput
import pyautogui
from pynput.mouse import Button, Controller

class PalmTap:
    def __init__(self, tap_sensitivity=0.4, tap_detection_frames=3):
        self.tap_sensitivity = tap_sensitivity

        # middle finger
        self.tap_buffer_middle = [1 for i in range(tap_detection_frames)]
        self.tap_distance_middle = 0.5
        self.last_is_tapped_middle = False
        self.is_tapped_middle = False

    def update_tap_distances(self, hand):
        """Calculate the distance scaled distance between the thumb and index tip"""

        # Add up the distances between the 3 outer palm landmarks
        palm_scalar = (
                distance_xyz(hand.wrist, hand.index_base)
                + distance_xyz(hand.wrist, hand.pinky_base)
                + distance_xyz(hand.pinky_base, hand.index_base)
        )

        # TODO fix this fudge, div by 0 because coords initialised as 0,0,0
        if palm_scalar == 0:
            palm_scalar += 0.1

        self.tap_distance_middle = (
                                       distance_xyz(hand.wrist, hand.middle_tip)
                                   ) / palm_scalar

    def update_tap_status(self):
        """Update the tap status based on the average and threshold specified"""

        self.tap_buffer_middle.append(self.tap_distance_middle)
        self.tap_buffer_middle.pop(0)
        self.last_is_tapped_middle = self.is_tapped_middle

        if (
                sum(self.tap_buffer_middle) / len(self.tap_buffer_middle)
                < self.tap_sensitivity
        ):
            self.is_tapped_middle = True
        else:
            self.is_tapped_middle = False

    def update_tap(self, hand):
        self.update_tap_distances(hand)
        self.update_tap_status()
