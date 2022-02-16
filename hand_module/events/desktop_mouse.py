#By Ali Hassan (click,drag events) and Rob Shaw (cursor movement)
from win32api import GetSystemMetrics  # pip install pywin32
import pydirectinput
import pyautogui
from pynput.mouse import Button, Controller
import logging


class DesktopMouse:
    def __init__(self, mouse_smoothing=3):
        self.last_is_left_clicked = False
        self.last_is_right_clicked = False
        self.last_is_double_clicked = False
        self.left_click_counter = 0
        self.Drag = False

        # cursor movement
        self.cursor_xy = [0, 0]
        self.screen_width = int(GetSystemMetrics(0))
        self.screen_height = int(GetSystemMetrics(1))
        self.mouse_buffer_x = [0 for i in range(mouse_smoothing)]
        self.mouse_buffer_y = [0 for i in range(mouse_smoothing)]
        self.mouse = Controller()

        pyautogui.FAILSAFE = False

        # logging
        # self.logger = logging.getLogger("Cursor")

    def update_cursor_xy(self, x, y):
        """TAKES X,Y AND AOI INPUTS AND CONVERTS TO DESKTOP CURSOR MOVEMENTS"""
        self.mouse_buffer_x.append(x)
        self.mouse_buffer_x.pop(0)
        self.mouse_buffer_y.append(y)
        self.mouse_buffer_y.pop(0)
        self.cursor_xy = [x, y]
        # pydirectinput.moveTo(int(x), int(y))
        self.mouse.position = (
            int(sum(self.mouse_buffer_x) / len(self.mouse_buffer_x)),
            int(sum(self.mouse_buffer_y) / len(self.mouse_buffer_y)),
        )

    def click_events(self, is_left_clicked, is_right_clicked, is_double_clicked):

        """This will determine by frame  if the left-click will be a drag or a click"""
        if is_left_clicked is True:
            self.left_click_counter += 1

        """This will enable double click, only possible if last_is_double_clicked= True and the is_double_clicked= False """
        if self.last_is_double_clicked != is_double_clicked:
            if (
                is_double_clicked is True
                and is_left_clicked is False
                and self.last_is_left_clicked is False
            ):
                print("double click")
                pydirectinput.doubleClick()
                # self.mouse.click(Button.left,2)
                self.left_click_counter = 0

        """This will enable left click upon release of the pinch. Based on how long the pinch was , it will either be a left click or a release from  a drag """
        if (
            is_left_clicked is False
            and is_double_clicked is False
            and self.last_is_double_clicked is False
            and self.last_is_left_clicked is True
        ):

            if self.left_click_counter <= 7:
                self.mouse.click(Button.left, 1)
                """self.logger.debug(
                    "User clicked. Pinch distance: "
                    # + str(self.pinch_distance)
                    + ". Coordinates: "
                    + str(self.cursor_xy),
                )"""
                print("Click")
                self.left_click_counter = 0
            if self.left_click_counter > 6:
                self.mouse.release(Button.left)
                """self.logger.debug(
                    "User dragged. Pinch distance: "
                    # + str(self.pinch_distance)
                    + ". Coordinates: "
                    + str(self.cursor_xy)
                    + ". Timer: "
                    + str(self.left_click_counter)
                )"""
                print("Release")
                self.left_click_counter = 0
            self.Drag = False

        """This will enable Right  click and only possible if is_double_clicked= False and the is_double_clicked= False"""
        if self.last_is_right_clicked != is_right_clicked:
            if (
                is_right_clicked is True
                and is_double_clicked is False
                and self.last_is_double_clicked is False
            ):
                self.mouse.click(Button.right, 1)
                self.Click_event_lock = True
                print("Right Click")
                """self.logger.debug(
                    "User right clicked. Pinch distance: "
                    # + str(self.pinch_distance)
                    + ". Coordinates: "
                    + str(self.cursor_xy)
                )"""
                self.left_click_counter = 0

        """This will enable Drag and only possible self.drag is set to True and the pinch length is more than 6 frames"""
        if is_left_clicked is True and self.Drag is False and is_right_clicked is False:

            if self.left_click_counter > 6:
                self.mouse.press(Button.left)
                print("Press")
                self.Drag = True
                """self.logger.debug(
                    "User starts dragging. Pinch distance: "
                    # + str(self.pinch_distance)
                    + ". Coordinates: "
                    + str(self.cursor_xy)
                )"""
                self.Drag = True

        self.last_is_double_clicked = is_double_clicked
        self.last_is_left_clicked = is_left_clicked
        self.last_is_right_clicked = is_right_clicked

    def scroll_events(self, speed=1, direction="Down"):
        speed = (
            speed * -1 if direction == "Down" else speed
        )  # downwards scroll gesture = negative scroll value
        self.mouse.scroll(0, speed)

    def zoom_events(self):
        pass

    def update_desktop_click_events(
        self, is_left_clicked, is_right_clicked, is_double_clicked
    ):
        self.click_events(is_left_clicked, is_right_clicked, is_double_clicked)

    def update_desktop_cursor(self, x, y):
        self.update_cursor_xy(x, y)
