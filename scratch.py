#
# start with empty grid
#
# iterate over all cells in meta grid
#
# get location of cell
# 	-> if exists in old_cells
# 			-> get content
# 		else:
# 			fill grid with [0,0] for new cells

import json
import os
import urllib

import requests
from shapely.geometry import Polygon


def load_new_meta_grid():
    cwd = os.path.dirname(os.path.realpath(__file__))
    with open(cwd + '/resulting_jsons/geojson_meta_grid_new.json') as f:
        geojson = json.load(f)

    return geojson['features']


def get_old_meta_grid_polygons():
    cwd = os.path.dirname(os.path.realpath(__file__))
    with open(cwd + '/old_grid/meta_grid.json') as f:
        geojson = json.load(f)

    polygon_list = []
    for cell in geojson['features']:
        polygon = Polygon(cell['geometry']['coordinates'][0])
        polygon_list.append(polygon)

    return polygon_list


def get_current_grid():
    cwd = os.path.dirname(os.path.realpath(__file__))
    with open(cwd + '/old_grid/grid.json') as f:
        grid = json.load(f)

    return grid


if __name__ == '__main__':
    new_grid = []
    matched_cells = []
    old_polygon_list = get_old_meta_grid_polygons()
    current_grid = get_current_grid()
    matching_polygon_id = None

    for cell in load_new_meta_grid():
        cell_id = cell['id']
        print(cell_id)
        polygon = Polygon(cell['geometry']['coordinates'][0])

        grid_cell_content = [0, 0]
        # overwrite cell_content with value from current grid, if corresponding cell found
        for old_polygon_id, old_polygon in enumerate(old_polygon_list):
            # print(polygon.bounds, old_polygon.bounds)
            if polygon.intersects(old_polygon):
                if polygon.intersection(old_polygon).area >= 0.9 * polygon.area:
                    print("matching cell found")
                    matching_polygon_id = old_polygon_id
                    grid_cell_content = current_grid[matching_polygon_id]
                    print("grid cell content", grid_cell_content)
                    matched_cells.append(cell)
                    break
        new_grid.append(grid_cell_content)
        #print(old_polygon_id, grid_cell_content, current_grid[old_polygon_id])
        # if (old_polygon_id == 3496):
         #   exit()
        # remove matched old polygons from list


    test_geo_json = {
        "type": "FeatureCollection",
        "features": matched_cells
    }

    with open('./resulting_jsons/geojson_' + 'intersection_old_new' + '.json', 'w', newline='') as f:
        json.dump(test_geo_json, f)  # , sort_keys=True, indent=4)

    with open('./resulting_jsons/replacement_grid' + '.json', 'w', newline='') as f:
        json.dump(new_grid, f)  # , sort_keys=True, indent=4)

    print(new_grid)
