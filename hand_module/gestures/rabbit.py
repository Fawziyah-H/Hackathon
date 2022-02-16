from ..helpers.geom_tools import distance_xy
from .primitives.pinch import Pinch
import logging

class Rabbit():
    def __init__(self, pinch: Pinch):
        """
            The Rabbit hand pose is as follows: 
            middle and ring tips contact i.e: "pinch" the thumb tip
            Index and little fingers are extended out (i.e: not "pinching" the thumb)

            Use the run_rabbit-recognition() function to run it in any code where you are checking for pinches
        """

        #self.logger = logging.getLogger("Rabbit Hand Pose")
        self.pinch = pinch
        self.is_active = False
        self.prev_frame_mode = False

    def update_is_active(self):
        if(self.pinch.is_pinched_middle and 
            self.pinch.is_pinched_ring and
            not self.pinch.is_pinched_index and 
            not self.pinch.is_pinched_pinky):
            self.is_active=True
            if (self.prev_frame_mode == False):
                #self.logger.debug("Rabbit pose recognised...")
                pass
        else:
            self.is_active= False

    def run(self):
        #checking which fingers pinch the thumb on your chosen hand
        self.update_is_active()
        self.prev_frame_mode = self.is_active