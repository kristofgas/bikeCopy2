
G_carall = ox.load_graphml('../../bikenwgrowth_external/data/copenhagen/bikedata/G_carall_graphml.graphml')


# ## Load bike traffic data, convert to fractions and normalise
# 

# In[5]:


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
# In[6]:




# ## Add 'bcount_attr' to carall graph

# In[7]:


#We create a variable for unassigned edges, 
# which is the average edgelength multiplied with the average fraction of bikecounts in the network

mean_bcount_attr = count_df['bcount_attr'].mean()

edges_len_dict = nx.get_edge_attributes(G_carall, 'length')
edges_len_mean = statistics.mean([k for k in edges_len_dict.values()])

bcount_attr_unassigned = edges_len_mean*mean_bcount_attr

with open('../../bikenwgrowth_external/data/copenhagen/bikedata/unassigned_bcount_attr.pkl', 'wb') as f:
    pickle.dump(bcount_attr_unassigned, f)


# In[8]:


# In[9]:


#we set the bcount_attr to 0 initially

nx.set_edge_attributes(G_carall, 0.0, 'bcount_attr')

#We apply bikecounts from our data to the nearest edges in the carall network
for i in range(len(count_df)):
    ne = ox.distance.get_nearest_edge(G_carall, [count_df.iloc[i].lat,count_df.iloc[i].long])
    nx.set_edge_attributes(G_carall, {ne: {'bcount_attr': count_df.iloc[i].bcount_attr }})

    
# a dictionary of each of the two new attributes in the G_carall graph is generated and saved. 
bcount_attr_dict = nx.get_edge_attributes(G_carall, "bcount_attr")

ox_to_csv(G_carall, PATH["data"] + 'copenhagen' + "/", 'copenhagen', 'carall')

ox_to_csv(ox.simplify_graph(G_carall), PATH["data"] + 'copenhagen' + "/", 'copenhagen', 'carall', "_simplified")


## Plot bikecounters and nearest edges


































# ## Generalise bikecounts to whole streets

# In[12]:


with zipfile.ZipFile("../../bikenwgrowth_external/data/copenhagen/copenhagen_carall_edges.zip", 'r') as zip_ref:
    zip_ref.extractall("../../bikenwgrowth_external/data/copenhagen/")

edges = pd.read_csv("../../bikenwgrowth_external/data/copenhagen/copenhagen_carall_edges.csv")

GG_carall = copy.deepcopy(G_carall)

edges = pd.read_csv("../../bikenwgrowth_external/data/copenhagen/copenhagen_carall_edges.csv")

#We take only assigned edges
edges1 = edges[edges.bcount_attr !=0.0]


# In[13]:


#we remove unnecessery data
edges2 = edges1.drop(edges1.columns[[1,3,4,5,6,8,9,10,11,12,13,14,15,16,17,18]], axis=1)


# In[14]:


#we apply the mean of bikecounts for all assigned streets, by grouping on the street name and calculating the mean.
edges3 = edges2.groupby('name')['bcount_attr'].mean().to_frame()

#renaming this column
edges3 = edges3.rename(columns={"bcount_attr": "mean_group_bcount"})

#the initial edges are joined with the new generalised counts
result = pd.merge(edges,edges3,on='name',how = 'left')

result.to_csv("../../bikenwgrowth_external/data/copenhagen/copenhagen_carall_edges.csv")

compress_file("../../bikenwgrowth_external/data/copenhagen/","copenhagen_carall_edges")


# ## Apply edge attribute after generalisation

# In[15]:




# In[17]:


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


# In[18]:


bcount_attr_dict = nx.get_edge_attributes(GG_carall, "bcount_attr")


# In[19]:




# In[21]:


normalise_graph_attr(GG_carall, "bcount_attr")

bcount_attr_dict = nx.get_edge_attributes(GG_carall, "bcount_attr")
bcount_attr_mean = statistics.mean([k for k in bcount_attr_dict.values()])

with open('../../bikenwgrowth_external/data/copenhagen/bikedata/mean_bcount_attr.pkl', 'wb') as f:
    pickle.dump(bcount_attr_mean, f)


ox_to_csv(GG_carall, PATH["data"] + 'copenhagen' + "/", 'copenhagen', 'carall')

ox_to_csv(ox.simplify_graph(GG_carall), PATH["data"] + 'copenhagen' + "/", 'copenhagen', 'carall', "_simplified")

ox.save_graphml(GG_carall, "../../bikenwgrowth_external/data/copenhagen/bikedata/G_carall_graphml.graphml")

with open('../../bikenwgrowth_external/data/copenhagen/bikedata/edges_dict_bcount_attr.pkl', 'wb') as f:
    pickle.dump(bcount_attr_dict, f)


# In[22]:

