#!/usr/bin/env python2.7

import CityScopeTable
import GridCell
import json
import configparser
import reproject


def get_data_from_config():
    config = configparser.ConfigParser()
    config.read('config.ini')
    create_table()

    return json.load('./resulting_jsons/geojson_' + config['SETTINGS']['LOCAL_EPSG'] + '.json')


# collects the table specs and creates geojsons in local and global projections
# geojsons containing coordinates are created for the outer_cell, inner_cell and margins of each grid_cell
def create_table():
    config = configparser.ConfigParser()
    config.read('config.ini')

    # dynamic input data from designer
    table = CityScopeTable.CityScopeTable()
    grid_of_cells = create_grid_of_cells(table)

    # create geojsons for inner and outer cells
    geo_json_outer_cells = create_geo_json(grid_of_cells, False)
    geo_json_inner_cells = create_geo_json(grid_of_cells, True)

    # save geojsons
    # outer cells
    with open('./resulting_jsons/outer_cells/geojson_' + config['SETTINGS']['LOCAL_EPSG'] + '.json', 'wb') as f:
        json.dump(geo_json_outer_cells, f)

    geo_json_table_global_projection = reproject.reproject_geojson_local_to_global(geo_json_outer_cells)
    with open('./resulting_jsons/outer_cells/geojson_' + config['SETTINGS']['OUTPUT_EPSG'] + '.json', 'wb') as f:
        json.dump(geo_json_table_global_projection, f)

    # inner cells
    with open('./resulting_jsons/inner_cells/geojson_' + config['SETTINGS']['LOCAL_EPSG'] + '.json', 'wb') as f:
        json.dump(geo_json_inner_cells, f)

    geo_json_inner_cells_global_projection = reproject.reproject_geojson_local_to_global(geo_json_inner_cells)
    with open('./resulting_jsons/inner_cells/geojson_' + config['SETTINGS']['OUTPUT_EPSG'] + '.json', 'wb') as f:
        json.dump(geo_json_inner_cells_global_projection, f)


# Creates a grid of GridCells
def create_grid_of_cells(table):
    # create a list of GridCell objects for all cells in grid
    grid_of_cells = []
    for row in range(table.get_table_row_count()):
        for column in range(table.get_table_column_count()):
            cell_id = row * table.get_table_column_count() + column

            # get coordinates of the current cell's origin
            if (row == 0 and column == 0):
                cell_origin = table.get_projected_start_cell_origin()
            # in highest row of grid - move towards the right
            elif (row == 0 and column != 0):
                neighbor_cell = grid_of_cells[(column - 1)]
                cell_origin = neighbor_cell.get_outer_cell().get_upper_right_corner()
            # the origin of the cell is always the equal to the lower left corner of the cell above
            else:
                neighbor_cell = grid_of_cells[cell_id - table.get_table_column_count()]
                cell_origin = neighbor_cell.get_outer_cell().get_lower_left_corner()

            grid_cell = GridCell.GridCell(
                cell_origin,
                table.get_table_rotation(),
                table.get_table_cell_size(),
                cell_id,
                table.get_table_cell_margin()
            )

            grid_of_cells.append(grid_cell)

    return grid_of_cells

# creates a geojson
def create_geo_json(grid_of_cells, inner_cells=False):
    geo_json = {
        "type": "FeatureCollection",
        "features": [
        ]
    }

    for grid_cell in grid_of_cells:
        if inner_cells:
            cell = grid_cell.get_inner_cell()
        else:
            cell = grid_cell.get_outer_cell()

        # create list of coordinates for cell
        coordinates = []
        for point in cell.get_cell_polygon_coord():
            coordinates.append(point)

        cell_content = {
            "type": "Feature",
            "geometry": {
                "type": "Polygon",
                "coordinates": [coordinates]
            },
            "properties": {
                "id": cell.get_cell_id(),
                "type": 0,
                "rotation": cell.get_table_rotation(),
                "color": '#000000',
                "base_height": 0,
                "height": 0
            },
            "id": cell.get_cell_id()
        }

        geo_json['features'].append(cell_content)

    return geo_json


if __name__ == "__main__":
    # execute only if run as a script
    create_table()