#!/usr/bin/env python2.7

# Geometry of a cell's margin


class CellMargin:
    # defining constructor
    # origin is the upper left corner

    # todo rename table_rotation in rotation

    def __init__(self, corners_coords_dict,  cell_id, margin_id):
        self.upper_left = corners_coords_dict['upper_left']
        self.upper_right = corners_coords_dict['upper_right']
        self.lower_right = corners_coords_dict['lower_right']
        self.lower_left = corners_coords_dict['lower_left']
        self.cell_id = cell_id
        self.margin_id = margin_id

        # defining class methods
    def get_upper_left_corner(self):
        return self.upper_left

    def get_upper_right_corner(self):
        return self.upper_right(90)

    def get_lower_right_corner(self):
        return self.lower_right(135)

    def get_lower_left_corner(self):
        return self.lower_left(180)

    def get_cell_id(self):
        return self.cell_id

    def get_margin_id(self):
        return self.cell_id

    def get_polygon_coord(self):
        return [
            [
                self.upper_left().x,
                self.upper_left().y
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
                self.upper_left().x,
                self.upper_left().y
            ],
        ]


