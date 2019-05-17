import pyproj
import json
import configparser

config = configparser.ConfigParser()
config.read('config.ini')
wgs84 = pyproj.Proj("+init=" + config['SETTINGS']['GLOBAL_EPSG'])
espg = pyproj.Proj("+init=" + config['SETTINGS']['LOCAL_EPSG'])


def open_geojson(path):
    with open(path) as f:
        return json.load(f)


# gets the path for the reprojected json
def get_projected_json_path(original_json_path):
    if original_json_path.endswith('.geojson'):
        return original_json_path[:-8] + '_wgs84' + '.json'
    raise NameError('Invalid path to original json. Must end on ".geojson"')


# reprojects a point to WGS84
def reproject_point_to_wgs84(point):
    projected_x, projected_y = pyproj.transform(espg, wgs84, point[0], point[1])

    return projected_x, projected_y


# reprojects a point to local hamburg epsg
def reproject_point_to_hamburg_epsg(point):
    projected_x, projected_y = pyproj.transform(wgs84, espg, point[0], point[1])

    return projected_x, projected_y


def reproject_geojson_epsg_to_wgs(geojson):
    features = geojson['features']

    for feature in features:
        coordinates = feature['geometry']['coordinates']
        for point in coordinates[0]:
            projected_x, projected_y = reproject_point_to_wgs84(point)

            # replace coordinates with projected ones in long, lat format
            point[0] = projected_x
            point[1] = projected_y

    projected_features = features
    geojson['features'] = projected_features
    #print(geojson)

    return geojson

