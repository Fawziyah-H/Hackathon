# wrist angle calculator for gaming joystick
# By Robert Shaw

from ..helpers.normalise import normalise
from ..helpers.geom_tools import distance_xy
from math import atan, pi, sqrt


class WristAngle:

    def __init__(self, x_range=0.6, y_range=1):
        self.x = 0
        self.z = 0
        self.x_range = x_range
        self.y_range = y_range
        self.x_center = -0.12
        self.z_center = 0.2
        self.counter = 0

    def update_angle(self, hand, gesture):
        z = (hand.index_base.z + hand.middle_base.z) / 2
        h = (distance_xy(hand.wrist, hand.index_base) + distance_xy(hand.wrist, hand.middle_base)) / 2
        theta = atan(z / h) if h != 0 else 0
        scale_theta = 3 * theta if theta > 0 else theta
        self.z = normalise(scale_theta - self.z_center, self.y_range)

        dx = hand.pinky_base.x - hand.wrist.x
        dz = hand.pinky_base.z - hand.wrist.z
        dy = hand.pinky_base.y - hand.wrist.y
        ln = abs(sqrt(dy ** 2 + dz ** 2))
        self.x = normalise(((atan(dx / ln) * 2) / pi) - self.x_center, self.x_range) if ln != 0 else 0

        if gesture:
            self.counter += 1
        else:
            self.counter = 0

        if self.counter > 20:
            self.x_center = ((atan(dx / ln) * 2) / pi)
            self.z_center = scale_theta
