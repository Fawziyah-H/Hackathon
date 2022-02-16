# By Robert Shaw - expanded by Ashild Kummen
from ...helpers.geom_tools import distance_xy, distance_xyz
from win32api import GetSystemMetrics  # pip install pywin32



class Pinch:
    def __init__(self, pinch_sensitivity=0.15, pinch_detection_frames=3):
        self.pinch_sensitivity = pinch_sensitivity
        # index finger
        self.pinch_buffer_index = [1 for _ in range(pinch_detection_frames)]
        self.pinch_distance_index = 0.5
        self.last_is_pinched_index = False
        self.is_pinched_index = False
        # middle finger
        self.pinch_buffer_middle = [1 for _ in range(pinch_detection_frames)]
        self.pinch_distance_middle = 0.5
        self.last_is_pinched_middle = False
        self.is_pinched_middle = False
        # ring finger
        self.pinch_buffer_ring = [1 for _ in range(pinch_detection_frames)]
        self.pinch_distance_ring = 0.5
        self.last_is_pinched_ring = False
        self.is_pinched_ring = False
        # pinky finger
        self.pinch_buffer_pinky = [1 for _ in range(pinch_detection_frames)]
        self.pinch_distance_pinky = 0.5
        self.last_is_pinched_pinky = False
        self.is_pinched_pinky = False

    def update_pinch_distances(self, hand):
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

        if hand.is_idle():
            self.pinch_distance_index = 1
            self.pinch_distance_middle = 1
            self.pinch_distance_ring = 1
            self.pinch_distance_pinky = 1
        else:
            self.pinch_distance_index = (
                distance_xyz(hand.thumb_tip, hand.index_tip)
            ) / palm_scalar
            self.pinch_distance_middle = (
                distance_xyz(hand.thumb_tip, hand.middle_tip)
            ) / palm_scalar
            self.pinch_distance_ring = (
                distance_xyz(hand.thumb_tip, hand.ring_tip)
            ) / palm_scalar
            self.pinch_distance_pinky = (
                distance_xyz(hand.thumb_tip, hand.pinky_tip)
            ) / palm_scalar

    def update_pinch_status(self):
        """Update the pinch status based on the average and threshold specified"""

        # INDEX___________________________________________________________

        self.pinch_buffer_index.append(self.pinch_distance_index)
        self.pinch_buffer_index.pop(0)
        self.last_is_pinched_index = self.is_pinched_index

        if (
            sum(self.pinch_buffer_index) / len(self.pinch_buffer_index)
            < self.pinch_sensitivity
        ):
            self.is_pinched_index = True
        else:

            self.is_pinched_index = False

        # MIDDLE___________________________________________________________

        self.pinch_buffer_middle.append(self.pinch_distance_middle)
        self.pinch_buffer_middle.pop(0)
        self.last_is_pinched_middle = self.is_pinched_middle

        if (
            sum(self.pinch_buffer_middle) / len(self.pinch_buffer_middle)
            < self.pinch_sensitivity
        ):
            self.is_pinched_middle = True
        else:
            self.is_pinched_middle = False

        # RING_____________________________________________________________

        self.pinch_buffer_ring.append(self.pinch_distance_ring)
        self.pinch_buffer_ring.pop(0)
        self.last_is_pinched_ring = self.is_pinched_ring

        if (
            sum(self.pinch_buffer_ring) / len(self.pinch_buffer_ring)
            < self.pinch_sensitivity
        ):
            self.is_pinched_ring = True
        else:
            self.is_pinched_ring = False

        # PINKY____________________________________________________________

        self.pinch_buffer_pinky.append(self.pinch_distance_pinky)
        self.pinch_buffer_pinky.pop(0)
        self.last_is_pinched_pinky = self.is_pinched_pinky

        if (
            sum(self.pinch_buffer_pinky) / len(self.pinch_buffer_pinky)
            < self.pinch_sensitivity
        ):
            self.is_pinched_pinky = True
        else:
            self.is_pinched_pinky = False

    def run(self, hand):
        self.update_pinch_distances(hand)
        self.update_pinch_status()
