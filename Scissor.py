from geom_tools import distance_xyz

class Scissor:
    def __init__(self):
        self.clicked = False
        self.distance = 50
        self.sensitivity = 0.10

    def update_distance(self, hand):
        """Calculate the distance between the index and middle tips"""

        palm_scalar = (
            distance_xyz(hand.wrist, hand.index_base)
            + distance_xyz(hand.wrist, hand.pinky_base)
            + distance_xyz(hand.pinky_base, hand.index_base)
        )

        self.distance = distance_xyz(hand.index_tip, hand.middle_tip) / palm_scalar

        #print("Palm scalar: ", palm_scalar)
        #print("Distance: ", self.distance)

    def update_click_status(self):
        """Update the click status based on the threshold specified"""

        if self.distance < self.sensitivity:
            self.clicked = True
        else:
            self.clicked = False

    def run(self, hand):
        self.update_distance(hand)
        self.update_click_status()
