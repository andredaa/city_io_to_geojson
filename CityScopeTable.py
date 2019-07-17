#!/usr/bin/env python2.7

# a class describing a city scope table

from shapely.geometry import Point
import math
import os
import configparser
from reproject import reproject_point


class CityScopeTable:
    # defining constructor
    # origin is the upper left corner
    def __init__(self):
        # get projections from config.ini
        config = configparser.ConfigParser()
        file_path = os.path.dirname(os.path.realpath(__file__))
        config.read(file_path + '/config.ini')

        #print(config['CITY_SCOPE'].getboolean('TABLE_FLIPPED'))

        self.table_flipped = config['CITY_SCOPE'].getboolean('TABLE_FLIPPED')
        self.table_rotation = config['CITY_SCOPE'].getint('TABLE_ROTATION') # TODO can the table rotation be different form the cell rotation??
        start_cell_origin_longitude = config['CITY_SCOPE'].getfloat('ORIGIN_LONGITUDE')
        start_cell_origin_latitude = config['CITY_SCOPE'].getfloat('ORIGIN_LATITUDE')
        print(start_cell_origin_longitude, start_cell_origin_latitude)
        self.start_cell_origin = Point(start_cell_origin_longitude, start_cell_origin_latitude)
        self.table_cell_size = config['CITY_SCOPE'].getint('CELL_SIZE')
        self.table_row_count = config['CITY_SCOPE'].getint('TABLE_ROWS')
        self.table_column_count = config['CITY_SCOPE'].getint('TABLE_COLS')
        self.origin_epsg = config['SETTINGS']['ORIGIN_EPSG']
        self.local_epsg = config['SETTINGS']['LOCAL_EPSG']


    def get_projected_start_cell_origin(self):
        origin_metric_coords = self.get_reprojected_origin()
        if not self.table_flipped:
            return origin_metric_coords

        # else: shift the table origin from the SouthEast corner to the NorthWest corner
        return self.get_flipped_origin(origin_metric_coords)

    def get_table_rotation(self):
        return 360 - self.table_rotation

    def get_table_cell_size(self):
        return self.table_cell_size

    def get_table_row_count(self):
        return self.table_row_count

    def get_table_column_count(self):
        return self.table_column_count

    def get_reprojected_origin(self):
        point = [self.start_cell_origin.x, self.start_cell_origin.y]
        origin_x, origin_y = reproject_point(self.origin_epsg, self.local_epsg, point)

        return Point(origin_x, origin_y)

    # returns the opposite corner of the grid (SE->NW)
    def get_flipped_origin(self, origin_metric_coords):
        table_width = self.get_table_column_count() * self.table_cell_size
        table_height = self.get_table_row_count() * self.table_cell_size
        diagonal = math.sqrt(pow(table_width, 2) + pow(table_height, 2))
        diagonal_angle = math.degrees(math.atan(table_width/table_height))
        angle_diagonal_to_x_axis = diagonal_angle - self.get_table_rotation()
        delta_x = math.sin(math.radians(angle_diagonal_to_x_axis)) * diagonal
        delta_y = math.cos(math.radians(angle_diagonal_to_x_axis)) * diagonal
        flipped_x = origin_metric_coords.x - delta_x
        flipped_y = origin_metric_coords.y + delta_y

        return Point(flipped_x, flipped_y)