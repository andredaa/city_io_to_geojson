#!/usr/bin/env python3.6.7

import CityScopeTable
import GridCell
import json
import configparser
import reproject
import random
import os
from shapely.geometry import shape, Point


# returns a shapely object containing a MultiPolygon in form of the designable area of the project site
def get_design_area_shape():
    cwd = os.path.dirname(os.path.realpath(__file__))
    with open(cwd + '/designable_area.json') as f:
        geojson = json.load(f)
        return shape(geojson['features'][0]['geometry'])


# collects the table specs and creates geojsons in local and global projections
# geojsons containing coordinates are created for the outer_cell, inner_cell and margins of each grid_cell
# sets interactive_id for cells inside design area
def set_interactive_cell_id(grid_of_cells):
    design_area = get_design_area_shape()
    design_grid = []
    interactive_id = 0

    for cell in grid_of_cells:
        if design_area.intersects(shape(cell.outer_cell.get_the_geom())):
            cell.set_interactive_id(interactive_id)
            design_grid.append(cell)
            interactive_id += 1


def create_table():
    # dynamic input data from designer
    table = CityScopeTable.CityScopeTable()
    grid_of_cells = create_grid_of_cells(table)

    set_interactive_cell_id(grid_of_cells)

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
    config = configparser.ConfigParser()
    config.read('config.ini')

    geo_json = {
        "type": "FeatureCollection",
        "features": [
        ]
    }
    for cell in grid_of_cells:
        print(cell.cell_id)
        inner_cell = cell.get_inner_cell()
        # add inner cells
        inner_cell_coordinates = []
        for point in inner_cell.get_polygon_coord():
            inner_cell_coordinates.append(point)
        cell_content = get_cell_content(inner_cell_coordinates, cell.get_cell_id(), cell.interactive_id)
        geo_json['features'].append(cell_content)

        # add margins
        # if margins
        if cell.cell_margin > 0:
            print("margin")
            margins = cell.get_margins()
            for margin in margins:
                margin_coordinates = []
                for point in margin.get_polygon_coord():
                    margin_coordinates.append(point)
                margin_content = get_cell_content(margin_coordinates, cell.get_cell_id(), cell.interactive_id,
                                                  margin.get_margin_id())
                geo_json['features'].append(margin_content)

    return geo_json


def get_cell_content(coordinates, cell_id, interactive_id, margin_id=None):


    cell_content = {
        "type": "Feature",
        "geometry": {
            "type": "Polygon",
            "coordinates": [coordinates]
        },
        "properties": {
            "type": 0,
            "height": 10,
            "color": "#A9A9A9",
            "interactive_id": interactive_id,
            "interactive": (interactive_id is not None)
        },
        "id": cell_id
    }

    if margin_id is not None:
        cell_content['properties'].update({"margin_id": margin_id, "color": '#000000'})

    return cell_content


def get_height(is_margin):
    if is_margin:
        return 0

    return random.randrage(5, 100)


def get_color(is_margin):
    if is_margin:
        return get_color_codes_reds()[random.randrange(len(get_color_codes_reds()))]

    return get_color_codes_blues()[random.randrange(len(get_color_codes_blues()))]


def get_color_codes_blues():
    return [
        '#E6E6FA',
        '#B0E0E6',
        '#ADD8E6',
        '#87CEFA',
        '#87CEEB',
        '#00BFFF',
        '#B0C4DE',
        '#1E90FF',
        '#6495ED',
        '#4682B4',
        '#5F9EA0',
        '#7B68EE',
        '#6A5ACD',
        '#483D8B',
        '#4169E1',
        '#0000FF',
        '#0000CD',
        '#00008B',
        '#000080',
        '#191970',
        '#8A2BE2',
        '#4B0082',
    ]

def get_color_codes_reds():
    return [
    '#FA8072',
    '#E9967A',
    '#F08080',
    '#CD5C5C',
    '#DC143C',
    '#B22222',
    '#FF0000',
    '#8B0000',
    '#800000',
    '#FF6347',
    '#FF4500',
    '#DB7093',
]

if __name__ == "__main__":
    # execute only if run as a script
    create_table()
