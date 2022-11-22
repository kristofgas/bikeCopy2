debug = False

exec(open("../parameters/parameters.py").read())
exec(open("../code/path.py").read())
exec(open("../code/setupCPH.py").read())
exec(open("../code/functions.py").read())

if __name__ == '__main__':
    if len(sys.argv) > 1: # limit to specific city
        citynumber = int(sys.argv[1])
        cityid = list(cities.keys())[citynumber]
        print(cityid)
        cities = {k:v for (k,v) in cities.items() if k == cityid}

    # 01 and 02 are done locally instead to supervise 
    # the OSM connection process manually
    #print("Running 01.py")
    #exec(open("01.py").read())
    #print("Running 02.py")
    #exec(open("02.py").read())

    poi_source_list = ["grid", "railwaystation"]
    prune_measure_list = ["betweenness"]
    parsets = list(itertools.product(poi_source_list, prune_measure_list))

    if len(sys.argv) > 2: # limit to specific parameter set
        parsets_used = [parsets[int(sys.argv[2])]]
    else:
        parsets_used = parsets

    for poi_source, prune_measure in parsets_used:
        print(poi_source, prune_measure)

        print("Running 03.py")
        exec(open("03.py").read())

        print("Running 04.py")
        exec(open("04.py").read())

        print("Running 05.py")
        exec(open("05.py").read())