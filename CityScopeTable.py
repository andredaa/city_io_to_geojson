#!/usr/bin/env python2.7

# a class describing a city scope table

from shapely.geometry import Point
import math
import os
import configparser
import pyproj


class CityScopeTable:
    # defining constructor
    # origin is the upper left corner
    def __init__(self):
        # get projections from config.ini
        config = configparser.ConfigParser()
        file_path = os.path.dirname(os.path.realpath(__file__))
        config.read(file_path + '/config.ini')

        # print(config['CITY_SCOPE'].getboolean('TABLE_FLIPPED'))

        self.table_flipped = config['CITY_SCOPE'].getboolean('TABLE_FLIPPED')
        self.table_rotation_lat_lon = config['CITY_SCOPE'].getint(
            'TABLE_ROTATION')  # the table orientation relative to the WGS84
        start_cell_origin_longitude = config['CITY_SCOPE'].getfloat('ORIGIN_LONGITUDE')
        start_cell_origin_latitude = config['CITY_SCOPE'].getfloat('ORIGIN_LATITUDE')
        print("lon, lat", start_cell_origin_longitude, start_cell_origin_latitude)
        self.start_cell_origin = Point(start_cell_origin_longitude, start_cell_origin_latitude)
        self.table_cell_size = config['CITY_SCOPE'].getint('CELL_SIZE')
        self.table_cell_margin = config['CITY_SCOPE'].getint('CELL_MARGIN')
        self.table_row_count = config['CITY_SCOPE'].getint('TABLE_ROWS')
        self.table_column_count = config['CITY_SCOPE'].getint('TABLE_COLS')
        self.origin_epsg = config['SETTINGS']['ORIGIN_EPSG']
        self.local_epsg = config['SETTINGS']['LOCAL_EPSG']
        self.table_rotation_spatial = self.calculate_rotation_metric_crs()

    def get_start_cell_origin(self):
        return self.start_cell_origin

    def get_projected_start_cell_origin(self):
        origin_spatial_coords = self.get_reprojected_origin()
        if not self.table_flipped:
            return origin_spatial_coords

        # else: shift the table origin from the SouthEast corner to the NorthWest corner
        return self.get_flipped_origin(origin_spatial_coords)

    def get_table_rotation(self):
        return 360 - self.table_rotation_lat_lon

    def get_table_rotation_spatial_crs(self):
        return self.table_rotation_spatial

    def get_table_cell_size(self):
        return self.table_cell_size

    def get_table_cell_margin(self):
        return self.table_cell_margin

    def get_table_row_count(self):
        return self.table_row_count

    def get_table_column_count(self):
        return self.table_column_count

    def get_reprojected_origin(self):
        point = [self.start_cell_origin.x, self.start_cell_origin.y]
        city_io_projection = pyproj.Proj("+init=" + self.origin_epsg)
        local_projection = pyproj.Proj("+init=" + self.local_epsg)
        projected_x, projected_y = pyproj.transform(city_io_projection, local_projection, point[0], point[1])

        return Point(projected_x, projected_y)

    # returns the opposite corner of the grid (SE->NW)
    def get_flipped_origin(self, origin_spatial_coords):
        table_width = self.get_table_column_count() * self.table_cell_size
        table_height = self.get_table_row_count() * self.table_cell_size
        diagonal = math.sqrt(pow(table_width, 2) + pow(table_height, 2))
        diagonal_angle = math.degrees(math.atan(table_width / table_height))
        angle_diagonal_to_x_axis = diagonal_angle - self.get_table_rotation_spatial_crs()
        delta_x = math.sin(math.radians(angle_diagonal_to_x_axis)) * diagonal
        delta_y = math.cos(math.radians(angle_diagonal_to_x_axis)) * diagonal
        flipped_x = origin_spatial_coords.x - delta_x
        flipped_y = origin_spatial_coords.y + delta_y

        return Point(flipped_x, flipped_y)

    def deg_to_rad(self, deg):
        return deg * math.pi / 180

    def rad_to_deg(self, rad):
        return rad * 180 / math.pi

    # logic from https://github.com/doorleyr/grid_geojson/commit/df321e7e5fe1cf389a24fcde57cadee8591f1c92#diff-a95911d0e1834f67b5fab2dca32cc329
    def calculate_rotation_metric_crs(self):
        return 34
        # earth_radius_m = 6.371e6
        # origin = self.start_cell_origin
        # bearing = (90 - self.table_rotation_lat_lon + 360) % 360
        # projection = pyproj.Proj("+init=" + self.local_epsg)
        # wgs = pyproj.Proj("+init=" + self.origin_epsg)  # todo rename as global epsg
        # cell_size = self.table_cell_size
        # ratio_grid_earth = (cell_size * self.table_column_count) / earth_radius_m
        # origin_latitude_rad = self.deg_to_rad(origin.y)
        # origin_longitude_rad = self.deg_to_rad(origin.x)
        # bearing_rad = self.deg_to_rad(bearing)
        #
        # # calculate position of the top right corner of the grid
        # top_right_latitude_rad = math.asin(math.sin(origin_latitude_rad) * math.cos(ratio_grid_earth)
        #                                    + (math.cos(origin_latitude_rad)
        #                                       * math.sin(ratio_grid_earth)
        #                                       * math.cos(bearing_rad)))
        #
        # top_right_longitude_rad = origin_longitude_rad + math.atan2(
        #     math.sin(bearing_rad) * math.sin(ratio_grid_earth) * math.cos(origin_latitude_rad),
        #     math.cos(ratio_grid_earth) - math.sin(origin_latitude_rad) * math.sin(top_right_latitude_rad)
        # )
        # # convert longitude latitude from rad to degree
        # top_right_lon_lat = {'lon': self.rad_to_deg(top_right_longitude_rad),
        #                      'lat': self.rad_to_deg(top_right_latitude_rad)}
        #
        # # reprojected coordinates of the 2 points into local, spatial system
        # top_left_xy = pyproj.transform(wgs, projection, origin.x,
        #                                origin.y)
        # top_right_xy = pyproj.transform(wgs, projection, top_right_lon_lat['lon'],
        #                                 top_right_lon_lat['lat'])
        # # now we have the top two points in a spatial system,
        # # we can calculate the rest of the points
        # dydx = (top_right_xy[1] - top_left_xy[1]) / (top_right_xy[0] - top_left_xy[0])
        # theta = math.atan((dydx))
        #
        # return self.rad_to_deg(theta)
