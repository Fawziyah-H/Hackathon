from .primitives.pinch import Pinch

class DoublePinch():
    def __init__(self, pinch: Pinch):
        """
        The Double Pinch hand symbol is simply checking for middle-thumb pinch and index-thumb pinches

        all other fingers cannot be pinching
        """
        self.pinch = pinch
        self.is_active = False
        self.prev_frame_mode = False

    def update_is_active(self):
        if(self.pinch.is_pinched_index and 
            self.pinch.is_pinched_middle and
            not self.pinch.is_pinched_ring and 
            not self.pinch.is_pinched_pinky):
            self.is_active=True
        else:
            self.is_active= False


    def run(self):
        self.update_is_active()
        self.prev_frame_mode = self.is_active