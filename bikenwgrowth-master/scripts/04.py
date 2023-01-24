warnings.filterwarnings('ignore')
rerun_existing = True


with open("../../bikenwgrowth_external/data/copenhagen/bikedata/mean_length_attr.pkl", 'rb') as f:
    unassigned_length_attr = pickle.load(f)
with open("../../bikenwgrowth_external/data/copenhagen/bikedata/mean_pop_den_attr.pkl", 'rb') as f:
    unassigned_pop_den_attr = pickle.load(f)
with open("../../bikenwgrowth_external/data/copenhagen/bikedata/mean_bcount_attr.pkl", 'rb') as q:
    unassigned_bcount_attr = pickle.load(q)
with open("../../bikenwgrowth_external/data/copenhagen/bikedata/mean_bcount_pop_den_att.pkl", 'rb') as q:
    unassigned_bcount_pop_den_attr = pickle.load(q)


# ## Join new attributes to all networks on geometry

# In[19]:


with zipfile.ZipFile("../../bikenwgrowth_external/data/copenhagen/copenhagen_carall_edges.zip", 'r') as zip_ref:
    zip_ref.extractall("../../bikenwgrowth_external/data/copenhagen/")

carall_edges = pd.read_csv("../../bikenwgrowth_external/data/copenhagen/copenhagen_carall_edges.csv")

for network in networktypesdata:
    print(network)
    
    with zipfile.ZipFile("../../bikenwgrowth_external/data/copenhagen/copenhagen_"+network+"_edges.zip", 'r') as zip_ref:
        zip_ref.extractall("../../bikenwgrowth_external/data/copenhagen/")

    biketrack_edges = pd.read_csv("../../bikenwgrowth_external/data/copenhagen/copenhagen_"+network+"_edges.csv")


    #the initial edges are joined with the new generalised counts
    result = pd.merge(biketrack_edges, carall_edges[['geometry','length_attr','bcount_attr','pop_den_attr','bcount_pop_den_attr']],how = 'left',on='geometry')
    #left_on=['u','v'], right_on = ['u','v']

    for i in range(len(result)):
        length_attr = result['length_attr'].iloc[i]
        bcount_attr = result['bcount_attr'].iloc[i]
        pop_den_attr = result['pop_den_attr'].iloc[i]
        bcount_pop_den_attr = result['bcount_pop_den_attr'].iloc[i]
        #if num is NaN
        if length_attr != length_attr:
            result['length_attr'].iloc[i]= unassigned_length_attr
        if bcount_attr != bcount_attr:
            result['bcount_attr'].iloc[i]= unassigned_bcount_attr
        if pop_den_attr != pop_den_attr:
            result['pop_den_attr'].iloc[i]= unassigned_pop_den_attr
        if bcount_pop_den_attr != bcount_pop_den_attr:
            result['bcount_pop_den_attr'].iloc[i]= unassigned_bcount_pop_den_attr
            
    result.to_csv("../../bikenwgrowth_external/data/copenhagen/copenhagen_"+network+"_edges.csv")
    compress_file("../../bikenwgrowth_external/data/copenhagen/","copenhagen_"+network+"_edges")
    


# ## Analyze existing infrastructure


for placeid, placeinfo in tqdm(cities.items(), desc = "Cities"):
    print(placeid + ": Analyzing existing infrastructure.")
    
    # output_place is one static file for the existing city. This can be compared to the generated infrastructure.
    # Make a check if this file was already generated - it only needs to be done once. If not, generate it:
    for attr in attrlist:
        filename = placeid + "_"+attr +"_existing.csv"
        if rerun_existing or not os.path.isfile(PATH["results"] + placeid + "/" + filename):
            empty_metrics = {
                             "length":0,
                             #"length_lcc":0,
                             #"coverage": 0,
                             #"directness": 0,
                             #"directness_lcc": 0,
                             #"poi_coverage": 0,
                             #"components": 0,
                             #"efficiency_global": 0,
                             #"efficiency_local": 0,
                             #"efficiency_global_routed": 0,
                             #"efficiency_local_routed": 0,
                             #"directness_lcc_linkwise": 0,
                             #"directness_all_linkwise": 0
                            }
            output_place = {}
            for networktype in networktypes:
                output_place[networktype] = copy.deepcopy(empty_metrics)

            # Analyze all networks     
            Gs = {}
            for networktype in networktypes:
                if networktype != "biketrack_onstreet" and networktype != "bikeable_offstreet":
                    graph = csv_to_ig_custom(PATH["data"] + placeid + "/", placeid, networktype,attr)
                    Gs[networktype] = graph
                    graph_simplified = simplify_ig(graph)
                    Gs[networktype + "_simplified"] = graph_simplified
                    #Gs[networktype] = csv_to_ig_custom(PATH["data"] + placeid + "/", placeid, networktype)
                    #Gs[networktype + "_simplified"] = csv_to_ig_custom(PATH["data"] + placeid + "/", placeid, networktype + "_simplified")
                elif networktype == "biketrack_onstreet":
                    graph_biketrack = Gs["biketrack"]
                    graph_carall =Gs["carall"]
                    Gs[networktype] = intersect_igraphs(graph_biketrack, graph_carall)
                    Gs[networktype + "_simplified"] = intersect_igraphs(simplify_ig(graph_biketrack), simplify_ig(graph_carall))
                elif networktype == "bikeable_offstreet":
                    G_temp = copy.deepcopy(Gs["bikeable"])
                    delete_overlaps(G_temp, Gs["carall"])
                    Gs[networktype] = G_temp
                    G_temp = copy.deepcopy(simplify_ig(Gs["bikeable"]))
                    delete_overlaps(G_temp, Gs["carall_simplified"])
                    Gs[networktype + "_simplified"] = G_temp

            with open(PATH["data"] + placeid + "/" + placeid + '_poi_' + poi_source + '_nnidscarall.csv') as f:
                nnids = [int(line.rstrip()) for line in f]


            covs = {}
            for networktype in tqdm(networktypes, desc = "Networks", leave = False):
                if debug: print(placeid + ": Analyzing results: " + networktype)
                metrics, cov = calculate_metrics(Gs[networktype], Gs[networktype + "_simplified"], Gs['carall'], nnids, empty_metrics, buffer_walk, numnodepairs, debug)
                #metrics, cov = calculate_metrics_custom(Gs[networktype], Gs[networktype + "_simplified"], Gs['carall'], nnids, empty_metrics, buffer_walk, numnodepairs, debug)

                for key, val in metrics.items():
                    output_place[networktype][key] = val
                covs[networktype] = cov
            # Save the covers
            write_result(covs, "pickle", placeid, "", "",attr+"_"+"existing_covers.pickle")

            # Write to CSV
            write_result(output_place, "dictnested", placeid, "", "", attr+"_"+"existing.csv", empty_metrics)


# ## Analyze POI based results


for placeid, placeinfo in tqdm(cities.items(), desc = "Cities"):
    print(placeid + ": Analyzing results")
    for attr in attrlist:
        print("attr: " + attr)
    # Load networks
        G_carall = csv_to_ig_custom(PATH["data"] + placeid + "/", placeid, 'carall',attr)
        #G_carall = csv_to_ig(PATH["data"] + placeid + "/", placeid, 'carall')
        Gexisting = {}
        for networktype in ["biketrack", "bikeable"]:
            Gexisting[networktype] = csv_to_ig_custom(PATH["data"] + placeid + "/", placeid, networktype, attr)



        # Load POIs
        with open(PATH["data"] + placeid + "/" + placeid + '_poi_' + poi_source + '_nnidscarall.csv') as f:
            nnids = [int(line.rstrip()) for line in f]

        # Load results
        filename = placeid + '_poi_' + poi_source + "_" + prune_measure + "_"+ attr
        resultfile = open(PATH["results"] + placeid + "/" + filename  +".pickle",'rb')
        res = pickle.load(resultfile)
        resultfile.close()
        if debug: pp.pprint(res)
        print(1)
        # Calculate
        # output contains lists for all the prune_quantile values of the corresponding results
        #output, covs = calculate_metrics_additively_custom(res["GTs"], res["GT_abstracts"], res["prune_quantiles"], G_carall, nnids, buffer_walk, numnodepairs, debug, True, Gexisting)
        #output_MST, cov_MST = calculate_metrics_custom(res["MST"], res["MST_abstract"], G_carall, nnids, output, buffer_walk, numnodepairs, debug, True, ig.Graph(), Polygon(), False, Gexisting)

        output, covs = calculate_metrics_additively(res["GTs"], res["GT_abstracts"], res["prune_quantiles"], G_carall, nnids, buffer_walk, numnodepairs, debug, True, Gexisting)
        output_MST, cov_MST = calculate_metrics(res["MST"], res["MST_abstract"], G_carall, nnids, output, buffer_walk, numnodepairs, debug, True, ig.Graph(), Polygon(), False, Gexisting)

        # Save the covers
        write_result(covs, "pickle", placeid, poi_source, prune_measure,  "_"+ attr+"_covers.pickle")
    #     write_result(covs_carminusbike, "pickle", placeid, poi_source, prune_measure, "_covers_carminusbike.pickle")
        write_result(cov_MST, "pickle", placeid, poi_source, prune_measure, "_"+ attr+"_cover_mst.pickle")

        # Write to CSV
        write_result(output, "dict", placeid, poi_source, prune_measure, "_"+ attr+".csv")
    #     write_result(output_carminusbike, "dict", placeid, poi_source, prune_measure, "_carminusbike.csv")
    #     write_result(output_carconstrictedbike, "dict", placeid, poi_source, prune_measure, "_carconstrictedbike.csv")
        write_result(output_MST, "dict", placeid, poi_source, "", "_"+ attr+"mst.csv")
