from ..hand import Hand
from .primitives.folded import Folded


class Gun:
    def __init__(self, fold: Folded, type="both"):
        """
        The gun hand pose has multiple types: single, double and both

        Double, the default option is as follows:
        Index, Middle and Thumb fully extended;
        Ring and pinky fingers folded in.

        Single is similar with only the index and thumb extended.

        Both means either hand pose will set this gesture to be active.

        For future use in games, maybe implement some logic to show that the gun is tilted towards the screen
        """
        self.type = "double"
        if type.lower() == "single":
            self.type = "single"
        elif type.lower() == "both":
            self.type = "both"
        self.fold_configuration = fold
        self.is_active = False
        self.prev_frame_mode = False

    def run(self):
        thumb_index_extended = not (
            self.fold_configuration.is_folded_index
            or self.fold_configuration.is_folded_thumb
        )
        ring_little_folded = (
            self.fold_configuration.is_folded_ring
            and self.fold_configuration.is_folded_pinky
        )
        middle_folded = self.fold_configuration.is_folded_middle

        active_condition = False
        if self.type == "both":
            active_condition = thumb_index_extended and ring_little_folded
        elif self.type == "single":
            active_condition = (
                thumb_index_extended and ring_little_folded and middle_folded
            )
        else:
            active_condition = (
                thumb_index_extended and ring_little_folded and not middle_folded
            )

        if active_condition:
            self.is_active = True
        else:
            self.is_active = False
