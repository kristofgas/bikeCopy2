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
        write_result(output_MST, "dict", placeid, poi_source, "", "_"+ attr+"_"+ "mst.csv")
