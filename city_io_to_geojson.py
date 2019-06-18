#!/usr/bin/env python2.7

import CityScopeTable
import GridCell
import json
import configparser
import reproject
from shapely.geometry import Polygon, polygon
from shapely_geojson import dumps, Feature, FeatureCollection

def get_color_for_cell_type(cell_type):
    colors_for_type = {
        0 : '# 373f51', # street
        1 : '# 002dd5',# residential low
        2 : '# 008dd5',# residential high
        3 : '# e43f0f',# working low
        4 : '# f51476',# working high
        5 : '# 000000',# unknown
        6 : '# 000000',# unknown
    }

    return colors_for_type[cell_type]


def create_grid_of_cells(table):
    # create a list of GridCell objects for all cells in grid
    grid_of_cells = []
    for row in range(table.get_table_row_count()):
        for column in range(table.get_table_column_count()):
            cell_id = row * table.get_table_column_count() + column
            cell_content = table.get_result()['grid'][cell_id]
            cell_type = cell_content[0]
            cell_rotation = cell_content[1]

            # get coordinates of the current cell's origin
            if (row == 0 and column == 0):
                cell_origin = table.get_projected_start_cell_origin()
            # in highest row of grid - move towards the right
            elif (row == 0 and column != 0):
                cell_origin = grid_of_cells[(column - 1)].get_upper_right_corner()
            # the origin of the cell is always the equal to the lower left corner of the cell above
            else:
                cell_origin = grid_of_cells[cell_id - table.get_table_column_count()].get_lower_left_corner()

            cell = GridCell.GridCell(
                cell_origin,
                table.get_table_rotation(),
                table.get_table_cell_size(),
                cell_id,
                cell_type,
                cell_rotation,
            )

            grid_of_cells.append(cell)

    return grid_of_cells


def get_cell_polygon_coord(cell):
    return [
        [
            cell.get_origin().x,
            cell.get_origin().y
        ],
        [
            cell.get_upper_right_corner().x,
            cell.get_upper_right_corner().y
        ],
        [
            cell.get_lower_right_corner().x,
            cell.get_lower_right_corner().y
        ],
        [
            cell.get_lower_left_corner().x,
            cell.get_lower_left_corner().y
        ],
        # coordinates of a polygon need to form a closed linestring
        [
            cell.get_origin().x,
            cell.get_origin().y
        ],
    ]


def create_table_json(grid_of_cells):

    features = []
    for cell in grid_of_cells:
        # filter out empty or irrelevant cells
        coordinates = []
        for point in get_cell_polygon_coord(cell):
            coordinates.append(point)

        cell_polygon = Polygon(coordinates)
        polygon.orient(cell_polygon)

        feature = Feature(cell_polygon, properties={
                          "id": cell.get_cell_id(),
                          "type": cell.get_cell_type(),
                          "rotation": cell.get_cell_rotation(),
                          "color": get_color_for_cell_type(cell.get_cell_type())
                      },
                  #  TODO is the needed? then add it later
                  #    id = {cell.get_cell_id()}
                          )
        features.append(feature)

       # print(dumps(feature, indent= 2))
       #  exit()

  #  print(type({dumps(FeatureCollection(features))}))
   # print({dumps(FeatureCollection(features))})
    #exit()

    return dumps(FeatureCollection(features), indent=2)


# collects the data from city io, transforms into a geojson and saves that geojson as input for the noise calculation
def convert_data_from_city_io():
    config = configparser.ConfigParser()
    config.read('config.ini')

    city_scope_address = config['CITY_SCOPE']['TABLE_URL_INPUT']
    # if the table origin is flipped to teh southeast, instead of regular northwest
    table_flipped = config['CITY_SCOPE'].getboolean('TABLE_FLIPPED')

    # dynamic input data from designer
    table = CityScopeTable.CityScopeTable(city_scope_address, table_flipped)
    grid_of_cells = create_grid_of_cells(table)
    geo_json_table_local_projection = create_table_json(grid_of_cells)

    # save geojsons
    with open('./resulting_jsons/geojson_' + config['SETTINGS']['LOCAL_EPSG'] + '.json', 'wb') as f:
        json.dump(geo_json_table_local_projection, f)

    geo_json_table_global_projection = reproject.reproject_geojson_local_to_global(geo_json_table_local_projection)
    with open('./resulting_jsons/geojson_' + config['SETTINGS']['OUTPUT_EPSG'] + '.json', 'wb') as f:
        json.dump(geo_json_table_global_projection, f)


if __name__ == "__main__":
    # execute only if run as a script
    convert_data_from_city_io()