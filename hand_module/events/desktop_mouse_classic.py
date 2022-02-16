# By Ashild Kummen, based on code by Ali Hassan
from ..helpers.geom_tools import distance_xy, distance_xyz
from ..hand import Hand
from pynput.mouse import Button, Controller
import datetime
import time
from data.usage_data_hands import usageData


class DesktopMouseClassic:
    def __init__(
        self,
        mouse_smoothing=8,
        dragWithIndex=False,
        cursorControl=True,
    ):
        # tracking click statuses
        self.last_is_clicked = False
        self.last_last_is_clicked = False
        self.is_clicked = False
        self.last_is_right_clicked = False
        self.is_right_clicked = False
        self.cursor_xy = [0, 0]
        self.start_drag_xy = [0, 0]
        self.min_count_drag = 3
        self.counter_index = 0  # for drag detection

        self.cursorControl = cursorControl  # dont move cursor with hand if false

        self.dragWithIndex = (
            dragWithIndex  # if true, drag is performed with tip of index/thumb
        )

        self.double_click_released = (
            True  # True if previous click fully released, avoids accidental clicks
        )
        self.firstDragFlag = True  # only true on first frame of an active drag
        self.start_drag_xy = [0, 0]  # to make adjustment if dragWithIndex is true

        self.Drag = False  # true when dragging

        self.mouse_buffer_x = [
            0 for i in range(mouse_smoothing)
        ]  # buffer for smoothing
        self.mouse_buffer_y = [
            0 for i in range(mouse_smoothing)
        ]  # buffer for smoothing

        mouse_smoothing_drag = (
            mouse_smoothing * 2
        )  # smooth twice as much when dragging with index
        self.mouse_buffer_x_drag = [0 for i in range(mouse_smoothing_drag)]
        self.mouse_buffer_y_drag = [0 for i in range(mouse_smoothing_drag)]

        self.mouse = Controller()  # pynput controller

        # timer for dragging
        self.t0 = time.time()

    def processMovement(
        self,
        image,
        domhand,
        aoi,
        draw,
        is_left_clicked=False,
        is_right_clicked=False,
        is_double_clicked=False,
        isScrolling=False,
        scroll_speed=1,
        scroll_direction="Up",
    ) -> str:
        """Get click status and scroll status and perform events. Return event type"""

        # Check for scroll
        if isScrolling and self.Drag == False:  # prevent simultaneous drag and scroll
            self.do_scroll(speed=scroll_speed, direction=scroll_direction)
            return "scroll"  # to not move mouse or click if scrolling

        # Move mouse
        if self.cursorControl:
            if self.Drag and self.dragWithIndex == True:
                self.update_cursor_xy_drag(domhand, aoi)
            else:
                self.update_cursor_xy(domhand, aoi)

        # Update click statuses
        if is_double_clicked:
            is_left_clicked, is_right_clicked = True, True
        self.last_last_is_clicked = self.last_is_clicked
        self.last_is_clicked = self.is_clicked
        self.is_clicked = is_left_clicked

        self.last_is_right_clicked = self.is_right_clicked
        self.is_right_clicked = is_right_clicked

        # Draw click status on screen
        draw.debug_variable(
            image,
            "Click status",
            is_left_clicked or is_right_clicked,
        )

        # Perform clicking events, return event type (str)
        event = self.click_events()
        return event

    def do_scroll(self, speed=1, direction="Down"):
        """Does scroll"""
        speed = (
            speed * -1 if direction == "Down" else speed
        )  # downwards scroll gesture = negative scroll value
        self.mouse.scroll(0, speed)

    def update_cursor_xy(self, hand: Hand, aoi):
        """Move cursor on screen"""
        raw_x = hand.palm_center.x  # uses center of palm for stability
        raw_y = hand.palm_center.y

        x, y = aoi.convert_xy(raw_x, raw_y)

        self.mouse_buffer_x.append(x)
        self.mouse_buffer_x.pop(0)
        self.mouse_buffer_y.append(y)
        self.mouse_buffer_y.pop(0)
        self.cursor_xy = [x, y]

        self.mouse.position = (
            int(sum(self.mouse_buffer_x) / len(self.mouse_buffer_x)),
            int(sum(self.mouse_buffer_y) / len(self.mouse_buffer_y)),
        )

        # Add a timer on how long its pinched with the middle or index finger
        if self.is_clicked == True:
            self.counter_index += 1

    def click_events(self) -> str:
        """Click, Right Click, Drag, and Double Click Logic. Returns which event performed if any."""
        return_str = ""  # returns which click event has occured if any

        # Check if double click released first to avoid unintentional right or left click
        if (
            self.double_click_released == False
            and self.is_clicked == False
            and self.is_right_clicked == False
            and self.last_is_clicked == False
            and self.last_is_right_clicked == False
        ):
            self.double_click_released = True

        # DOUBLE CLICK
        if (
            self.double_click_released == True
            and self.Drag == False
            and self.is_clicked == True
            and self.is_right_clicked == True
            and (self.last_is_right_clicked == False or self.last_is_clicked == False)
            and self.Drag == False
        ):
            self.double_click()
            self.counter_index = 0
            self.double_click_released = False

            return_str = "double"

        # CLICK and RELEASE
        elif (
            self.double_click_released == True
            and self.is_clicked == False
            and self.last_is_clicked == True
            and self.is_right_clicked == False
            and self.Drag == False
        ):  # click
            self.left_click()
            self.counter_index = 0
            return_str = "left"

        elif (
            self.double_click_released == True
            and self.is_clicked == False
            and self.last_is_clicked == False
            and self.last_last_is_clicked == True
            and self.is_right_clicked == False
            and self.Drag == True
        ):
            # releasing a drag
            self.release_drag()
            self.Drag = False
            self.firstDragFlag = True

            self.counter_index = 0

        # DRAG
        elif (
            self.double_click_released == True
            and self.is_clicked == True
            and self.is_right_clicked == False
            and self.Drag == False
        ):

            if self.counter_index > self.min_count_drag:
                self.Drag = True
                self.start_drag_xy = self.cursor_xy
                self.start_drag()
                self.firstDragFlag = True
                return_str = "left"

        # RIGHT CLICK
        elif (
            self.double_click_released == True
            and self.is_clicked == False
            and self.is_right_clicked == False
            and self.last_is_right_clicked == True
            and self.Drag == False
        ):
            self.right_click()
            self.counter_index = 0
            return_str = "right"

        return return_str

    def update_cursor_xy_drag(self, hand: Hand, aoi):
        """Move cursor on screen during dragging - changed to track index/thumb tip"""
        if self.firstDragFlag:
            self.start_drag_xy = [
                hand.thumb_tip.x - hand.palm_center.x,
                hand.thumb_tip.y - hand.palm_center.y,
            ]
            self.mouse_buffer_x_drag[0 : len(self.mouse_buffer_x)] = self.mouse_buffer_x
            self.mouse_buffer_x_drag[
                len(self.mouse_buffer_x) : len(self.mouse_buffer_x) * 2
            ] = self.mouse_buffer_x
            self.mouse_buffer_y_drag[0 : len(self.mouse_buffer_y)] = self.mouse_buffer_y
            self.mouse_buffer_y_drag[
                len(self.mouse_buffer_y) : len(self.mouse_buffer_y) * 2
            ] = self.mouse_buffer_y

        self.firstDragFlag = False

        raw_x = (
            hand.thumb_tip.x - self.start_drag_xy[0]
        )  # change to e.g. index_tip or pinky_base as necessary
        raw_y = hand.thumb_tip.y - self.start_drag_xy[1]
        x, y = aoi.convert_xy(raw_x, raw_y)

        self.mouse_buffer_x_drag.append(x)
        self.mouse_buffer_x_drag.pop(0)
        self.mouse_buffer_y_drag.append(y)
        self.mouse_buffer_y_drag.pop(0)
        self.mouse_buffer_x.append(x)
        self.mouse_buffer_x.pop(0)
        self.mouse_buffer_y.append(y)
        self.mouse_buffer_y.pop(0)
        self.cursor_xy = [x, y]

        self.mouse.position = (
            int(sum(self.mouse_buffer_x_drag) / len(self.mouse_buffer_x_drag)),
            int(sum(self.mouse_buffer_y_drag) / len(self.mouse_buffer_y_drag)),
        )

    def left_click(self):
        """Performs a left click"""
        self.mouse.click(Button.left)
        print(
            datetime.datetime.now(),
            "Click. Coordinates: " + str(self.cursor_xy),
        )
        usageData.incrementCount("nClicks", key2="Left")

    def right_click(self):
        """Performs a right click"""
        self.mouse.click(Button.right)
        print(
            datetime.datetime.now(),
            "Right click. Coordinates: " + str(self.cursor_xy),
        )
        usageData.incrementCount("nClicks", key2="Right")

    def start_drag(self):
        """Starts a drag"""
        self.mouse.press(Button.left)
        print(
            datetime.datetime.now(),
            "Drag (start). Coordinates: " + str(self.cursor_xy),
        )
        usageData.incrementCount("nDrags")

        self.t0 = time.time()

    def release_drag(self):
        """Releases a drag"""
        self.mouse.release(Button.left)
        time_dragging = time.time() - self.t0
        print(
            datetime.datetime.now(),
            "Release. Coordinates: "
            + str(self.cursor_xy)
            + ". Time spent dragging: "
            + str(time_dragging)
            + "s",
        )
        usageData.appendToList("timeDragging", round(time_dragging, 2))

    def double_click(self):
        """Performs a double click"""
        self.mouse.click(Button.left, 2)  # double click
        print(
            datetime.datetime.now(),
            "Double click. Coordinates: " + str(self.cursor_xy),
        )
        usageData.incrementCount("nClicks", key2="Double")
