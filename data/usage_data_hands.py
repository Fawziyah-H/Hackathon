# By Ashild Kummen

import datetime
from tabulate import tabulate
import platform


class UsageDataCollector(object):
    def __init__(self):
        self.timestamp = str(datetime.datetime.now())
        self.data = {
            self.timestamp: {
                "Identifier": "UsageData",
                "ConfigurationUsed": {},
                "Hardware": {},
                "ScreenSize": {"x": 0, "y": 0},
                "ApplicationsOpened": [],
                "StartupTime": 0,
                "UsageTime": 0,
                "TimeActiveHandInFrame": {"Left": [], "Right": []},
                "nIdleStateChanges": {"Left": 0, "Right": 0},
                "nAOIChanges": 0,
                "nClicks": {"Left": 0, "Right": 0, "Double": 0},
                "nDrags": 0,
                "timeDragging": [],
                "nScrolls": 0,
                "timeScrolling": [],
            }
        }

        self.frameData = []
        self.frameData_headers = [
            "Identifier",
            "Frame",
            "Timestamp",
            "x",
            "y",
            "distanceToCam",
            "Window",
            "left_click",
            "right_click",
            "double_click",
            "drag",
            "scroll",
            "scrollDirection",
        ]

    def initialise(self, settings=None, cursorControl=None):
        if settings != None and cursorControl != None:
            self.data[self.timestamp]["ConfigurationUsed"] = {
                "nHands": settings.get_setting("nHands"),
                "handedness": settings.get_setting("Handedness"),
                "cursorControl": cursorControl,
                "smoothing": int(settings.get_setting("Smoothness")),
                "sensitivity": float(settings.get_setting("Sensitivity")),
                "scroll_speed": float(settings.get_setting("ScrollSpeed")),
                "screen_config": str(settings.get_setting("Arrangement")),
                "usecase": settings.get_setting("UseCase"),
                "showHandTracking": settings.get_setting("ShowHandTracking"),
                "dragWithIndex": settings.get_setting("dragWithIndex"),
                "activateArrowKey": settings.get_setting("activateArrowKey")
                in ["True", "true"],
            }

        self.data[self.timestamp]["Hardware"] = {
            "OperatingSystem": platform.system(),
            "Release": platform.release(),
            "Version": platform.version(),
            "Processer": platform.processor(),
            "Platform type": platform.platform(),
            "Machine type": platform.machine(),
        }

    def addData(self, key, value, key2=None):
        if key2 == None:
            self.data[self.timestamp][key] = value
        else:
            self.data[self.timestamp][key][key2] = value

    def incrementCount(self, key, key2=None):
        if key2 == None:
            self.data[self.timestamp][key] += 1
        else:
            self.data[self.timestamp][key][key2] += 1

    def appendToList(self, key, value, key2=None):
        if key2 == None:
            self.data[self.timestamp][key].append(value)
        else:
            self.data[self.timestamp][key][key2].append(value)

    def saveData(self):
        pass

    def addTimeData(
        self,
        x: int,
        y: int,
        distanceToCam: float,
        window: str,
        left_click: bool,
        right_click: bool,
        double_click: bool,
        drag: bool,
        scroll: bool,
        scrollDirection: str,
    ):
        if len(self.frameData) == 0:
            frameNo = 1
        else:
            frameNo = self.frameData[-1][1] + 1

        timestamp = str(datetime.datetime.now())
        identifier = "UsageData"
        new_data = [
            identifier,
            frameNo,
            timestamp,
            x,
            y,
            distanceToCam,
            window,
            left_click,
            right_click,
            double_click,
            drag,
            scroll,
            scrollDirection,
        ]
        self.frameData.append(new_data)

    def displayData(self):
        print(self.data)
        print(tabulate(self.frameData, headers=self.frameData_headers))


usageData = UsageDataCollector()