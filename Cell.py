#!/usr/bin/env python2.7

# Geometry of squared cells defined by origin, rotation and cell_size
import math
import geometry


class Cell:
    # defining constructor
    # origin is the upper left corner

    # todo rename table_rotation in rotation

    def __init__(self, origin, table_rotation, cell_size, cell_id):
        self.origin = origin
        self.table_rotation = table_rotation
        self.cell_size = cell_size
        self.cell_id = cell_id

        # defining class methods
    def get_origin(self):
        return self.origin

    def get_table_rotation(self):
        return self.table_rotation

    def get_cell_size(self):
        return self.cell_size

    def get_cell_id(self):
        return self.cell_id

    def get_upper_right_corner(self):
        return self.get_cell_corner(90)

    def get_lower_right_corner(self):
        return self.get_cell_corner(135)

    def get_lower_left_corner(self):
        return self.get_cell_corner(180)

    # gets the cell corner as a point with coordinates.
    def get_cell_corner(self, angle):
        if angle % 90 == 0:
            distance = self.get_cell_size()
        elif angle % 45 == 0:
            distance = self.get_cell_size() * math.sqrt(2)
        else:
            raise Exception('The angle does not correspond to a corner in a square. Given angle: {}'.format(angle))

        return geometry.get_point_in_distance(self.get_origin(), distance, angle, self.get_table_rotation())

    # order of coordinates following right hand rule
    def get_cell_polygon_coord(self):
        return [
            [
                self.get_origin().x,
                self.get_origin().y
            ],
            [
                self.get_lower_left_corner().x,
                self.get_lower_left_corner().y
            ],
            [
                self.get_lower_right_corner().x,
                self.get_lower_right_corner().y
            ],
            [
                self.get_upper_right_corner().x,
                self.get_upper_right_corner().y
            ],
            # coordinates of a polygon need to form a closed linestring
            [
                self.get_origin().x,
                self.get_origin().y
            ],
        ]


