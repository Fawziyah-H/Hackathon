from .helpers.xyz import xyz
from .idle_state import IdleState
from .gestures.primitives.folded import Folded
from .gestures.primitives.pinch import Pinch
from .gestures.primitives.stretched import Stretched


class Hand:
    def __init__(self, leftorright: str, domoroff: str, pinch_sensitivity=0.14):
        self.thumb_tip = xyz(0, 0, 0)
        self.index_tip = xyz(0, 0, 0)
        self.middle_tip = xyz(0, 0, 0)
        self.ring_tip = xyz(0, 0, 0)
        self.pinky_tip = xyz(0, 0, 0)
        self.thumb_base = xyz(0, 0, 0)
        self.index_base = xyz(0, 0, 0)
        self.middle_base = xyz(0, 0, 0)
        self.ring_base = xyz(0, 0, 0)
        self.pinky_base = xyz(0, 0, 0)
        self.wrist = xyz(0, 0, 0)
        self.palm_center = xyz(0, 0, 0)

        # getting upper joint coordinate of each finger
        self.thumb_upperj = xyz(0, 0, 0)
        self.index_upperj = xyz(0, 0, 0)
        self.middle_upperj = xyz(0, 0, 0)
        self.ring_upperj = xyz(0, 0, 0)
        self.pinky_upperj = xyz(0, 0, 0)

        self.leftorright = leftorright
        self.idlenesstracker = IdleState()

        self.index_pinky_dist = {"x": [], "y": []}

        self.folded = Folded()  # tracks which fingers are folded
        self.stretched = Stretched()  # tracks which fingers are stretched
        self.pinch = Pinch(
            pinch_sensitivity=pinch_sensitivity
        )  # tracks pinching gesturing

    def is_idle(self) -> bool:
        # returns whether hand is idle or not (True = idle)
        return self.idlenesstracker.state

    def is_turned_around(self) -> bool:
        # returns whether hand has palm facing inward rather than outward i.e. turned around
        if ((self.leftorright == "Right") & (self.index_tip.x > self.pinky_tip.x)) | (
            (self.leftorright == "Left") & (self.index_tip.x < self.pinky_tip.x)
        ):
            return True
        else:
            return False

    def is_stretched_out(self) -> bool:
        # returns whether hand is stretched out (no folded fingers)
        if (
            self.stretched.is_stretched_thumb
            and self.stretched.is_stretched_index
            and self.stretched.is_stretched_middle
            and self.stretched.is_stretched_ring
            and self.stretched.is_stretched_pinky
        ):
            return True
        else:
            return False

    def find_palm_center(self):
        # Finds a point in the center of the palm to track
        self.palm_center.x = (self.middle_base.x - self.wrist.x) / 2 + self.wrist.x
        self.palm_center.y = (self.middle_base.y - self.wrist.y) / 2 + self.wrist.y
        self.palm_center.z = (self.middle_base.z - self.wrist.z) / 2 + self.wrist.z

    def update_index_pinky_dist(self):
        self.index_pinky_dist["x"].append(self.index_tip.x - self.pinky_tip.x)
        self.index_pinky_dist["y"].append(self.index_tip.y - self.pinky_tip.y)

    def update(self, handdata_raw):
        # takes hand landmark data from mediapipe hands and processes it
        if handdata_raw == None:  # hand is out of frame
            self.reset()
            return

        # Getting hand interestpoints: (x,y,z)
        self.thumb_tip = xyz(
            handdata_raw.landmark[4].x,
            handdata_raw.landmark[4].y,
            handdata_raw.landmark[4].z,
        )
        self.index_tip = xyz(
            handdata_raw.landmark[8].x,
            handdata_raw.landmark[8].y,
            handdata_raw.landmark[8].z,
        )
        self.middle_tip = xyz(
            handdata_raw.landmark[12].x,
            handdata_raw.landmark[12].y,
            handdata_raw.landmark[12].z,
        )
        self.ring_tip = xyz(
            handdata_raw.landmark[16].x,
            handdata_raw.landmark[16].y,
            handdata_raw.landmark[16].z,
        )
        self.pinky_tip = xyz(
            handdata_raw.landmark[20].x,
            handdata_raw.landmark[20].y,
            handdata_raw.landmark[20].z,
        )
        self.thumb_base = xyz(
            handdata_raw.landmark[2].x,
            handdata_raw.landmark[2].y,
            handdata_raw.landmark[2].z,
        )
        self.index_base = xyz(
            handdata_raw.landmark[5].x,
            handdata_raw.landmark[5].y,
            handdata_raw.landmark[5].z,
        )
        self.middle_base = xyz(
            handdata_raw.landmark[9].x,
            handdata_raw.landmark[9].y,
            handdata_raw.landmark[9].z,
        )
        self.ring_base = xyz(
            handdata_raw.landmark[13].x,
            handdata_raw.landmark[13].y,
            handdata_raw.landmark[13].z,
        )
        self.pinky_base = xyz(
            handdata_raw.landmark[17].x,
            handdata_raw.landmark[17].y,
            handdata_raw.landmark[17].z,
        )
        self.wrist = xyz(
            handdata_raw.landmark[0].x,
            handdata_raw.landmark[0].y,
            handdata_raw.landmark[0].z,
        )
        self.thumb_upperj = xyz(
            handdata_raw.landmark[3].x,
            handdata_raw.landmark[3].y,
            handdata_raw.landmark[3].z,
        )
        self.index_upperj = xyz(
            handdata_raw.landmark[7].x,
            handdata_raw.landmark[7].y,
            handdata_raw.landmark[7].z,
        )
        self.middle_upperj = xyz(
            handdata_raw.landmark[11].x,
            handdata_raw.landmark[11].y,
            handdata_raw.landmark[11].z,
        )
        self.ring_upperj = xyz(
            handdata_raw.landmark[15].x,
            handdata_raw.landmark[15].y,
            handdata_raw.landmark[15].z,
        )
        self.pinky_upperj = xyz(
            handdata_raw.landmark[19].x,
            handdata_raw.landmark[19].y,
            handdata_raw.landmark[19].z,
        )

        self.find_palm_center()
        self.update_index_pinky_dist()

        # Checking hand idleness
        self.idlenesstracker.check_state(self)

        #  Updating folded and stretched
        self.folded.run(self)
        self.stretched.run(self)
        self.pinch.run(self)

    def reset(self):
        """Gets called when hand is out of frame"""
        if self.is_idle() == False:
            # set hand to idle if it used to be active
            self.idlenesstracker.reset_state(self)
        # reset hand interestpoints (x,y,z)
        self.thumb_tip = xyz(0, 0, 0)
        self.index_tip = xyz(0, 0, 0)
        self.middle_tip = xyz(0, 0, 0)
        self.ring_tip = xyz(0, 0, 0)
        self.pinky_tip = xyz(0, 0, 0)
        self.thumb_base = xyz(0, 0, 0)
        self.index_base = xyz(0, 0, 0)
        self.middle_base = xyz(0, 0, 0)
        self.ring_base = xyz(0, 0, 0)
        self.pinky_base = xyz(0, 0, 0)
        self.wrist = xyz(0, 0, 0)
        self.palm_center = xyz(0, 0, 0)
        self.thumb_upperj = xyz(0, 0, 0)
        self.index_upperj = xyz(0, 0, 0)
        self.middle_upperj = xyz(0, 0, 0)
        self.ring_upperj = xyz(0, 0, 0)
        self.pinky_upperj = xyz(0, 0, 0)
