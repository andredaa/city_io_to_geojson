import math
from shapely.geometry import Point


# returns a Point located in a given distance and angle from the cell_origin. Considers table rotation.
def get_point_in_distance(origin, distance, angle, rotation):
    # direction by table rotation and angle of the corner
    bearing = angle + rotation

    corner_x = origin.x + distance * math.sin(math.radians(bearing))
    corner_y = origin.y + distance * math.cos(math.radians(bearing))

    return Point(corner_x, corner_y)