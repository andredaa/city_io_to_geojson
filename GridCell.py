#!/usr/bin/env python2.7

# a class describing a squared cell in a city scope grid
import math
import geometry
import CellSquare
import CellMargin


class GridCell:
    # defining constructor
    # origin is the upper left corner
    def __init__(self, origin, table_rotation_spatial_crs, cell_size, cell_id, cell_margin=0):
        self.origin = origin
        self.table_rotation = table_rotation_spatial_crs
        self.cell_size = cell_size
        self.cell_id = cell_id
        self.cell_margin = cell_margin

        # create inner, outer cells and margins
        self.outer_cell = self.create_outer_cell()
        self.inner_cell = self.create_inner_cell()
        self.margins = self.create_margins()
        self.interactive_id = None

# defining class getters
    def get_origin(self):
        return self.origin

    def get_outer_cell(self):
        return self.outer_cell

    def get_inner_cell(self):
        return self.inner_cell

    def get_margins(self):
        return self.margins

    def get_cell_id(self):
        return self.cell_id

    def set_interactive_id(self, interactive_id):
        self.interactive_id = interactive_id

    def get_table_rotation(self):
        return self.table_rotation

# private class methods
    def create_outer_cell(self):
        return CellSquare.CellSquare(self.get_origin(), self.table_rotation, self.cell_size, self.cell_id)

    def create_inner_cell(self):
        inner_cell_size = self.cell_size - 2 * self.cell_margin
        return CellSquare.CellSquare(self.get_inner_square_origin(), self.table_rotation, inner_cell_size, self.cell_id)

    # Returns an array of margins
    def create_margins(self):
        if self.cell_margin > 0:
            return [
                CellMargin.CellMargin(self.get_corners_for_margin(0), self.cell_id, 0),
                CellMargin.CellMargin(self.get_corners_for_margin(1), self.cell_id, 1),
                CellMargin.CellMargin(self.get_corners_for_margin(2), self.cell_id, 2),
                CellMargin.CellMargin(self.get_corners_for_margin(3), self.cell_id, 3)
            ]


    # gets the origin of a smaller square inside the cell - with a given margin to the bounding cells walls
    def get_inner_square_origin(self):
        distance_from_outer_cell_origin = self.cell_margin * math.sqrt(2)

        # TODO: Figure out if there is an alternative to negative distance and 360-45 degree
        return geometry.get_point_in_distance(self.get_origin(), -distance_from_outer_cell_origin, (360 - 45),
                                              self.get_table_rotation())

    def get_corners_for_margin(self, margin_id):
        corners_for_margins = {
            # upper side of the grid cell
            0: {
                'upper_left': self.get_outer_cell().get_origin(),
                'upper_right': self.get_outer_cell().get_upper_right_corner(),
                'lower_right': self.get_inner_cell().get_upper_right_corner(),
                'lower_left': self.get_inner_cell().get_origin()
            },
            # right hand side of the grid cell
            1: {
                'upper_left': self.get_inner_cell().get_upper_right_corner(),
                'upper_right': self.get_outer_cell().get_upper_right_corner(),
                'lower_right': self.get_outer_cell().get_lower_right_corner(),
                'lower_left': self.get_inner_cell().get_lower_right_corner()
            },
            # bottom of the grid_cell
            2: {
                'upper_left': self.get_inner_cell().get_lower_left_corner(),
                'upper_right': self.get_inner_cell().get_lower_right_corner(),
                'lower_right': self.get_outer_cell().get_lower_right_corner(),
                'lower_left': self.get_outer_cell().get_lower_left_corner()
            },
            # left hand side of the grid_cell
            3: {
                'upper_left': self.get_outer_cell().get_origin(),
                'upper_right': self.get_inner_cell().get_origin(),
                'lower_right': self.get_inner_cell().get_lower_left_corner(),
                'lower_left': self.get_outer_cell().get_lower_left_corner()
            },
        }

        return corners_for_margins[margin_id]
