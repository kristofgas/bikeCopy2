#debug = False

#exec(open("../parameters/parameters.py").read())
#exec(open("../code/path.py").read())
#exec(open("../code/setupCPH.py").read())
#exec(open("../code/functions.py").read())

for placeid, placeinfo in tqdm(cities.items(), desc = "Cities"):
    if placeinfo["nominatimstring"] != '':
        location = ox.geocoder.geocode_to_gdf(placeinfo["nominatimstring"])
        location = fill_holes(extract_relevant_polygon(placeid, shapely.geometry.shape(location['geometry'][0])))
        if debug: # Draw location polygons and their holes
            try:
                color = cm.rainbow(np.linspace(0,1,len(location)))
                for poly,c in zip(location, color):
                    plt.plot(*poly.exterior.xy, c = c)
                    for intr in poly.interiors:
                        plt.plot(*intr.xy, c = "red")
            except:
                plt.plot(*location.exterior.xy)
            plt.show()
    else:
        # https://gis.stackexchange.com/questions/113799/how-to-read-a-shapefile-in-python
        shp = fiona.open(PATH["data"] + placeid + "/" + placeid + ".shp")
        first = next(iter(shp))
        location = shapely.geometry.shape(first['geometry'])
    
    Gs = {}
    for parameterid, parameterinfo in tqdm(osmnxparameters.items(), desc = "Networks", leave = False):
        for i in range(0,10): # retry
            try:
                Gs[parameterid] = ox.graph_from_polygon(location, 
                                       network_type = parameterinfo['network_type'],
                                       custom_filter = (parameterinfo['custom_filter']),
                                       retain_all = parameterinfo['retain_all'],
                                       simplify = False)
            except ValueError:
                Gs[parameterid] = nx.empty_graph(create_using = nx.MultiDiGraph)
                print(placeid + ": No OSM data for graph " + parameterid + ". Created empty graph.")
                break
            except ConnectionError or UnboundLocalError:
                print("ConnectionError or UnboundLocalError. Retrying.")
                continue
            except:
                print("Other error. Retrying.")
                continue
            break
        if parameterinfo['export']: ox_to_csv(Gs[parameterid], PATH["data"] + placeid + "/", placeid, parameterid)

    # Compose special cases biketrack, bikeable, biketrackcarall
    parameterid = 'biketrack'
    Gs[parameterid] = nx.compose_all([Gs['bike_cyclewaylefttrack'], Gs['bike_cyclewaytrack'], Gs['bike_highwaycycleway'], Gs['bike_bicycleroad'], Gs['bike_cyclewayrighttrack'], Gs['bike_designatedpath'], Gs['bike_cyclestreet']])
    ox_to_csv(Gs[parameterid], PATH["data"] + placeid+"_newdata" + "/", placeid, parameterid)
    
    parameterid = 'bikeable'
    Gs[parameterid] = nx.compose_all([Gs['biketrack'], Gs['car30'], Gs['bike_livingstreet']]) 
    ox_to_csv(Gs[parameterid], PATH["data"] + placeid + "/", placeid, parameterid)
    
    parameterid = 'biketrackcarall'
    Gs[parameterid] = nx.compose(Gs['biketrack'], Gs['carall']) # Order is important
    ox_to_csv(Gs[parameterid], PATH["data"] + placeid + "/", placeid, parameterid)
    
    print([k for k in Gs ])
    
    for parameterid in networktypes[:-2]:
        #G_temp = nx.MultiDiGraph(ox.utils_graph.get_digraph(ox.simplify_graph(Gs[parameterid]))) # This doesnt work - cant get rid of multiedges
        ox_to_csv(ox.simplify_graph(Gs[parameterid]), PATH["data"] + placeid + "/", placeid, parameterid, "_simplified")



# Compress all data files (will not do anything if files were compressed already)
for folder, subfolders, files in os.walk(PATH["data"]):
    for file in files:
        if file.endswith('es.csv'):
            compress_file(folder + "/", file.split(".")[0])


# ## Frequency distribution of 'length_attr'


len_dict = nx.get_edge_attributes(Gs['carall'], "length")
normalise_edge_dict(len_dict)
len_dict_list = list(len_dict.values())

i=-1
for e in Gs['carall'].edges():
    i+=1
    a,b = e
    nx.set_edge_attributes(Gs['carall'], {(a,b,0): {"length_attr": len_dict_list[i] }})


length_attr_mean = statistics.mean([k for k in len_dict.values()])

with open('../../bikenwgrowth_external/data/copenhagen/bikedata/mean_length_attr.pkl', 'wb') as f:
    pickle.dump(length_attr_mean, f)

with open('../../bikenwgrowth_external/data/copenhagen/bikedata/edges_dict_length_attr.pkl', 'wb') as f:
    pickle.dump(len_dict, f)

G_carall = Gs['carall'].copy()






































#Load bike data
count_df = pd.read_csv("../../bikenwgrowth_external/data/copenhagen/bikedata/bicycle_counts.csv")
count_df = count_df[count_df.year ==2019]
bikelanes = gpd.GeoDataFrame(count_df, geometry=gpd.points_from_xy(count_df['long'], count_df['lat']))

#convert to fraction. All bikecounts are added 1 to avoid division by zero (if zero bikes).
count_df['bcount_attr']= count_df['bicycle_count']
for i in range(len(count_df)):
    count_df['bcount_attr'].iloc[i] = 1.0/float(count_df['bicycle_count'].iloc[i]+1)

#Normalise bikecounts in range 0.1 to 1 to avoid zero values

x = count_df.drop(count_df.columns[[0,1,2,3,4,5,6]], axis=1) #returns a numpy array of only bikecounts
min_max_scaler = preprocessing.MinMaxScaler(feature_range=(0.1, 1.0))
x_scaled = min_max_scaler.fit_transform(x)
bike_norm_df = pd.DataFrame(x_scaled)

#update count_df with normalised values

for i in range(len(count_df)):
    count_df['bcount_attr'].iloc[i] = bike_norm_df.iloc[i]

#We create a variable for unassigned edges, 
# which is the average edgelength multiplied with the average fraction of bikecounts in the network

mean_bcount_attr = count_df['bcount_attr'].mean()

edges_len_dict = nx.get_edge_attributes(G_carall, 'length')
edges_len_mean = statistics.mean([k for k in edges_len_dict.values()])

bcount_attr_unassigned = edges_len_mean*mean_bcount_attr

with open('../../bikenwgrowth_external/data/copenhagen/bikedata/unassigned_bcount_attr.pkl', 'wb') as f:
    pickle.dump(bcount_attr_unassigned, f)

bcount_attr_unassigned


nx.set_edge_attributes(G_carall, 0.0, 'bcount_attr')

#We apply bikecounts from our data to the nearest edges in the carall network
for i in range(len(count_df)):
    ne = ox.distance.get_nearest_edge(G_carall, [count_df.iloc[i].lat,count_df.iloc[i].long])
    nx.set_edge_attributes(G_carall, {ne: {'bcount_attr': count_df.iloc[i].bcount_attr }})

    
# a dictionary of each of the two new attributes in the G_carall graph is generated and saved. 
bcount_attr_dict = nx.get_edge_attributes(G_carall, "bcount_attr")

ox_to_csv(G_carall, PATH["data"] + 'copenhagen' + "/", 'copenhagen', 'carall')

ox_to_csv(ox.simplify_graph(G_carall), PATH["data"] + 'copenhagen' + "/", 'copenhagen', 'carall', "_simplified")



with zipfile.ZipFile("../../bikenwgrowth_external/data/copenhagen/copenhagen_carall_edges.zip", 'r') as zip_ref:
    zip_ref.extractall("../../bikenwgrowth_external/data/copenhagen/")

edges = pd.read_csv("../../bikenwgrowth_external/data/copenhagen/copenhagen_carall_edges.csv")

GG_carall = copy.deepcopy(G_carall)

edges = pd.read_csv("../../bikenwgrowth_external/data/copenhagen/copenhagen_carall_edges.csv")

#We take only assigned edges
edges1 = edges[edges.bcount_attr !=0.0]



#we remove unnecessery data
edges2 = edges1.drop(edges1.columns[[1,3,4,5,6,8,9,10,11,12,13,14,15,16,17,18]], axis=1)


#we apply the mean of bikecounts for all assigned streets, by grouping on the street name and calculating the mean.
edges3 = edges2.groupby('name')['bcount_attr'].mean().to_frame()

#renaming this column
edges3 = edges3.rename(columns={"bcount_attr": "mean_group_bcount"})

#the initial edges are joined with the new generalised counts
result = pd.merge(edges,edges3,on='name',how = 'left')

result.to_csv("../../bikenwgrowth_external/data/copenhagen/copenhagen_carall_edges.csv")

compress_file("../../bikenwgrowth_external/data/copenhagen/","copenhagen_carall_edges")

result3 = result2.copy()
for i in range(len(result3)):
    num = result3['mean_group_bcount'].iloc[i]
    #if num is NaN
    if num != num:
        result3['bcount_attr'].iloc[i]= bcount_attr_unassigned
    if result3['bcount_attr']==0.0:
        result3['bcount_attr'].iloc[i]= num *result3['length'].iloc[i]
    else:
        result3['bcount_attr'].iloc[i]= result3['bcount_attr'].iloc[i] *result3['length'].iloc[i]
# ## Apply edge attribute after generalisation


result2 = result

#we apply the 'bcount_attr' the the result2 dataframe, representing all edges in the carall network.
# for edges that 'still' do not have a bikecount, a standard value is assigned 'bcount_attr_unassigned',
# otherwise the new mean fraction of bikecounts for each edge, is multiplied with the length of this edge.
# For now we lost the original fraction of bikecounts for assigned edges, but we will add them back in next step.
for i in range(len(result2)):
    num = result2['mean_group_bcount'].iloc[i]
    #if num is NaN
    if num != num:
        result2['mean_group_bcount'].iloc[i]= bcount_attr_unassigned
    else:
        result2['mean_group_bcount'].iloc[i]= num *result2['length'].iloc[i]

# The new results are added to the carall network,
i=-1
for e in GG_carall.edges():
    i+=1
    a,b=e
    old_bcount_attr = GG_carall.get_edge_data(a,b,0)['bcount_attr']
    # if the edge is initially unassigned in the network we check if a generalised mean value of the whole street, 
    #belonging to this street exist, otherwise a standard value is given. If an edge is initially assigned a bikecount
    # we assign it the bcount_attr again, represented as edgelength multiplied by the fraction of bikecounts.
    if old_bcount_attr ==0.0:
        if  result2['mean_group_bcount'].iloc[i] == bcount_attr_unassigned:
            nx.set_edge_attributes(GG_carall, {(a,b,0): {"bcount_attr": bcount_attr_unassigned }})
        else:
            edgelength = GG_carall.get_edge_data(a,b,0)['length']
            mean_group_count = result2['mean_group_bcount'].iloc[i]
            nx.set_edge_attributes(GG_carall, {(a,b,0): {"bcount_attr": mean_group_count }})
    else:
        edgelength = GG_carall.get_edge_data(a,b,0)['length']
        bcountattr = old_bcount_attr* edgelength
        nx.set_edge_attributes(GG_carall, {(a,b,0): {"bcount_attr": bcountattr }})


bcount_attr_dict = nx.get_edge_attributes(GG_carall, "bcount_attr")

normalise_graph_attr(GG_carall, "bcount_attr")

bcount_attr_dict = nx.get_edge_attributes(GG_carall, "bcount_attr")
bcount_attr_mean = statistics.mean([k for k in bcount_attr_dict.values()])

with open('../../bikenwgrowth_external/data/copenhagen/bikedata/mean_bcount_attr.pkl', 'wb') as f:
    pickle.dump(bcount_attr_mean, f)


with open('../../bikenwgrowth_external/data/copenhagen/bikedata/edges_dict_bcount_attr.pkl', 'wb') as f:
    pickle.dump(bcount_attr_dict, f)






































G_carall = GG_carall.copy()

pop_den_df = pd.read_csv("../../bikenwgrowth_external/data/copenhagen/bikedata/dnk_pd_2019_1km_ASCII_XYZ.csv")
#pop_den_df = pd.read_csv("../../bikenwgrowth_external/data/copenhagen/bikedata/dnk_pd_2019_1km_ASCII_XYZ_small.csv")

#convert to fraction. All pop densities are added 1 to avoid division by zero (if zero density).
pop_den_df['pop_den_attr']= pop_den_df['Z']
for i in range(len(pop_den_df['Z'])):
    pop_den_df['pop_den_attr'].iloc[i] = 1.0/float(pop_den_df['pop_den_attr'].iloc[i]+1)

pop_den_df.rename(columns = {'X':'long', 'Y':'lat','Z':'pop_den'}, inplace = True)

i=0
nDict = {}
for i in range(len(pop_den_df)):
    n = ox.distance.get_nearest_node(G_carall, [pop_den_df.iloc[i].lat,pop_den_df.iloc[i].long])
    if haversine([pop_den_df.iloc[i].lat,pop_den_df.iloc[i].long], (G_carall.nodes[n]["y"], G_carall.nodes[n]["x"]), unit="m") <= snapthreshold:
        #nDict = {**nDict, n: pop_den_df.iloc[i].pop_den_attr}
        nDict[n] = pop_den_df.iloc[i].pop_den_attr
        i+=1
        print(i)

nx.set_edge_attributes(G_carall, 0.0, 'pop_den_attr')

for e in G_carall.edges():
    a,b=e
    lat = G_carall.nodes[a]["y"]
    long = G_carall.nodes[a]["x"]
    eDistDict = {}
    
    for n in nDict:
        y = G_carall.nodes[n]["y"]
        x = G_carall.nodes[n]["x"]
        dist = haversine([lat,long], (y,x), unit="m")
        #eDistDict = {**eDistDict, dist:nDict[n]}
        eDistDict[dist] = nDict[n]
    
    minDist = min(eDistDict.keys()) 
    popDenAttr = eDistDict[minDist]
    edgelength = edgelength = G_carall.get_edge_data(a,b,0)['length']
    pop_den_attr = popDenAttr * edgelength
    
    nx.set_edge_attributes(G_carall, {(a,b,0): {"pop_den_attr": pop_den_attr }})
    
        #(distance: (node, pop_den_attr))
        
normalise_graph_attr(G_carall, "pop_den_attr")

pop_len_attr_dict = nx.get_edge_attributes(G_carall, "pop_den_attr")

pop_den_attr_mean = statistics.mean([k for k in pop_len_attr_dict.values()])

with open('../../bikenwgrowth_external/data/copenhagen/bikedata/mean_pop_den_attr.pkl', 'wb') as f:
    pickle.dump(pop_den_attr_mean, f)


with open('../../bikenwgrowth_external/data/copenhagen/bikedata/edges_dict_pop_den_attr.pkl', 'wb') as f:
    pickle.dump(pop_len_attr_dict, f)

























with open("../../bikenwgrowth_external/data/copenhagen/bikedata/mean_pop_den_attr.pkl", 'rb') as f:
    mean_pop_den_attr = pickle.load(f)
with open("../../bikenwgrowth_external/data/copenhagen/bikedata/mean_bcount_attr.pkl", 'rb') as q:
    mean_bcount_attr = pickle.load(q)


# ## Set alpha



a = 0.5



unassigned_bcount_pop_den_attr = (a* mean_bcount_attr) + ((1-a)* mean_pop_den_attr)



with open('../../bikenwgrowth_external/data/copenhagen/bikedata/unassigned_bcount_pop_den_attr.pkl', 'wb') as f:
    pickle.dump(unassigned_bcount_pop_den_attr, f)


# ## Add 'bcount_pop_den_attr' to carall graph

nx.set_edge_attributes(G_carall, 0.0, 'bcount_pop_den_attr')

ox_to_csv(G_carall, PATH["data"] + 'copenhagen' + "/", 'copenhagen', 'carall')

ox_to_csv(ox.simplify_graph(G_carall), PATH["data"] + 'copenhagen' + "/", 'copenhagen', 'carall', "_simplified")

ox.save_graphml(G_carall, "../../bikenwgrowth_external/data/copenhagen/bikedata/G_carall_graphml.graphml")

with zipfile.ZipFile("../../bikenwgrowth_external/data/copenhagen/copenhagen_carall_edges.zip", 'r') as zip_ref:
    zip_ref.extractall("../../bikenwgrowth_external/data/copenhagen/")

edges = pd.read_csv("../../bikenwgrowth_external/data/copenhagen/copenhagen_carall_edges.csv")




# ## Calculate 'bcount_pop_den_attr' for each edge, and add to carall graph


edges = edges.drop(edges.columns[[0,1,2,3,4,5,6,9,10,11,12,13,14,15,16,17,18,19,20,21]], axis=1)

edges['bcount_pop_den_attr'] = a* edges['bcount_attr'] + (1-a)*edges['pop_den_attr']
#edges['bcount_attr'] * edges['pop_den_attr']



i=-1
for e in G_carall.edges():
    i+=1
    a,b=e
    bcount_pop_den_attr = edges['bcount_pop_den_attr'].iloc[i]
    nx.set_edge_attributes(G_carall, {(a,b,0): {"bcount_pop_den_attr": bcount_pop_den_attr}})

normalise_graph_attr(G_carall, "bcount_pop_den_attr")

bcount_pop_den_attr_dict = nx.get_edge_attributes(G_carall, "bcount_pop_den_attr")

bcount_pop_den_attr_mean = statistics.mean([k for k in bcount_pop_den_attr_dict.values()])

with open('../../bikenwgrowth_external/data/copenhagen/bikedata/mean_bcount_pop_den_att.pkl', 'wb') as f:
    pickle.dump(bcount_pop_den_attr_mean, f)

ox_to_csv(G_carall, PATH["data"] + 'copenhagen' + "/", 'copenhagen', 'carall')

ox_to_csv(ox.simplify_graph(G_carall), PATH["data"] + 'copenhagen' + "/", 'copenhagen', 'carall', "_simplified")

ox.save_graphml(G_carall, "../../bikenwgrowth_external/data/copenhagen/bikedata/G_carall_graphml.graphml")

with open('../../bikenwgrowth_external/data/copenhagen/bikedata/edges_dict_bcount_pop_den_attr.pkl', 'wb') as f:
    pickle.dump(bcount_pop_den_attr_dict, f)
