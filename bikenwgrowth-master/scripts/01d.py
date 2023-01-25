
G_carall = ox.load_graphml('../../bikenwgrowth_external/data/copenhagen/bikedata/G_carall_graphml.graphml')


# In[5]:


with open("../../bikenwgrowth_external/data/copenhagen/bikedata/mean_pop_den_attr.pkl", 'rb') as f:
    mean_pop_den_attr = pickle.load(f)
with open("../../bikenwgrowth_external/data/copenhagen/bikedata/mean_bcount_attr.pkl", 'rb') as q:
    mean_bcount_attr = pickle.load(q)


# ## Set alpha

# In[6]:


a = 0.5


# In[7]:


unassigned_bcount_pop_den_attr = (a* mean_bcount_attr) + ((1-a)* mean_pop_den_attr)


# In[8]:


with open('../../bikenwgrowth_external/data/copenhagen/bikedata/unassigned_bcount_pop_den_attr.pkl', 'wb') as f:
    pickle.dump(unassigned_bcount_pop_den_attr, f)


# ## Add 'bcount_pop_den_attr' to carall graph

# In[9]:


nx.set_edge_attributes(G_carall, 0.0, 'bcount_pop_den_attr')

ox_to_csv(G_carall, PATH["data"] + 'copenhagen' + "/", 'copenhagen', 'carall')

ox_to_csv(ox.simplify_graph(G_carall), PATH["data"] + 'copenhagen' + "/", 'copenhagen', 'carall', "_simplified")

ox.save_graphml(G_carall, "../../bikenwgrowth_external/data/copenhagen/bikedata/G_carall_graphml.graphml")

with zipfile.ZipFile("../../bikenwgrowth_external/data/copenhagen/copenhagen_carall_edges.zip", 'r') as zip_ref:
    zip_ref.extractall("../../bikenwgrowth_external/data/copenhagen/")

edges = pd.read_csv("../../bikenwgrowth_external/data/copenhagen/copenhagen_carall_edges.csv")


# In[10]:




# ## Calculate 'bcount_pop_den_attr' for each edge, and add to carall graph

# In[11]:


edges = edges.drop(edges.columns[[0,1,2,3,4,5,6,9,10,11,12,13,14,15,16,17,18,19,20,21]], axis=1)

edges['bcount_pop_den_attr'] = a* edges['bcount_attr'] + (1-a)*edges['pop_den_attr']
#edges['bcount_attr'] * edges['pop_den_attr']


# In[12]:



# In[13]:


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

