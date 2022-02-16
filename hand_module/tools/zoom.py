from ..helpers.geom_tools import distance_xy
from ..hand import Hand
from ..gestures.gesture import Gesture
from pynput.mouse import Controller, Button
import logging


class Zoom:
    """This class can be used for recognising gestures to zoom in and out for a particular scene"""

    def __init__(self, gestures: Gesture):
        # self.logger = logging.getLogger("Zoom Attempt")

        self.offhand_gesture = gestures.get_gesture("rabbit", "offhand")
        self.domhand_gesture = gestures.get_gesture("rabbit", "domhand")
        self.is_in_zoom_mode = False
        self.zoom_amt = 0
        self.buffer_frames = 4
        self.dist_between_hands = 0
        self.handdistchange_between_frames = [0 for _ in range(self.buffer_frames - 1)]
        self.distance_threshold = 5
        self.mouse = Controller()
        self.prev_frame_mode = False
        self.prev_zoom_type = None

    def update_zoom_mode(self):
        """Zoom mode is activated when the dom and off hands are both in desired state else inactivated"""
        if self.offhand_gesture.is_active and self.domhand_gesture.is_active:
            self.is_in_zoom_mode = True
            if self.prev_frame_mode == False:
                print("Zoom mode activated...")
            self.prev_frame_mode = True
        else:
            self.is_in_zoom_mode = False
            if self.prev_frame_mode:
                print("Zoom mode deactivated...")
            self.prev_frame_mode = False

    def zoom_in(self):
        """set zoom amount to 1 and write to log"""
        self.zoom_amt = 1
        if self.prev_zoom_type == None or self.prev_zoom_type == "zoom out":
            print("Zooming IN...")
            self.prev_zoom_type = "zoom in"

    def zoom_out(self):
        """set zoom amount to -1 and write to log"""
        self.zoom_amt = -1
        if self.prev_zoom_type == None or self.prev_zoom_type == "zoom in":
            print("Zooming OUT...")
            self.prev_zoom_type = "zoom out"

    def update_zoom_amt(self, domhand: Hand, offhand: Hand):
        """Zoom amount can be used to adjust how quick the zoom is based on actions. -ve for zoom out, +ve for zoom in"""
        if self.is_in_zoom_mode:
            old_dist = self.dist_between_hands
            new_dist = distance_xy(domhand.wrist, offhand.wrist)

            """Calculate the distance changes between frames."""
            if old_dist > 0:
                self.handdistchange_between_frames.append((new_dist - old_dist) * 1000)
                self.handdistchange_between_frames.pop(0)
            if 0 not in self.handdistchange_between_frames:
                """When the buffer is full calculate average change, depending on value change zoom amount"""
                average_change = sum(self.handdistchange_between_frames) / len(
                    self.handdistchange_between_frames
                )
                if average_change >= self.distance_threshold:
                    self.zoom_in()
                elif average_change <= self.distance_threshold * -1:
                    self.zoom_out()
                else:
                    self.zoom_amt = 0
            self.dist_between_hands = new_dist
        else:
            self.zoom_amt = 0
            self.handdistchange_between_frames = [
                0 for _ in range(self.buffer_frames - 1)
            ]
            self.prev_zoom_type = None

    def zooming_with_scrollwheel(self):
        if self.is_in_zoom_mode and self.zoom_amt < 0:
            self.mouse.scroll(0, -2)
        elif self.is_in_zoom_mode and self.zoom_amt > 0:
            self.mouse.scroll(0, 2)

    def run_zoom(self, domhand: Hand, offhand: Hand):
        """
        Check if user wants to zoom
        Conditions for this
        middle finger pinch
        ring finger pinch
        ON BOTH HANDS, stretch to zoom in, compress to zoom out
        """
        self.update_zoom_mode()
        """Check the direction and magnitude they want to zoom"""
        self.update_zoom_amt(domhand, offhand)
        """Zoom with the scrollwheel"""
        self.zooming_with_scrollwheel()
