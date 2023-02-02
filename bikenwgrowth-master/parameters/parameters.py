# PARAMETERS
# These are values to loop through for different runs
poi_source = "grid" # railwaystation, grid
prune_measure = "betweenness" # betweenness, closeness, random

SERVER = False # Whether the code runs on the server (important to avoid parallel job conflicts)


# SEMI-CONSTANTS
# These values should not be changed, unless the analysis shows we need to

smallcitythreshold = 46 # cities smaller or equal than this rank in the city list will be treated as "small" and get full calculations
prune_quantiles = [x/40 for x in list(range(1, 41))] # The quantiles where the GT should be pruned using the prune_measure





#prune_measures = {"betweenness": "Bq", "closeness": "Cq", "random": "Rq"}
prune_measures = {"betweenness": "Bq"}



networktypes = ["biketrack", "carall", "bikeable", "biketrackcarall", "biketrack_onstreet", "bikeable_offstreet"] # Existing infrastructures to analyze
#networktypes = ["carall"] # Existing infrastructures to analyze

networktypesdata = ["biketrack","bikeable", "biketrackcarall"]

attrlist = ['length_attr','bcount_attr','pop_den_attr','bcount_pop_den_attr']

#attrlist = ['length']


# 02
gridl = 1707 # in m, for generating the grid
# https://en.wikipedia.org/wiki/Right_triangle#Circumcircle_and_incircle
# 2*0.5 = a+a-sqrt(2)a   |   1 = a(2-sqrt2)   |   a = 1/(2-sqrt2) = 1.707
# This leads to a full 500m coverage when a (worst-case) square is being triangulated
bearingbins = 72 # number of bins to determine bearing. e.g. 72 will create 5 degrees bins
poiparameters = {"railwaystation":{'railway':['station','halt']}#, # should maybe also add: ["railway"!~"entrance"], but afaik osmnx is not capable of this: https://osmnx.readthedocs.io/en/stable/osmnx.html?highlight=geometries_from_polygon#osmnx.geometries.geometries_from_polygon
                 #"busstop":{'highway':'bus_stop'}
                }

# 04
buffer_walk = 500 # Buffer in m for coverage calculations. (How far people are willing to walk)
numnodepairs = 500 # Number of node pairs to consider for random sample to calculate directness (O(numnodepairs^2), so better not go over 1000)

#05
nodesize_grown = 7.5
plotparam = {"bbox": (1280,1280),
			"dpi": 96,
			"carall": {"width": 0.5, "edge_color": '#999999'},
			# "biketrack": {"width": 1.25, "edge_color": '#2222ff'},
            "biketrack": {"width": 1, "edge_color": '#000000'},
			"biketrack_offstreet": {"width": 0.75, "edge_color": '#00aa22'},
			"bikeable": {"width": 0.75, "edge_color": '#222222'},
			# "bikegrown": {"width": 6.75, "edge_color": '#ff6200', "node_color": '#ff6200'},
			# "highlight_biketrack": {"width": 6.75, "edge_color": '#0eb6d2', "node_color": '#0eb6d2'},
            "bikegrown": {"width": 3.75, "edge_color": '#0eb6d2', "node_color": '#0eb6d2'},
            "highlight_biketrack": {"width": 3.75, "edge_color": '#2222ff', "node_color": '#2222ff'},
			"highlight_bikeable": {"width": 3.75, "edge_color": '#222222', "node_color": '#222222'},
			"poi_unreached": {"node_color": '#ff7338', "edgecolors": '#ffefe9'},
			"poi_reached": {"node_color": '#0b8fa6', "edgecolors": '#f1fbff'},
			"abstract": {"edge_color": '#000000', "alpha": 0.75}
			}

plotparam_analysis = {
			"bikegrown": [{"linewidth": 1.5, "color": '#1f77b4', "linestyle": "solid", "label": "length"},
                         {"linewidth": 1.5, "color": '#ff7f0e', "linestyle": "solid", "label": "length_attr"},
                         {"linewidth": 1.5, "color": '#2ca02c', "linestyle": "solid", "label": "bcount_attr"},
                         {"linewidth": 1.5, "color": '#d62728', "linestyle": "solid", "label": "pop_den_attr"},
                         {"linewidth": 1.5, "color": '#9467bd', "linestyle": "solid", "label": "bcount_pop_den_attr"}],
			"bikegrown_abstract": {"linewidth": 3.75, "color": '#000000', "linestyle": "solid", "label": "Grown network (unrouted)", "alpha": 0.75},
			"mst": {"linewidth": 2, "color": '#0eb6d2', "linestyle": "dashed", "label": "MST"},
			"mst_abstract": {"linewidth": 2, "color": '#000000', "linestyle": "dashed", "label": "MST (unrouted)", "alpha": 0.75},
			"biketrack": {"linewidth": 1, "color": '#2222ff', "linestyle": "solid", "label": "Protected"},
			"bikeable": {"linewidth": 1, "color": '#222222', "linestyle": "dashed", "label": "Bikeable"},
			"constricted": {"linewidth": 3.75, "color": '#D22A0E', "linestyle": "solid", "label": "Street network"},
            "constricted_SI": {"linewidth": 2, "color": '#D22A0E', "linestyle": "solid", "label": "Street network"},
			"constricted_3": {"linewidth": 2, "color": '#D22A0E', "linestyle": "solid", "label": "Top 3%"},
			"constricted_5": {"linewidth": 2, "color": '#a3210b', "linestyle": "solid", "label": "Top 5%"},
			"constricted_10": {"linewidth": 2, "color": '#5a1206', "linestyle": "solid", "label": "Top 10%"},
            "bikegrown_betweenness": {"linewidth": 2.5, "color": '#0eb6d2', "linestyle": "solid", "label": "Betweenness"},
            "bikegrown_closeness": {"linewidth": 2, "color": '#186C7A', "linestyle": "dashed", "label": "Closeness"},
            "bikegrown_random": {"linewidth": 1.5, "color": '#222222', "linestyle": "dotted", "label": "Random"}
			}

#constricted_parameternamemap = {"betweenness": "_metrics", "grid": "", "railwaystation": "_rail"}
constricted_parameternamemap = {"betweenness": "_metrics", "grid": ""}
constricted_plotinfo = {"title": ["Global Efficiency", "Local Efficiency", "Directness of LCC", "Spatial Clustering", "Anisotropy"]}
analysis_existing_rowkeys = {"bikeable": 0, "bikeable_offstreet": 1, "biketrack": 2, "biketrack_onstreet": 3, "biketrackcarall": 4, "carall": 5}


# CONSTANTS
# These values should be set once and not be changed

# 01
osmnxparameters = {'car30': {'network_type':'drive', 'custom_filter':'["maxspeed"~"^30$|^20$|^15$|^10$|^5$|^20 mph|^15 mph|^10 mph|^5 mph"]', 'export': True, 'retain_all': True},
                   'carall': {'network_type':'drive', 'custom_filter': None, 'export': True, 'retain_all': False},
                   'bike_cyclewaytrack': {'network_type':'bike', 'custom_filter':'["cycleway"~"track"]', 'export': False, 'retain_all': True},
                   'bike_highwaycycleway': {'network_type':'bike', 'custom_filter':'["highway"~"cycleway"]', 'export': False, 'retain_all': True},
                   'bike_designatedpath': {'network_type':'all', 'custom_filter':'["highway"~"path"]["bicycle"~"designated"]', 'export': False, 'retain_all': True},
                   'bike_cyclewayrighttrack': {'network_type':'bike', 'custom_filter':'["cycleway:right"~"track"]', 'export': False, 'retain_all': True},
                   'bike_cyclewaylefttrack': {'network_type':'bike', 'custom_filter':'["cycleway:left"~"track"]', 'export': False, 'retain_all': True},
                   'bike_cyclestreet': {'network_type':'bike', 'custom_filter':'["cyclestreet"]', 'export': False, 'retain_all': True},
                   'bike_bicycleroad': {'network_type':'bike', 'custom_filter':'["bicycle_road"]', 'export': False, 'retain_all': True},
                   'bike_livingstreet': {'network_type':'bike', 'custom_filter':'["highway"~"living_street"]', 'export': False, 'retain_all': True}
                  }  
# Special case 'biketrack': "cycleway"~"track" OR "highway"~"cycleway" OR "bicycle"~"designated" OR "cycleway:right=track" OR "cycleway:left=track" OR ("highway"~"path" AND "bicycle"~"designated") OR "cyclestreet" OR "highway"~"living_street"
# Special case 'bikeable': biketrack OR car30
# See: https://wiki.openstreetmap.org/wiki/Key:cycleway#Cycle_tracks
# https://wiki.openstreetmap.org/wiki/Tag:highway=path#Usage_as_a_universal_tag
# https://wiki.openstreetmap.org/wiki/Tag:highway%3Dliving_street
# https://wiki.openstreetmap.org/wiki/Key:cyclestreet


# 02
snapthreshold = 500 # in m, tolerance for snapping POIs to network

print("Loaded parameters.\n")
