
G_carall = ox.load_graphml('../../bikenwgrowth_external/data/copenhagen/bikedata/G_carall_graphml.graphml')


# ## Load population density data, convert to fractions

# In[5]:


pop_den_df = pd.read_csv("../../bikenwgrowth_external/data/copenhagen/bikedata/dnk_pd_2019_1km_ASCII_XYZ.csv")
#pop_den_df = pd.read_csv("../../bikenwgrowth_external/data/copenhagen/bikedata/dnk_pd_2019_1km_ASCII_XYZ_small.csv")

#convert to fraction. All pop densities are added 1 to avoid division by zero (if zero density).
pop_den_df['pop_den_attr']= pop_den_df['Z']
for i in range(len(pop_den_df['Z'])):
    pop_den_df['pop_den_attr'].iloc[i] = 1.0/float(pop_den_df['pop_den_attr'].iloc[i]+1)

pop_den_df.rename(columns = {'X':'long', 'Y':'lat','Z':'pop_den'}, inplace = True)


# In[6]:



# ## Create dictionary of nodes from the Carall graph from nearest population density counters

# In[7]:

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
        


# ## Normalisation

# In[12]:


normalise_graph_attr(G_carall, "pop_den_attr")

pop_len_attr_dict = nx.get_edge_attributes(G_carall, "pop_den_attr")

pop_den_attr_mean = statistics.mean([k for k in pop_len_attr_dict.values()])

with open('../../bikenwgrowth_external/data/copenhagen/bikedata/mean_pop_den_attr.pkl', 'wb') as f:
    pickle.dump(pop_den_attr_mean, f)

ox_to_csv(G_carall, PATH["data"] + 'copenhagen' + "/", 'copenhagen', 'carall')

ox_to_csv(ox.simplify_graph(G_carall), PATH["data"] + 'copenhagen' + "/", 'copenhagen', 'carall', "_simplified")

ox.save_graphml(G_carall, "../../bikenwgrowth_external/data/copenhagen/bikedata/G_carall_graphml.graphml")

with open('../../bikenwgrowth_external/data/copenhagen/bikedata/edges_dict_pop_den_attr.pkl', 'wb') as f:
    pickle.dump(pop_len_attr_dict, f)


# In[13]:

