# System
import copy
import csv
import sys
import os
import watermark
import pickle
import itertools
import random
import zipfile
from collections import defaultdict
import pprint
pp = pprint.PrettyPrinter(indent=4)
from tqdm.notebook import tqdm
import warnings
import shutil

# Math/Data
import math
import numpy as np
import pandas as pd
from sklearn import preprocessing
import statistics

# Network
import igraph as ig
import networkx as nx

# Plotting
import matplotlib.pyplot as plt
from matplotlib import cm
import matplotlib
from matplotlib.collections import PatchCollection
from matplotlib.ticker import MaxNLocator

# Geo
import osmnx as ox
ox.utils.config(timeout = 300, logs_folder = PATH["logs"], log_file = True)
import fiona
import shapely
from osgeo import gdal
from osgeo import osr

from haversine import haversine, haversine_vector
import pyproj
from shapely.geometry import Point, MultiPoint, LineString, Polygon, MultiLineString, MultiPolygon
import shapely.ops as ops
import geopandas as gpd
import geojson



     
# dict of placeid:placeinfo
# If a city has a proper shapefile through nominatim
# In case no (False), manual download of shapefile is necessary, see below
cities = {'copenhagen': {'nominatimstring': '', 'countryid': 'dnk', 'name': 'Copenhagen'}}

# Create city subfolders  

for subfolder in ["data", "plots", "plots_networks", "results", "exports", "exports_json", "videos"]:
    placepath = PATH[subfolder] + 'copenhagen' + "/"
    if not os.path.exists(placepath):
        os.makedirs(placepath)
        print("Successfully created folder " + placepath)

from IPython.display import Audio
sound_file = '../dingding.mp3'

print("Setup finished.\n")
