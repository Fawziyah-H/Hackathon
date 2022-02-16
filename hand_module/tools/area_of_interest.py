# area_of_interest.py - creates blue rectangle of which hand movemenst are processed at cursor movements within. corners map to the corners of the screen. dynamically calibrated based on distance to the camera.
# By Ashild Kummen

from win32api import GetSystemMetrics  # pip install pywin32
import cv2
from ..helpers.geom_tools import distance_xyz
import numpy as np
from win32con import SM_CMONITORS, SM_CXVIRTUALSCREEN, SM_CYVIRTUALSCREEN
import sys
from data.usage_data_hands import usageData
import datetime


class AreaOfInterest:
    """Blue rectangle that maps to the corners of the screen. Autocalibrated with distance to the camera."""

    # Area of interest identifies the rectangle in which to process hand gestures within,
    # e.g. to moving the cursor to the upper left corner of the area of interest rectangle moves is to the upper left corner of the screen.
    def __init__(self, cap, screen_config):

        # Getting screen size and ratio
        self.screen_width = GetSystemMetrics(SM_CXVIRTUALSCREEN)
        self.screen_height = GetSystemMetrics(SM_CYVIRTUALSCREEN)
        print(
            datetime.datetime.now(),
            "screen size:",
            self.screen_width,
            "x",
            self.screen_height,
        )
        sys.stdout.flush()

        self.screen_ratio = (
            self.screen_width / self.screen_height
        )  # ratio = width / height

        # Detecting multi-screen use
        self.arrangement = screen_config

        print("final:", self.screen_width, "x", self.screen_height)
        # Getting camera window width and height
        self.cam_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.cam_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        # Initialising default spacing parameter. by default the spacing is 51% of camera window
        # Spacing = gap between aoi rectangle height and camera height
        # high spacing is useful due to mediapipe struggling to detect hands that are too close.
        # for two screens, the spacing needs to adjust to accommodate a more wide or tall aoi.
        if self.arrangement == "SingleScreen":
            self.screen_width = GetSystemMetrics(0)
            self.screen_height = GetSystemMetrics(1)
            print("screen size:", self.screen_width, "x", self.screen_height)

            self.screen_ratio = (
                self.screen_width / self.screen_height
            )  # ratio = width / height
            # default 51%, then 61% for level 2, etc.
            self.spacing_levels = [0.51, 0.61, 0.71]
            self.spacing = int(0.51 * self.cam_height)

        elif (self.arrangement == "Horizontal12") or (
            self.arrangement == "Horizontal21"
        ):
            self.spacing_levels = [0.70, 0.75, 0.80]
            self.spacing = self.spacing_levels[0] * self.cam_height

        elif (self.arrangement == "Vertical12") or (self.arrangement == "Vertical21"):
            self.spacing_levels = [0.41, 0.51, 0.61]
            self.spacing = self.spacing_levels[0] * self.cam_height

        # setting default palm distance (distance from wrist to top of palm)
        self.default_palm_distance = 0.18

        # to keep track of spacing, as so we do not change it until it has been consistent for "nFramesForSwitching" frames
        self.prev_spacing = None
        self.spacing_count = 0
        self.nFramesForSwitching = 15  # reduce to increase sensitivity

        self.distanceToCam = 0

        self.configure()

    def configure(self, spacing=None):
        """Configure aoi"""

        if spacing:  # new spacing parameter is given
            self.spacing = int(spacing)

        # Initialising area of interst width and height
        self.height = int(self.cam_height - self.spacing)
        self.width = int(self.height * self.screen_ratio)

        # defining top left and bottom right corners (for rectangle)
        self.top_left = (
            int((self.cam_width - self.width) / 2),
            int(self.spacing * 0.5),
        )
        self.bottom_right = (
            int((self.cam_width - self.width) / 2) + self.width,
            int(self.spacing * 0.5 + self.height),
        )
        print(
            datetime.datetime.now(),
            "New AOI configured. AOI size: "
            + str(self.width)
            + "x"
            + str(self.height)
            + ". Screen size: "
            + str(self.screen_width)
            + "x"
            + str(self.screen_height)
            + ". Origin (top left corner): "
            + str(self.top_left),
        )
        sys.stdout.flush()
        usageData.incrementCount("nAOIChanges")

    def update(self, domhand):
        """Update aoi"""
        if (
            domhand.is_idle() == True
        ):  # dominant hand is idle, will not change area of interest
            return

        # calculate distance between wrist xyz and middle_base xyz:
        new_palm_distance = distance_xyz(domhand.wrist, domhand.middle_base)

        # print("new_palm_distance:", new_palm_distance)  # for debug purposes

        new_spacing = self.spacing_checker(
            new_palm_distance
        )  # use seperate function to calculate what the spacing should be

        if self.prev_spacing == new_spacing:
            self.spacing_count += 1  # add one to count as last frame spacing and this frame spacing is the same
        else:
            self.spacing_count = 0  # else reset count

        self.prev_spacing = new_spacing  # update previous frame spacing

        if (self.spacing_count >= self.nFramesForSwitching) & (
            self.spacing != new_spacing
        ):  # spacing has remained identical for more than nFrames and its different than its current spacing state.
            self.spacing_count = 0  # reset counter
            self.configure(new_spacing)  # configure new aoi with the updated spacing

        self.distanceToCam = 1 - new_palm_distance

        return self.distanceToCam

    def spacing_checker(self, new_palm_distance) -> int:
        """calculates appropriate spacing of aoi rectangle"""

        if new_palm_distance >= self.default_palm_distance - 0.025:
            return int(self.spacing_levels[0] * self.cam_height)  # min spacing, level 1
        if (
            self.default_palm_distance - 0.075
            <= new_palm_distance
            < self.default_palm_distance - 0.025
        ):
            return int(self.spacing_levels[1] * self.cam_height)  # level 2
        if new_palm_distance <= self.default_palm_distance - 0.075:
            return int(self.spacing_levels[2] * self.cam_height)  # max spacing, level 3

    def convert_xy(self, x, y):
        """Does an affine transformation for camera x,y coordinates to map to the screen pixels"""

        x, y = (
            x * self.cam_width,
            y * self.cam_height,
        )  # from percentage to camera pixel

        # from camera pixel to screen pixel
        xNew = np.interp(
            x,
            (
                (self.cam_width - self.width) / 2,
                self.cam_width - (self.cam_width - self.width) / 2,
            ),
            (0, self.screen_width),
        )
        yNew = np.interp(
            y,
            (
                (self.cam_height - self.height) / 2,
                self.cam_height - (self.cam_height - self.height) / 2,
            ),
            (0, self.screen_height),
        )

        if self.arrangement == "Vertical21":
            # because second screen is above the first, we need to subtract the height of the second screen:
            yNew = yNew - (self.screen_height - int(GetSystemMetrics(1)))

        if self.arrangement == "Horizontal21":
            # because second screen is to the left of the first, we need to subtract the width of the second screen:
            xNew = xNew - (self.screen_width - int(GetSystemMetrics(0)))

        return xNew, yNew

    def basic_convert(self, x, y):
        return x * self.screen_width, y * self.screen_height
