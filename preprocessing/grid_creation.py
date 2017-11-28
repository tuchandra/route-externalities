import os
import json
import argparse
from math import ceil, floor

from geojson import Polygon, Feature, FeatureCollection, dump
from shapely.geometry import shape, Point

"""
Code adapted from answer to question here:
http://gis.stackexchange.com/questions/54119/creating-square-grid-polygon-shapefile-with-python
"""

SCALE = 3

def grid(outputGridfn, xmin, xmax, ymin, ymax, gridHeight, gridWidth, boundary):

    # check all floats
    xmin = float(xmin)
    xmax = float(xmax)
    ymin = float(ymin)
    ymax = float(ymax)
    gridWidth = float(gridWidth)
    gridHeight = float(gridHeight)

    # get rows
    rows = ceil((ymax - ymin) / gridHeight)
    # get columns
    cols = ceil((xmax - xmin) / gridWidth)

    # create grid cells
    countcols = 0
    features = []
    while countcols < cols:
        # set x coordinate for this column
        grid_x_left = xmin + (countcols * gridWidth)
        countcols += 1
        # reset count for rows
        countrows = 0
        while countrows < rows:
            # update y coordinate for this row
            grid_y_bottom = ymin + (countrows * gridHeight)
            countrows += 1
            # check if grid centroid contained in county boundary
            bottomleftcorner = (grid_x_left, grid_y_bottom)
            coords = [bottomleftcorner]
            # add other three corners of gridcell before closing grid with starting point again
            for i in [(0.001, 0), (0.001, 0.001), (0, 0.001), (0, 0)]:
                coords.append((bottomleftcorner[0] + i[1], bottomleftcorner[1] + i[0]))
            intersects = False
            for corner in coords[1:]:
                if boundary.contains(Point(corner)):
                    intersects = True
                    break
            if intersects:
                properties = {'rid': round(grid_y_bottom * 10**SCALE), 'cid': round(grid_x_left * 10**SCALE)}
                features.append(Feature(geometry=Polygon([coords]), properties=properties))

    with open(outputGridfn, 'w') as fout:
        dump(FeatureCollection(features), fout)

def main():
    """Generate grid for a GeoJSON json file passed on the command line."""

    parser = argparse.ArgumentParser()
    parser.add_argument("features_geojson", help="Path to GeoJSON with features to be gridded.")
    parser.add_argument("output_folder", help="Folder to contain output grid GeoJSONs.")
    args = parser.parse_args()

    with open(args.features_geojson, 'r', encoding = 'utf8') as fin:
        feature = json.load(fin)

    boundary = shape(feature["geometry"])
    bb = feature["bbox"]

    xmin = bb[0]  # most western point
    xmax = bb[2]  # most eastern point
    ymin = bb[1]  # most southern point
    ymax = bb[3]  # most northern point

    gridHeight = 0.001
    gridWidth = 0.001
    xmin = floor(xmin * 10**SCALE) / 10**SCALE
    ymax = ceil(ymax * 10**SCALE) / 10**SCALE

    grid("{0}_grid.geojson".format(os.path.join(args.output_folder, args.features_geojson)),
         xmin, xmax, ymin, ymax, gridHeight, gridWidth, boundary)


if __name__ == "__main__":
    main()