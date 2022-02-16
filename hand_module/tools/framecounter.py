# fps counter
# By Robert Shaw
import time


class framecounter:
    """basic framecounter, initialise outside of your frame process"""
    def __init__(self):
        self.frames = 0
        self.second = 0

    def update(self):
        """update each frame"""
        if time.time() < self.second + 1:
            self.frames += 1
        else:
            print("FPS:", self.frames)
            self.second = time.time()
            self.frames = 1
