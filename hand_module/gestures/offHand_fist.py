
from .primitives.folded import Folded



class Fist:
    def __init__(self, Folded: Folded):
        """
        The Index Pinch hand symbol is simply checking for an index-thumb pinch

        all other fingers cannot be pinching
        """
        self.Folded = Folded


    def update_is_active(self):
        if(self.Folded.is_folded_middle and
                self.Folded.is_folded_ring):

            self.is_active=True
        else:
            self.is_active= False

    def run(self):
        self.update_is_active()
        self.prev_frame_mode = self.is_active