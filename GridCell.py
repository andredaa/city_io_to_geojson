#!/usr/bin/env python2.7

# a class describing a squared cell in a city scope grid
import math

from shapely.geometry import Point, Polygon


class GridCell:
    # defining constructor
    # origin is the upper left corner
    def __init__(self, origin, table_rotation, cell_size, cell_id, cell_margin=0):
        self.origin = origin
        self.table_rotation = table_rotation
        self.cell_size = cell_size
        self.cell_id = cell_id
        self.cell_margin = cell_margin

        # defining class methods
    def get_origin(self):
        return self.origin

    def get_table_rotation(self):
        return self.table_rotation

    def get_cell_size(self):
        return self.cell_size

    def get_cell_id(self):
        return self.cell_id

    def get_cell_margin(self):
        return self.cell_margin

    def get_upper_right_corner(self):
        return self.get_cell_corner(90)

    def get_lower_right_corner(self):
        return self.get_cell_corner(135)

    def get_lower_left_corner(self):
        return self.get_cell_corner(180)

    # gets the cell corner as a point with coordinates.
    def get_cell_corner(self, angle):
        if (angle % 90 == 0):
            distance = self.get_cell_size()
        elif (angle % 45 == 0):
            distance = self.get_cell_size() * math.sqrt(2)
        else:
            raise Exception('The angle does not correspond to a corner in a square. Given angle: {}'.format(angle))

        return self.get_point_in_distance(distance, angle)

    # gets the origin of a smaller square inside the cell - with a given margin to the bounding cells walls
    def get_inner_square_origin(self, margin):
        distance_from_outer_cell_orgin = margin * math.sqrt(2)

        # TODO: Figure out if there is an alternative to negative distance and 360-45 degree
        return self.get_point_in_distance(-distance_from_outer_cell_orgin, (360-45))

    # returns a Point located in a given distance and angle from the cell_origin. Considers table rotation.
    def get_point_in_distance(self, distance, angle):
        # direction by table rotation and angle of the corner
        bearing = angle + self.get_table_rotation()

        corner_x = self.get_origin().x + distance * math.sin(math.radians(bearing))
        corner_y = self.get_origin().y + distance * math.cos(math.radians(bearing))

        return Point(corner_x, corner_y)








