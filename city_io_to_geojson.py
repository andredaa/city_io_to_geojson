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

    # filter grid of cells for subgrids
    grid_of_outer_cells = get_grid_of_outer_cells(grid_of_cells)
    grid_of_inner_cells = get_grid_of_inner_cells(grid_of_cells)
    grid_of_margins = get_grid_of_margins(grid_of_cells)

    # create geojsons
    geo_json_outer_cells = create_geo_json_for_cells(grid_of_outer_cells)
    geo_json_inner_cells = create_geo_json_for_cells(grid_of_inner_cells)
    geo_json_cell_margins = create_geo_json_for_margins(grid_of_margins, table.get_table_rotation())

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

    # cell margins
    with open('./resulting_jsons/margins/geojson_' + config['SETTINGS']['LOCAL_EPSG'] + '.json', 'wb') as f:
        json.dump(geo_json_cell_margins, f)

    geo_json_cell_margins_global_projection = reproject.reproject_geojson_local_to_global(geo_json_cell_margins)
    with open('./resulting_jsons/margins/geojson_' + config['SETTINGS']['OUTPUT_EPSG'] + '.json', 'wb') as f:
        json.dump(geo_json_cell_margins_global_projection, f)


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
                table.get_table_rotation(),
                table.get_table_cell_size(),
                cell_id,
                table.get_table_cell_margin()
            )

            grid_of_cells.append(grid_cell)

    return grid_of_cells


def get_grid_of_outer_cells(grid_of_cells):
    grid_of_outer_cells = []
    for cell in grid_of_cells:
        outer_cell = cell.get_outer_cell()
        grid_of_outer_cells.append(outer_cell)

    return grid_of_outer_cells


def get_grid_of_inner_cells(grid_of_cells):
    grid_of_inner_cells = []
    for cell in grid_of_cells:
        inner_cell = cell.get_inner_cell()
        grid_of_inner_cells.append(inner_cell)

    return grid_of_inner_cells


def get_grid_of_margins(grid_of_cells):
    grid_of_margins = []
    for cell in grid_of_cells:
        margins = cell.get_margins()
        for margin in margins:
            grid_of_margins.append(margin)

    return grid_of_margins


# creates a geojson
def create_geo_json_for_cells(list_of_cells):
    geo_json = {
        "type": "FeatureCollection",
        "features": [
        ]
    }
    for cell in list_of_cells:
        # create outer cells geojson
        cell_coordinates = []
        for point in cell.get_polygon_coord():
            cell_coordinates.append(point)
        cell_content = get_cell_content(cell_coordinates, cell.get_cell_id(), cell.get_table_rotation())
        geo_json['features'].append(cell_content)

    return geo_json


# creates a geojson
def create_geo_json_for_margins(list_of_margins, table_rotation):
    geo_json = {
        "type": "FeatureCollection",
        "features": [
        ]
    }
    for margin in list_of_margins:
        # create outer cells geojson
        cell_coordinates = []
        for point in margin.get_polygon_coord():
            cell_coordinates.append(point)
        cell_content = get_cell_content(cell_coordinates, margin.get_cell_id(), table_rotation, margin.get_margin_id())
        geo_json['features'].append(cell_content)

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
            "color": '#000000',
            "base_height": 0,
            "height": 0
        },
        "id": cell_id
    }

    if margin_id:
        cell_content['properties'].update({"margin_id": margin_id})

    return cell_content


if __name__ == "__main__":
    # execute only if run as a script
    create_table()
