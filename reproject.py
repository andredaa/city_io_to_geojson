import pyproj
import json
import configparser
import os

config = configparser.ConfigParser()
file_path = dir_path = os.path.dirname(os.path.realpath(__file__))
config.read(file_path + '/config.ini')
global_epsg = config['SETTINGS']['OUTPUT_EPSG']
local_epsg = config['SETTINGS']['LOCAL_EPSG']


def open_geojson(path):
    with open(path) as f:
        return json.load(f)


# gets the path for the reprojected json
def get_projected_json_path(original_json_path):
    if original_json_path.endswith('.geojson'):
        return original_json_path[:-8] + '_wgs84' + '.json'
    raise NameError('Invalid path to original json. Must end on ".geojson"')


# reprojects a point
def reproject_point(current_epsg, new_epsg, point):
    current = pyproj.Proj("+init=" + current_epsg)
    new = pyproj.Proj("+init=" + new_epsg)
    projected_x, projected_y = pyproj.transform(current, new, point[0], point[1])

    return projected_x, projected_y

# reprojects a point to WGS84
def reproject_point_local_to_global(point):
    projected_x, projected_y = reproject_point(local_epsg, global_epsg, point)

    return projected_x, projected_y


# reprojects a point to local hamburg epsg
def reproject_point_global_to_local(point):
    projected_x, projected_y = reproject_point(global_epsg, local_epsg, point)

    return projected_x, projected_y

# receives a geojson, reprojects it and returns the reprojected geojson
def reproject_geojson_local_to_global(geojson):
    features = geojson['features']

    for feature in features:
        coordinates = feature['geometry']['coordinates']
        for point in coordinates[0]:
            projected_x, projected_y = reproject_point_local_to_global(point)

            # replace coordinates with projected ones in long, lat format
            point[0] = projected_x
            point[1] = projected_y

    projected_features = features
    geojson['features'] = projected_features

    return geojson

