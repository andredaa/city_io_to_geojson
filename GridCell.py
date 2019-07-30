#!/usr/bin/env python2.7

# a class describing a squared cell in a city scope grid
import math
import geometry
import Cell


class GridCell:
    # defining constructor
    # origin is the upper left corner
    def __init__(self, origin, table_rotation, cell_size, cell_id, cell_margin=0):
        self.origin = origin
        self.table_rotation = table_rotation
        self.cell_size = cell_size
        self.cell_id = cell_id
        self.cell_margin = cell_margin

        # create inner and outer cells
        self.outer_cell = self.create_outer_cell()
        self.inner_cell = self.create_inner_cell()

        # defining class methods
    def get_origin(self):
        return self.origin

    def get_outer_cell(self):
        return self.outer_cell

    def get_inner_cell(self):
        return self.inner_cell

    def get_table_rotation(self):
        return self.table_rotation

    def create_outer_cell(self):
        return Cell.Cell(self.get_origin(), self.table_rotation, self.cell_size, self.cell_id)

    def create_inner_cell(self):
        inner_cell_size = self.cell_size - 2 * self.cell_margin
        return Cell.Cell(self.get_inner_square_origin(), self.table_rotation, inner_cell_size, self.cell_id)

    # gets the origin of a smaller square inside the cell - with a given margin to the bounding cells walls
    def get_inner_square_origin(self):
        distance_from_outer_cell_origin = self.cell_margin * math.sqrt(2)

        # TODO: Figure out if there is an alternative to negative distance and 360-45 degree
        return geometry.get_point_in_distance(self.get_origin(), -distance_from_outer_cell_origin, (360 - 45),
                                              self.get_table_rotation())
