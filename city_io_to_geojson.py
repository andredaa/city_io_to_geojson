#!/usr/bin/env python2.7

import CityScopeTable
import GridCell
import json
import configparser
import reproject
import project_properties


def create_grid_of_cells(table):
    # create a list of GridCell objects for all cells in grid
    grid_of_cells = []
    for row in range(table.get_table_row_count()):
        for column in range(table.get_table_column_count()):
            cell_id = row * table.get_table_column_count() + column
            cell_content = [1, 1]
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


# order of coordinates following right hand rule
def get_cell_polygon_coord(cell):
    return [
        [
            cell.get_origin().x,
            cell.get_origin().y
        ],
        [
            cell.get_lower_left_corner().x,
            cell.get_lower_left_corner().y
        ],
        [
            cell.get_lower_right_corner().x,
            cell.get_lower_right_corner().y
        ],
        [
            cell.get_upper_right_corner().x,
            cell.get_upper_right_corner().y
        ],
        # coordinates of a polygon need to form a closed linestring
        [
            cell.get_origin().x,
            cell.get_origin().y
        ],
    ]


def create_table_json(grid_of_cells):
    geo_json = {
        "type": "FeatureCollection",
        "features": [
        ]
    }

    for cell in grid_of_cells:
        # filter out empty or irrelevant cells
        coordinates = []
        for point in get_cell_polygon_coord(cell):
            coordinates.append(point)

        cell_content = {
            "type": "Feature",
            "geometry": {
                "type": "Polygon",
                "coordinates": [coordinates]
            },
            "properties": {
                "id": cell.get_cell_id(),
                "type": cell.get_cell_type(),
                "rotation": cell.get_cell_rotation(),
                "color": project_properties.get_color_for_cell_type(cell.get_cell_type()),
                "base_height": project_properties.get_base_height_for_cell_type(cell.get_cell_type()),
                "height": project_properties.get_height_for_cell_type(cell.get_cell_type())
            },
            "id": cell.get_cell_id()
        }

        geo_json['features'].append(cell_content)

    return geo_json


# collects the data from city io, transforms into a geojson and saves that geojson as input for the noise calculation
def create_table():
    config = configparser.ConfigParser()
    config.read('config.ini')

    # dynamic input data from designer
    table = CityScopeTable.CityScopeTable()
    grid_of_cells = create_grid_of_cells(table)
    geo_json_table_local_projection = create_table_json(grid_of_cells)


    # save geojsons
    with open('./resulting_jsons/geojson_' + config['SETTINGS']['LOCAL_EPSG'] + '.json', 'wb') as f:
        json.dump(geo_json_table_local_projection, f)

    geo_json_table_global_projection = reproject.reproject_geojson_local_to_global(geo_json_table_local_projection)
    with open('./resulting_jsons/geojson_' + config['SETTINGS']['OUTPUT_EPSG'] + '.json', 'wb') as f:
        json.dump(geo_json_table_global_projection, f)


def get_data_from_city_io():
    config = configparser.ConfigParser()
    config.read('config.ini')
    create_table()

    return json.load('./resulting_jsons/geojson_' + config['SETTINGS']['LOCAL_EPSG'] + '.json')


if __name__ == "__main__":
    # execute only if run as a script
    create_table()