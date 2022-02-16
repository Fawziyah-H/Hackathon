from ...helpers.xyz import xyz
from ...helpers.geom_tools import distance_xy, distance_xyz


class Folded:
    """Use this class to detect if a finger is fully folded over"""

    def __init__(self):
        self.folded_detection_frames = 3
        self.threshold_buffer_frames = 4
        self.threshold_buffer = [0 for _ in range(self.threshold_buffer_frames)]
        self.threshold_distance = 0

        # Individual finger variables
        self.folded_buffer_thumb = [0 for _ in range(self.folded_detection_frames)]
        self.is_folded_thumb = False

        self.folded_buffer_index = [0 for _ in range(self.folded_detection_frames)]
        self.is_folded_index = False

        self.folded_buffer_middle = [0 for _ in range(self.folded_detection_frames)]
        self.is_folded_middle = False

        self.folded_buffer_ring = [0 for _ in range(self.folded_detection_frames)]
        self.is_folded_ring = False

        self.folded_buffer_pinky = [0 for _ in range(self.folded_detection_frames)]
        self.is_folded_pinky = False

    def update_threshold_distance(self, hand):
        self.threshold_buffer.pop(0)
        self.threshold_buffer.append(distance_xyz(hand.index_base, hand.pinky_base))
        self.threshold_distance = (
            sum(self.threshold_buffer) / self.threshold_buffer_frames
        ) * 1.1

    def update_folded_buffer(self, hand):
        # Detect if the tip of a finger is closer to the palm center than the base

        self.folded_buffer_thumb.pop(0)
        self.folded_buffer_index.pop(0)
        self.folded_buffer_middle.pop(0)
        self.folded_buffer_ring.pop(0)
        self.folded_buffer_pinky.pop(0)

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

        # detect if finger tip is closer to palm center than the base
        tip_closer_than_base = [False, False, False, False, False]

        for index in range(5):
            if distance_xy(tips[index], hand.palm_center) < distance_xy(
                bases[index], hand.palm_center
            ):
                tip_closer_than_base[index] = True

        # Detect if the z-distance of the tip to the palm center is below threshold

        dist_below_threshold = [False, False, False, False, False]
        for index in range(5):
            if distance_xyz(tips[index], hand.palm_center) < self.threshold_distance:
                dist_below_threshold[index] = True

        # if both conditions are true append 1 to the buffer, else append 0

        either_true = [False, False, False, False, False]
        for index in range(5):
            if tip_closer_than_base[index] or dist_below_threshold[index]:
                either_true[index] = True

        if either_true[0]:
            self.folded_buffer_thumb.append(1)
        else:
            self.folded_buffer_thumb.append(0)

        if either_true[1]:
            self.folded_buffer_index.append(1)
        else:
            self.folded_buffer_index.append(0)

        if either_true[2]:
            self.folded_buffer_middle.append(1)
        else:
            self.folded_buffer_middle.append(0)

        if either_true[3]:
            self.folded_buffer_ring.append(1)
        else:
            self.folded_buffer_ring.append(0)

        if either_true[4]:
            self.folded_buffer_pinky.append(1)
        else:
            self.folded_buffer_pinky.append(0)

    def update_is_folded(self):
        if sum(self.folded_buffer_thumb) == self.folded_detection_frames:
            self.is_folded_thumb = True
        else:
            self.is_folded_thumb = False

        if sum(self.folded_buffer_index) == self.folded_detection_frames:
            self.is_folded_index = True
        else:
            self.is_folded_index = False

        if sum(self.folded_buffer_middle) == self.folded_detection_frames:
            self.is_folded_middle = True
        else:
            self.is_folded_middle = False

        if sum(self.folded_buffer_ring) == self.folded_detection_frames:
            self.is_folded_ring = True
        else:
            self.is_folded_ring = False

        if sum(self.folded_buffer_pinky) == self.folded_detection_frames:
            self.is_folded_pinky = True
        else:
            self.is_folded_pinky = False

    def clear_variables(self):
        self.folded_buffer_thumb.pop(0)
        self.folded_buffer_thumb.append(0)
        self.folded_buffer_index.pop(0)
        self.folded_buffer_index.append(0)
        self.folded_buffer_middle.pop(0)
        self.folded_buffer_middle.append(0)
        self.folded_buffer_ring.pop(0)
        self.folded_buffer_ring.append(0)
        self.folded_buffer_pinky.pop(0)
        self.folded_buffer_pinky.append(0)
        self.threshold_buffer.pop(0)
        self.threshold_buffer.append(0)
        self.threshold_distance = 0

    def run(self, hand):
        if not hand.is_idle():
            self.update_threshold_distance(hand)
            self.update_folded_buffer(hand)
            self.update_is_folded()
        else:
            self.clear_variables()
