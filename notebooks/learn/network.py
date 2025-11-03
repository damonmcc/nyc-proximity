import marimo

__generated_with = "0.17.6"
app = marimo.App(width="medium")

with app.setup:
    import marimo as mo
    import geopandas as gpd
    import pandas as pd
    import osmnx as ox
    import networkx as nx
    import matplotlib.pyplot as plt
    from pathlib import Path


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## Get streets, places, and census blocks
    """)
    return


@app.cell
def _():
    DATA_DIRECTORY = Path("./data")
    return (DATA_DIRECTORY,)


@app.cell
def _(DATA_DIRECTORY):
    nyc_blocks = gpd.read_parquet(DATA_DIRECTORY / "nyc_blocks.parquet")
    return (nyc_blocks,)


@app.cell
def _():
    inwood_census_block_ids = [
        "10293001001",
        "10283004002",
        "10285001000",
        "10287003000",
        "10293002000",
        "10293002001",
        "10293003000",
        "10293003001",
        "10293004000",
        "10293004001",
        "10293005000",
        "10295001000",
        "10307003001",
        "10299002001",
        "10303003000",
        "10307001002",
        "10307002000",
        "10299003006",
        "10307001001",
        "10285001001",
        "10285002000",
        "10285003000",
        "10285003001",
        "10285004000",
        "10287001009",
        "10291006000",
        "10291007000",
        "10293001000",
        "10297001001",
        "10297001005",
        "10297001006",
        "10299001000",
        "10299001001",
        "10299003000",
        "10299003001",
        "10299003002",
        "10299003003",
        "10299003004",
        "10299003005",
        "10283003000",
        "10283003001",
        "10283004000",
        "10291002000",
        "10283004001",
        "10287003001",
        "10287001003",  # manually added
        "10287001004",
        "10291001000",
        "10287001005",
        "10291003000",
        "10291003001",
        "10287001006",
        "10295004000",
        "10287002000",
        "10287002001",
        "10295004001",
        "10291004000",
        "10295004002",
        "10291004001",
        "10297000001",
        "10291004002",
        "10297000002",
        "10291005000",
        "10293001002",
        "10293001003",
        "10293001004",
        "10297001000",
        "10295001001",
        "10295002000",
        "10295002001",
        "10295003000",
        "10307002001",
        "10295003001",
        "10307003000",
        "10297001004",
        "10299001002",
        "10299002000",
        "10299002002",
        "10299002003",
        "10299002004",
        "10299002005",
        "10299002006",
        "10299002007",
        "10297001003",
        "10297001002",  # manually added
        "10299003007",
        "10299003008",
        "10299003009",
        "10299003010",
        "10299003011",
        "10303002002",
        "10303002003",
        "10303003001",
        "10303003002",
        "10303003003",
        "10307001000",
        "10299003012",
        "10303001000",
        "10303001001",
        "10303001002",
        "10303001003",
        "10303002000",
        "10303002001",
    ]
    inwood_census_block_ids_fixed = ["3606" + x for x in inwood_census_block_ids]
    return (inwood_census_block_ids_fixed,)


@app.cell
def _(inwood_census_block_ids_fixed, nyc_blocks):
    inwood_census_blocks = nyc_blocks[
        nyc_blocks["GEOID20"].isin(inwood_census_block_ids_fixed)
    ]
    inwood_census_blocks
    return (inwood_census_blocks,)


@app.cell
def _(inwood_census_blocks):
    inwood_polygon = inwood_census_blocks.union_all().convex_hull
    inwood_graph_raw = ox.graph.graph_from_polygon(
        inwood_polygon, truncate_by_edge=True
    )
    _, _ax = ox.plot.plot_graph(
        inwood_graph_raw, node_size=0, edge_color="w", edge_linewidth=0.2
    )
    _ = _ax.axis("off")
    return inwood_graph_raw, inwood_polygon


@app.cell
def _(inwood_graph_raw):
    inwood_graph_projected = ox.projection.project_graph(
        inwood_graph_raw, to_crs="2263"
    )
    inwood_graph_projected.graph["crs"]
    return (inwood_graph_projected,)


@app.cell
def _(inwood_graph_projected):
    inwood_graph = ox.simplification.consolidate_intersections(
        inwood_graph_projected,
        rebuild_graph=True,
        tolerance=20,
        dead_ends=False,
    )
    _, _ax = ox.plot.plot_graph(
        inwood_graph, node_size=0, edge_color="w", edge_linewidth=0.2
    )
    _ = _ax.axis("off")
    return (inwood_graph,)


@app.cell
def _(inwood_polygon):
    tags = {
        "shop": ["supermarket", "greengrocer", "farm"],
        "amenity": ["library"],
    }
    # polygon must be in unprojected latitude-longitude degrees (EPSG:4326)
    inwood_places = ox.features.features_from_polygon(inwood_polygon, tags)
    inwood_places
    return (inwood_places,)


@app.cell
def _(inwood_graph):
    inwood_graph_nodes, inwood_graph_streets = ox.graph_to_gdfs(inwood_graph)
    inwood_graph_streets.crs
    return inwood_graph_nodes, inwood_graph_streets


@app.cell
def _(inwood_places):
    inwood_places.crs
    return


@app.cell
def _(inwood_census_blocks):
    inwood_census_blocks.crs
    return


@app.cell
def _(inwood_census_blocks, inwood_graph_streets, inwood_places):
    inwood_places_projected = inwood_places.to_crs(inwood_graph_streets.crs)
    inwood_census_blocks_projected = inwood_census_blocks.to_crs(
        inwood_graph_streets.crs
    )
    return inwood_census_blocks_projected, inwood_places_projected


@app.cell
def _(
    inwood_census_blocks_projected,
    inwood_graph_streets,
    inwood_places_projected,
):
    _, _ax = plt.subplots(1, 1, figsize=(6, 6))
    _ax.set_title("Inwood, New York, NY\nPlaces, Census Blocks, Walkable Streets")
    inwood_places_projected.plot(
        ax=_ax,
        fc="green",
        ec="none",
        markersize=12,
    )
    inwood_graph_streets.plot(
        linewidth=0.25,
        ax=_ax,
        color="w",
        alpha=0.6,
    )
    inwood_census_blocks_projected.plot(
        "Pop1",
        cmap="copper",
        alpha=0.3,
        ax=_ax,
        linewidth=0.25,
        edgecolor="k",
    )
    _ax.axis(inwood_census_blocks_projected.total_bounds[[0, 2, 1, 3]])
    _ax.axis("off")
    _ax
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## Assign an intersection to each place
    """)
    return


@app.cell
def _(inwood_places_projected):
    inwood_places_projected
    return


@app.cell
def _():
    useful_feature_tags = ["name", "shop", "amenity"]
    return (useful_feature_tags,)


@app.cell
def _(inwood_places_projected):
    inwood_place_points = inwood_places_projected.representative_point()
    inwood_place_points
    return (inwood_place_points,)


@app.cell
def _(inwood_graph, inwood_place_points):
    nearest_nodes = ox.distance.nearest_nodes(
        inwood_graph, inwood_place_points.x, inwood_place_points.y
    )
    nearest_nodes
    return (nearest_nodes,)


@app.cell
def _(inwood_graph_nodes):
    inwood_graph_nodes
    return


@app.cell
def _(inwood_places_projected):
    inwood_places_projected.index
    return


@app.cell
def _(
    inwood_graph,
    inwood_places_projected,
    nearest_nodes,
    useful_feature_tags,
):
    inwood_graph_places = inwood_graph.copy()
    features = inwood_places_projected.reset_index()[
        ["id"] + useful_feature_tags
    ].to_dict(orient="records")
    for _node, _feature in zip(
        nearest_nodes,
        features,
    ):
        _feature = {k: v for k, v in _feature.items() if pd.notna(v)}
        inwood_graph_places.nodes[_node].update({"place": _feature})
    return (inwood_graph_places,)


@app.cell
def _(inwood_graph_places):
    _nodes, _edges = ox.convert.graph_to_gdfs(inwood_graph_places)
    _nodes["place"].value_counts()
    return


@app.cell
def _(inwood_places_projected):
    test_multi_place_nodes = pd.concat(
        [inwood_places_projected, inwood_places_projected]
    )
    test_multi_place_nodes
    return (test_multi_place_nodes,)


@app.cell
def _(inwood_graph, test_multi_place_nodes):
    test_graph = inwood_graph.copy()
    test_multi_place_points = test_multi_place_nodes.representative_point()
    test_multi_place_points
    return test_graph, test_multi_place_points


@app.cell
def _(
    test_graph,
    test_multi_place_nodes,
    test_multi_place_points,
    useful_feature_tags,
):
    _nearest_nodes = ox.distance.nearest_nodes(
        test_graph, test_multi_place_points.x, test_multi_place_points.y
    )
    _features = test_multi_place_nodes.reset_index()[
        ["id"] + useful_feature_tags
    ].to_dict(orient="records")
    for _node, _feature in zip(
        _nearest_nodes,
        _features,
    ):
        _feature = {k: v for k, v in _feature.items() if pd.notna(v)}
        _node_places = test_graph.nodes[_node].get("places")
        _node_places = [] if not _node_places else _node_places
        _feature["name"] = (
            _feature["name"] + " NEW"
            if len(_node_places) != 0
            else _feature["name"]
        )
        _node_places.append(_feature)
        test_graph.nodes[_node].update({"places": _node_places})
    _nodes, _edges = ox.convert.graph_to_gdfs(test_graph)
    _nodes
    _nodes["places"].value_counts()
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## Do isochrone stuff
    """)
    return


@app.cell
def _():
    from shapely.geometry import Point, LineString, Polygon
    return LineString, Point, Polygon


@app.cell
def _():
    travel_speed_mph = 3  # mph
    travel_speed_mpm = travel_speed_mph * 88  # miles per hour to feet per minute
    trip_times = [5, 10, 15]  # in minutes
    return travel_speed_mpm, trip_times


@app.cell
def _(trip_times):
    # get one color for each isochrone
    iso_colors = ox.plot.get_colors(n=len(trip_times), cmap="plasma", start=0)
    return (iso_colors,)


@app.cell
def _(inwood_graph_places, travel_speed_mpm):
    # add an edge attribute for time in minutes required to traverse each edge
    for _, _, _, data in inwood_graph_places.edges(data=True, keys=True):
        data["time"] = data["length"] / travel_speed_mpm
    return


@app.cell
def _(inwood_graph_places):
    _, _inwood_graph_streets = ox.graph_to_gdfs(inwood_graph_places)
    _ax = _inwood_graph_streets.plot(
        linewidth=0.25,
        column="time",
        alpha=0.6,
    )
    _ = _ax.axis("off")
    _ax
    return


@app.cell
def _(inwood_graph_places):
    _nodes = ox.convert.graph_to_gdfs(inwood_graph_places, edges=False)
    _x, _y = _nodes["geometry"].union_all().centroid.xy
    inwood_graph_places_center_node = ox.distance.nearest_nodes(
        inwood_graph_places, _x[0], _y[0]
    )
    return (inwood_graph_places_center_node,)


@app.cell
def _(
    inwood_graph_places,
    inwood_graph_places_center_node,
    iso_colors,
    trip_times,
):
    # color the nodes according to isochrone then plot the street network
    node_colors = {}
    for trip_time, color in zip(sorted(trip_times, reverse=True), iso_colors):
        subgraph = nx.ego_graph(
            inwood_graph_places,
            inwood_graph_places_center_node,
            radius=trip_time,
            distance="time",
        )
        for node in subgraph.nodes():
            node_colors[node] = color
    nc = [node_colors.get(node, "none") for node in inwood_graph_places.nodes()]
    ns = [15 if node in node_colors else 0 for node in inwood_graph_places.nodes()]
    fig, ax = ox.plot.plot_graph(
        inwood_graph_places,
        node_color=nc,
        node_size=ns,
        node_alpha=0.8,
        edge_linewidth=0.2,
        edge_color="#999999",
    )
    return


@app.cell
def _(
    Point,
    inwood_graph_places,
    inwood_graph_places_center_node,
    iso_colors,
    trip_times,
):
    # make the isochrone polygons
    isochrone_polys = []
    for _trip_time in sorted(trip_times, reverse=True):
        _subgraph = nx.ego_graph(
            inwood_graph_places,
            inwood_graph_places_center_node,
            radius=_trip_time,
            distance="time",
        )
        _node_points = [
            Point((data["x"], data["y"]))
            for node, data in _subgraph.nodes(data=True)
        ]
        _bounding_poly = gpd.GeoSeries(_node_points).union_all().convex_hull
        isochrone_polys.append(_bounding_poly)
    isochrones = gpd.GeoDataFrame(geometry=isochrone_polys)
    # plot the network then add isochrones as colored polygon patches
    _, _ax = ox.plot.plot_graph(
        inwood_graph_places,
        show=False,
        close=False,
        edge_color="#999999",
        edge_alpha=0.2,
        node_size=0,
    )
    isochrones.plot(ax=_ax, color=iso_colors, ec="none", alpha=0.6, zorder=-1)
    _ax
    return


@app.cell
def _(
    LineString,
    Point,
    Polygon,
    inwood_graph_places,
    inwood_graph_places_center_node,
    iso_colors,
    trip_times,
):
    # plot isochrones as buffers to get more faithful isochrones than convex hulls can offer
    def make_iso_polys(G, center_node, edge_buff=25, node_buff=50, infill=False):
        isochrone_polys = []
        for trip_time in sorted(trip_times, reverse=True):
            subgraph = nx.ego_graph(
                G, center_node, radius=trip_time, distance="time"
            )

            node_points = [
                Point((data["x"], data["y"]))
                for node, data in subgraph.nodes(data=True)
            ]
            nodes_gdf = gpd.GeoDataFrame(
                {"id": list(subgraph.nodes)}, geometry=node_points
            )
            nodes_gdf = nodes_gdf.set_index("id")

            edge_lines = []
            for n_fr, n_to in subgraph.edges():
                f = nodes_gdf.loc[n_fr].geometry
                t = nodes_gdf.loc[n_to].geometry
                edge_lookup = G.get_edge_data(n_fr, n_to)[0].get(
                    "geometry", LineString([f, t])
                )
                edge_lines.append(edge_lookup)

            n = nodes_gdf.buffer(node_buff).geometry
            e = gpd.GeoSeries(edge_lines).buffer(edge_buff).geometry
            all_gs = list(n) + list(e)
            new_iso = gpd.GeoSeries(all_gs).union_all()

            # try to fill in surrounded areas so shapes will appear solid and
            # blocks without white space inside them
            if infill:
                new_iso = Polygon(new_iso.exterior)
            isochrone_polys.append(new_iso)
        return isochrone_polys


    # make the isochrone polygons
    isochrone_buffer_polys = make_iso_polys(
        inwood_graph_places,
        inwood_graph_places_center_node,
        edge_buff=25,
        node_buff=0,
        infill=True,
    )
    isochrone_buffer_polys_gdf = gpd.GeoDataFrame(geometry=isochrone_buffer_polys)

    # plot the network then add isochrones as colored polygon patches
    _, _ax = ox.plot.plot_graph(
        inwood_graph_places,
        show=False,
        close=False,
        edge_color="#999999",
        edge_alpha=0.2,
        node_size=0,
    )
    isochrone_buffer_polys_gdf.plot(
        ax=_ax, color=iso_colors, ec="none", alpha=0.6, zorder=-1
    )
    return


if __name__ == "__main__":
    app.run()
