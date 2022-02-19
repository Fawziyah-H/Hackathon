from geom_tools import distance_xyz

class MiddlePinch():
    def __init__(self, pinch_sensitivity=0.15, pinch_detection_frames=3):
        self.pinch_sensitivity = pinch_sensitivity
        self.pinch_buffer_middle = [1 for _ in range(pinch_detection_frames)]
        self.pinch_distance_middle = 0.5
        self.clicked = False

    
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

        self.pinch_distance_middle = (
                distance_xyz(hand.thumb_tip, hand.middle_tip)
            ) / palm_scalar


    def update_pinch_status(self):
        """Update the pinch status based on the average and threshold specified"""
        self.pinch_buffer_middle.append(self.pinch_distance_middle)
        self.pinch_buffer_middle.pop(0)

        if (
            sum(self.pinch_buffer_middle) / len(self.pinch_buffer_middle)
            < self.pinch_sensitivity
        ):
            self.clicked = True
        else:
            self.clicked = False

    def run(self, hand):
        self.update_pinch_distances(hand)
        self.update_pinch_status()