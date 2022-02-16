# made by Ashild Kummen
from ..helpers.geom_tools import distance_xyz
from pynput.mouse import Button, Controller
import time
import datetime
from data.usage_data_hands import usageData


class Scroll:
    """Gesture with folded thumb, ring finger, and pinky"""

    def __init__(self):
        self.status = False  # True if scrolling
        self.prev_frame = False
        self.same_count = 0

        self.direction = "Up"  # either "Up" or "Down"
        self.prev_index_y = [0 for i in range(6)]

        # initialising configuration parameters
        self.min_distane_index_middle = 0.24
        self.min_distance_thumb_ring = 0.35
        self.nFramesForSwitch = 5

        # timer
        self.t0 = time.time()

    def detect_scroll(self, hand):
        dist_to_camera = distance_xyz(hand.wrist, hand.middle_base)

        if dist_to_camera == 0:
            # hand out of frame
            self.status = False
            self.same_count = 0
            return

        dist_index_middle = distance_xyz(hand.middle_tip, hand.index_tip)

        dist_thumb_ring = distance_xyz(hand.ring_upperj, hand.thumb_tip)

        # taking distance to camera into account:
        dist_index_middle = abs(dist_index_middle / dist_to_camera)
        dist_thumb_ring = abs(dist_thumb_ring / dist_to_camera)

        # CONDITION FOR SCROLL: the ring, pinky finger, and thumb  is close to the ring finger
        if (
            hand.folded.is_folded_ring
            and hand.folded.is_folded_pinky
            and hand.folded.is_folded_thumb
            and (dist_thumb_ring < self.min_distance_thumb_ring)
        ):
            new_scroll_status = True
        else:
            new_scroll_status = False

        # Update and check against tracking parameters
        if new_scroll_status == self.prev_frame:  # status is the same
            self.same_count += 1
        else:
            self.same_count = 0

        self.prev_frame = new_scroll_status

        # Get direction
        self.update_direction(hand.index_tip.y)

        # Switch to/from scrolling mode if conditions met and it has been consistent for nFramesForSwitch:
        if (self.same_count >= self.nFramesForSwitch) & (
            new_scroll_status != self.status  # switch
        ):
            self.status = new_scroll_status
            if self.status == True:
                self.t0 = time.time()
                print(datetime.datetime.now(), "Scroll started.")
                usageData.incrementCount("nScrolls")  # update usage data

            else:
                time_spent = time.time() - self.t0
                print(
                    datetime.datetime.now(),
                    "scroll ended. Time spent scrolling: ",
                    str(time_spent) + "s",
                )
                usageData.appendToList(
                    "timeScrolling", round(time_spent, 2)
                )  # update usage data

        return self.status  # True if scrolling

    def update_direction(self, new_index_y):
        """Get scroll gesture direction"""
        average_now = sum(self.prev_index_y[-4:-1]) / 3  # last 3 frames
        average_before = sum(self.prev_index_y[0:3]) / 3  # 3rd-6th last frame

        if abs(average_now - average_before) > 0.02:  # movement over treshold
            moving = True
        else:
            moving = False

        if moving == True:
            new_direction = "Down" if average_now > average_before else "Up"
            if self.status == True and (new_direction != self.direction):
                # change of direction
                self.direction = new_direction
                print(
                    datetime.datetime.now(),
                    "Scroll direction changed to:" + self.direction,
                )

        self.prev_index_y.append(new_index_y)
        if len(self.prev_index_y) > 6:
            self.prev_index_y.pop(0)
