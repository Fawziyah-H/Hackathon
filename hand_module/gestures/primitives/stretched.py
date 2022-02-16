# Made by Ashild Kummen, based on folded.py by Chenuka Ratwatte
from ...helpers.geom_tools import distance_xy, distance_xyz


class Stretched:
    """Use this class to detect if a finger is fully stretched up"""

    def __init__(self):
        self.stretched_detection_frames = 3
        self.threshold_buffer_frames = 4
        self.threshold_buffer = [0 for _ in range(self.threshold_buffer_frames)]
        self.threshold_distance = 0

        # Individual finger variables
        self.stretched_buffer_thumb = [
            0 for _ in range(self.stretched_detection_frames)
        ]
        self.is_stretched_thumb = False

        self.stretched_buffer_index = [
            0 for _ in range(self.stretched_detection_frames)
        ]
        self.is_stretched_index = False

        self.stretched_buffer_middle = [
            0 for _ in range(self.stretched_detection_frames)
        ]
        self.is_stretched_middle = False

        self.stretched_buffer_ring = [0 for _ in range(self.stretched_detection_frames)]
        self.is_stretched_ring = False

        self.stretched_buffer_pinky = [
            0 for _ in range(self.stretched_detection_frames)
        ]
        self.is_stretched_pinky = False

    def update_stretched_buffer(self, hand):
        # Detect if the tip of a finger is closer to the palm center than the base

        self.stretched_buffer_thumb.pop(0)
        self.stretched_buffer_index.pop(0)
        self.stretched_buffer_middle.pop(0)
        self.stretched_buffer_ring.pop(0)
        self.stretched_buffer_pinky.pop(0)

        tips = [
            hand.thumb_tip,
            hand.index_tip,
            hand.middle_tip,
            hand.ring_tip,
            hand.pinky_tip,
        ]
        bases = [
            hand.thumb_base,
            hand.index_base,
            hand.middle_base,
            hand.ring_base,
            hand.pinky_base,
        ]
        upperj = [
            hand.thumb_upperj,
            hand.index_upperj,
            hand.middle_upperj,
            hand.ring_upperj,
            hand.pinky_upperj,
        ]

        wrist = hand.wrist
        palm_center = hand.palm_center

        # detect if finger tip is closer to palm center than the base
        finger_stretched = [False, False, False, False, False]

        # for thumb: check if tip of thumb is closer to tip of index finger than center of palm
        if distance_xy(tips[0], palm_center) > distance_xyz(upperj[0], palm_center):
            finger_stretched[0] = True

        # for other fingers: check if distance between tip of finger to center of palm is higher than upper finger joint to wrist
        for index in range(1, 5):
            if distance_xy(tips[index], bases[index]) > distance_xy(
                upperj[index], bases[index]
            ):
                finger_stretched[index] = True

        # if both conditions are true append 1 to the buffer, else append 0
        if finger_stretched[0]:
            self.stretched_buffer_thumb.append(1)
        else:
            self.stretched_buffer_thumb.append(0)

        if finger_stretched[1]:
            self.stretched_buffer_index.append(1)
        else:
            self.stretched_buffer_index.append(0)

        if finger_stretched[2]:
            self.stretched_buffer_middle.append(1)
        else:
            self.stretched_buffer_middle.append(0)

        if finger_stretched[3]:
            self.stretched_buffer_ring.append(1)
        else:
            self.stretched_buffer_ring.append(0)

        if finger_stretched[4]:
            self.stretched_buffer_pinky.append(1)
        else:
            self.stretched_buffer_pinky.append(0)

    def update_is_stretched(self):
        if sum(self.stretched_buffer_thumb) == self.stretched_detection_frames:
            self.is_stretched_thumb = True
        else:
            self.is_stretched_thumb = False

        if sum(self.stretched_buffer_index) == self.stretched_detection_frames:
            self.is_stretched_index = True
        else:
            self.is_stretched_index = False

        if sum(self.stretched_buffer_middle) == self.stretched_detection_frames:
            self.is_stretched_middle = True
        else:
            self.is_stretched_middle = False

        if sum(self.stretched_buffer_ring) == self.stretched_detection_frames:
            self.is_stretched_ring = True
        else:
            self.is_stretched_ring = False

        if sum(self.stretched_buffer_pinky) == self.stretched_detection_frames:
            self.is_stretched_pinky = True
        else:
            self.is_stretched_pinky = False

    def clear_variables(self):
        self.stretched_buffer_thumb.pop(0)
        self.stretched_buffer_thumb.append(0)
        self.stretched_buffer_index.pop(0)
        self.stretched_buffer_index.append(0)
        self.stretched_buffer_middle.pop(0)
        self.stretched_buffer_middle.append(0)
        self.stretched_buffer_ring.pop(0)
        self.stretched_buffer_ring.append(0)
        self.stretched_buffer_pinky.pop(0)
        self.stretched_buffer_pinky.append(0)
        self.threshold_buffer.pop(0)
        self.threshold_buffer.append(0)
        self.threshold_distance = 0

    def run(self, hand):
        self.update_stretched_buffer(hand)
        self.update_is_stretched()

        # print("stretched:", self.is_stretched_thumb, self.is_stretched_index, self.is_stretched_middle, self.is_stretched_ring, self.is_stretched_pinky)
