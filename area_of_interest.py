# using to map cam coordinates to screen coordinates for digital inking
# area_of_interest.py - creates blue rectangle of which hand movemenst are processed at cursor movements within. corners map to the corners of the screen.

from typing import Optional, Tuple, List, Dict
import cv2
from win32api import EnumDisplayMonitors, GetMonitorInfo  # pip install pywin32

work_area = Tuple[int, int, int, int]
class AreaOfInterest:
    """Blue rectangle that maps to the corners of the screen. Autocalibrated with distance to the camera."""

    # Area of interest identifies the rectangle in which to process hand gestures within,
    # e.g. to moving the cursor to the upper left corner of the area of interest rectangle moves is to the upper left corner of the screen.
    def __init__(self, cap, current_spacing=0):
        """Creates an AreaOfInterest Object. Responsible for defining the region of space representing
        the current monitor in use.

        :param spacing_levels: Represents the sizes of the AOI depending on user's distance from display.
        :type spacing_levels: List[float]
        :param current_spacing: The index of which spacing level to use. Defaults to 0.
        :type current_spacing: int, optional
        """        
        self.cam_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.cam_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.cam_ratio = (self.cam_width / self.cam_height)
        self.current_monitor = -1
        self.monitors = self._init_monitors()
        self.change_monitor()
        self._spacing_levels = [0.5, 0.6, 0.7]
        self.update_spacing_level(current_spacing)

    def update_spacing_level(self, level: Optional[int] = None) -> None:
        if level >= len(self._spacing_levels) or level < 0:
            raise RuntimeError("Attempt to set AOI to an invalid spacing level: ", level, ". Available levels are 0 - ",
                               len(self._spacing_levels) - 1)

        self._current_height_spacing = self._spacing_levels[level]
        self._current_width_spacing = self._current_height_spacing * self.screen_ratio / self.cam_ratio


    def convert_xy(self, x_cam_percent: float, y_cam_percent: float) -> Tuple[float,float]:
        """Does an affine transformation for camera x,y coordinates to map to the screen pixels"""

        # current spacing shows how what percent of the cam height is the screen height
        # move origin to the middle
        x_cam_percent, y_cam_percent = x_cam_percent - 0.5, y_cam_percent - 0.5
        # transform the cam percentages to the screen percentages and move origin back to left top corner
        y_screen_percent = y_cam_percent / self._current_height_spacing + 0.5
        x_screen_percent = x_cam_percent / self._current_width_spacing + 0.5
        # make sure everything in range 0-1
        y_screen_percent = max(0, min(y_screen_percent, 1))
        x_screen_percent = max(0, min(x_screen_percent, 1))

        # transform screen percentages to screen pixles
        return self.top_left[0] + x_screen_percent * self.screen_width, self.top_left[1] + y_screen_percent * self.screen_height

    def change_monitor(self) -> None:
        """Changes which monitor the area of interest represents."""        
        if self.current_monitor == len(self.monitors)-1:
            self.current_monitor = 0
        else:
            self.current_monitor += 1
        self.top_left = self.monitors[self.current_monitor][0:2]
        self._update_proportions()

    @staticmethod
    def _init_monitors() -> dict[int, work_area]:
        #Get all monitors and their working areas
        all_monitors = {}
        for index, monitor in enumerate(EnumDisplayMonitors()):
            monitor_data = GetMonitorInfo(monitor[0])
            all_monitors[index] = monitor_data["Work"]
        return all_monitors  

    def _update_proportions(self) -> None:
        monitor_info = self.monitors[self.current_monitor]
        self.screen_width = monitor_info[2]-monitor_info[0]
        self.screen_height = monitor_info[3]-monitor_info[1]
        self.screen_ratio = (self.screen_width / self.screen_height)
