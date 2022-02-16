# Basic geometry tools
# By Robert Shaw

from math import sqrt, atan2, degrees

def distance_xy(point_0, point_1):
    return sqrt((point_0.x - point_1.x) ** 2 + (point_0.y - point_1.y) ** 2)

def distance_xyz(point_0, point_1):
    return sqrt((point_0.x - point_1.x) ** 2 + (point_0.y - point_1.y) ** 2 + (point_0.z - point_1.z) ** 2)

def angle_xy(point_0,point_1):
    #returns degrees relative to a horizontal line going through point_0
    # because of the way the pixel feed output is set up in open cv
    # 0 degrees points right, 90 degrees points down, 180 degrees points left and, 270 points up
    denominator = point_1.x - point_0.x
    numerator = point_1.y - point_0.y
    answer = degrees(atan2(numerator,denominator))
    if answer >=0:
        return answer
    else:
        return 360 + answer