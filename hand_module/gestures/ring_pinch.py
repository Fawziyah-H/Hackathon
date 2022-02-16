from .primitives.pinch import Pinch

class RingPinch():
    def __init__(self, pinch: Pinch):
        """
        The Ring Pinch hand symbol is simply checking for an ring-thumb pinch

        all other fingers cannot be pinching
        """
        self.pinch = pinch
        self.is_active = False
        self.prev_frame_mode = False

    def update_is_active(self):
        if( not self.pinch.is_pinched_index and 
            not self.pinch.is_pinched_middle and
            self.pinch.is_pinched_ring and 
            not self.pinch.is_pinched_pinky):
            self.is_active=True
        else:
            self.is_active= False

    def run(self):
        self.update_is_active()
        self.prev_frame_mode = self.is_active