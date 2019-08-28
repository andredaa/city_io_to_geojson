#!/usr/bin/env python3.6.7

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

    geo_json_local_projection = create_geo_json(grid_of_cells)

    # debugging only: save local geojson
    # with open('./resulting_jsons/geojson_' + 'local_projection' + '.json', 'wb') as f:
    #    json.dump(geo_json_local_projection, f) # , sort_keys=True, indent=4)

    # save reprojected geojson
    geo_json_global_projection = reproject.reproject_geojson_local_to_global(geo_json_local_projection)
    with open('./resulting_jsons/geojson_' + 'global_projection' + '.json', 'w', newline='') as f:
        json.dump(geo_json_global_projection, f) # , sort_keys=True, indent=4)


# Creates a grid of GridCells
def create_grid_of_cells(table):
    # create a list of GridCell objects for all cells in grid
    grid_of_cells = []
    for row in range(table.get_table_row_count()):
        for column in range(table.get_table_column_count()):
            cell_id = row * table.get_table_column_count() + column

            # get coordinates of the current cell's origin
            if row == 0 and column == 0:
                cell_origin = table.get_projected_start_cell_origin()
            # in highest row of grid - move towards the right
            elif row == 0 and column != 0:
                neighbor_cell = grid_of_cells[(column - 1)]
                cell_origin = neighbor_cell.get_outer_cell().get_upper_right_corner()
            # the origin of the cell is always the equal to the lower left corner of the cell above
            else:
                neighbor_cell = grid_of_cells[cell_id - table.get_table_column_count()]
                cell_origin = neighbor_cell.get_outer_cell().get_lower_left_corner()

            grid_cell = GridCell.GridCell(
                cell_origin,
                table.get_table_rotation_spatial_crs(),
                table.get_table_cell_size(),
                cell_id,
                table.get_table_cell_margin()
            )

            grid_of_cells.append(grid_cell)

    return grid_of_cells


# creates a geojson
def create_geo_json(grid_of_cells):
    geo_json = {
        "type": "FeatureCollection",
        # todo put crs crs
        "features": [
        ]
    }
    for cell in grid_of_cells:
        inner_cell = cell.get_inner_cell()
        # add inner cells
        inner_cell_coordinates = []
        for point in inner_cell.get_polygon_coord():
            inner_cell_coordinates.append(point)
        cell_content = get_cell_content(inner_cell_coordinates, cell.get_cell_id(), cell.get_table_rotation)
        geo_json['features'].append(cell_content)

        # add margins
        margins = cell.get_margins()
        for margin in margins:
            margin_coordinates = []
            for point in margin.get_polygon_coord():
                margin_coordinates.append(point)
            margin_content = get_cell_content(margin_coordinates, cell.get_cell_id(), cell.get_table_rotation,
                                              margin.get_margin_id())
            geo_json['features'].append(margin_content)

    return geo_json


def get_cell_content(coordinates, cell_id, rotation, margin_id=None):
    cell_content = {
        "type": "Feature",
        "geometry": {
            "type": "Polygon",
            "coordinates": [coordinates]
        },
        "properties": {
            "id": cell_id,
            "type": 0,
            "rotation": rotation,
            "color": '#FFFFFF',
            "base_height": 0,
            "height": 0
        },
        "cell_id": cell_id
    }

    if margin_id is not None:
        cell_content['properties'].update({"margin_id": margin_id, "color": '#000000'})

    return cell_content


if __name__ == "__main__":
    # execute only if run as a script
    create_table()
