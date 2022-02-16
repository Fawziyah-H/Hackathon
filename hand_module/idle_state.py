from .helpers.xyz import xyz
from .helpers.geom_tools import distance_xyz
import datetime
from data.usage_data_hands import usageData
import time


class IdleState:
    # Handles whether hand/finger movements should be tracked or not: i.e. an active vs "idle" state

    def __init__(self):
        self.state_str_mapping = {True: "IDLE", False: "ACTIVE"}

        self.nFramesForSwitch = (
            7  # change to make states change faster. by default set to 1 second
        )

        self.prev_frame = True
        self.same_count = 0

        self.state = True  # initialised to idle

        self.timer_left = 0
        self.timer_right = 0

    def check_state(self, hand):
        # Conditions for idleness: if any of these are met, the state is idle. If not, the state is active.
        # Condition 1: The hand is turned around so the palm is facing inward i.e. not outwards towards the camera.
        if ((hand.leftorright == "Right") & (hand.index_tip.x > hand.pinky_tip.x)) | (
            (hand.leftorright == "Left") & (hand.index_tip.x < hand.pinky_tip.x)
        ):
            this_state = True

        # Condition 2: The hand is closed / resting so that the tip of the index finger is below the tip of the thumb.
        elif (
            hand.index_tip.y - (distance_xyz(hand.wrist, hand.pinky_base) * 0.1)
        ) > hand.thumb_tip.y:
            this_state = True

        else:
            this_state = False  # "Active"

        # Updating statetracker
        if (
            self.prev_frame != this_state
        ):  # reset count if frame has dissimilar state from last frame
            self.same_count = 0
        else:  # add one to count
            self.same_count += 1

        self.prev_frame = this_state  # update previous frame value to current frame

        # Checking if the same state has been present for nFramesForSwitch, and if so changing the state
        if (self.same_count >= self.nFramesForSwitch) & (
            this_state != self.state
        ):  # state switch! Updating self.domhand / self.subhand
            self.same_count = 0
            self.state = this_state
            print(
                datetime.datetime.now(),
                "State on "
                + hand.leftorright
                + " changed to: "
                + self.state_str_mapping[this_state]
                + ".",
            )

            # logging usage data
            usageData.incrementCount("nIdleStateChanges", key2=hand.leftorright)

            if self.state == False:
                if hand.leftorright == "Left":
                    self.timer_left = time.time()
                else:
                    self.timer_right = time.time()

            if self.state == True:
                if hand.leftorright == "Left":  # went idle
                    time_active = round(time.time() - self.timer_left, 2)
                    usageData.appendToList(
                        "TimeActiveHandInFrame", value=time_active, key2="Left"
                    )
                else:
                    time_active = round(time.time() - self.timer_right, 2)
                    usageData.appendToList(
                        "TimeActiveHandInFrame", value=time_active, key2="Right"
                    )

    def reset_state(self, hand):
        self.state = True
        print(
            datetime.datetime.now(),
            "State on "
            + hand.leftorright
            + " changed to Idle due to moving out of frame.",
        )
