import pyproj
import json
import configparser
import os

config = configparser.ConfigParser()
file_path = dir_path = os.path.dirname(os.path.realpath(__file__))
config.read(file_path + '/config.ini')
global_epsg = config['SETTINGS']['OUTPUT_EPSG']
local_epsg = config['SETTINGS']['LOCAL_EPSG']


# gets the path for the reprojected json
def get_projected_json_path(original_json_path):
    if original_json_path.endswith('.geojson'):
        return original_json_path[:-8] + '_wgs84' + '.json'
    raise NameError('Invalid path to original json. Must end on ".geojson"')


# receives a geojson, reprojects it and returns the reprojected geojson
def reproject_geojson_local_to_global(local_geojson):
    local_prj = pyproj.Proj("+init=" + local_epsg)
    global_prj = pyproj.Proj("+init=" + global_epsg)

    features = local_geojson['features']
    feature_length = len(features[0]['geometry']['coordinates'][0])

    # creates a list of coordinates used in the local_geojson
    local_coords = []
    for feature in features:
        coordinates = feature['geometry']['coordinates'][0]
        for point in coordinates:
            local_coords.append((point[0], point[1]))
    
    # reprojects local coords and updates features with reprojected coords
    point_counter = 0
    for gc in pyproj.itransform(local_prj, global_prj, local_coords):
        feature_num = int(point_counter / feature_length)
        features[feature_num]['geometry']['coordinates'][0][point_counter % feature_length] = gc

        point_counter += 1

    projected_features = features
    local_geojson['features'] = projected_features

    return local_geojson
