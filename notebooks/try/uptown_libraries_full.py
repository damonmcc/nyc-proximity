import marimo

__generated_with = "0.17.6"
app = marimo.App(width="medium")

with app.setup:
    import marimo as mo
    import geopandas as gpd
    import osmnx as ox
    import networkx as nx
    import matplotlib.pyplot as plt
    from matplotlib.ticker import MaxNLocator
    from pathlib import Path


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    # Access to libraries in uptown Manhattan
    """)
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## Get and prepare data
    """)
    return


@app.cell
def _():
    DATA_DIRECTORY = Path("./data")
    return (DATA_DIRECTORY,)


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ### Census blocks
    """)
    return


@app.cell
def _(DATA_DIRECTORY):
    nyc_blocks = gpd.read_parquet(DATA_DIRECTORY / "nyc_blocks.parquet")
    return (nyc_blocks,)


@app.cell
def _(nyc_blocks):
    nyc_blocks["centroid"] = nyc_blocks.geometry.centroid
    return


@app.cell
def _(nyc_blocks):
    nyc_blocks
    return


@app.cell
def _(nyc_blocks):
    ref_lat = 40.84
    uptown_blocks = nyc_blocks[
        (nyc_blocks["GeogName"] == "Manhattan")
        & (nyc_blocks["centroid"].y > ref_lat)
    ]
    uptown_polygon = uptown_blocks.union_all()
    uptown_blocks
    return uptown_blocks, uptown_polygon


@app.cell
def _(uptown_blocks):
    uptown_blocks.plot()
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ### Streets
    """)
    return


@app.cell
def _(uptown_polygon):
    uptown_graph_raw = ox.graph.graph_from_polygon(
        uptown_polygon,
        truncate_by_edge=True,
        network_type="walk",
    )
    _, _ax = ox.plot.plot_graph(
        uptown_graph_raw, node_size=0, edge_color="w", edge_linewidth=0.2
    )
    _ = _ax.axis("off")
    return (uptown_graph_raw,)


@app.cell
def _(uptown_graph_raw):
    uptown_graph_projected = ox.projection.project_graph(
        uptown_graph_raw, to_crs="2263"
    )
    uptown_graph_projected.graph["crs"]
    return (uptown_graph_projected,)


@app.cell
def _(uptown_graph_projected):
    uptown_graph_consolidated = ox.simplification.consolidate_intersections(
        uptown_graph_projected,
        tolerance=30,  # feet
    )
    _, _ax = ox.plot.plot_graph(
        uptown_graph_consolidated, node_size=0, edge_color="w", edge_linewidth=0.2
    )
    _ = _ax.axis("off")
    return (uptown_graph_consolidated,)


@app.cell
def _(uptown_graph_consolidated):
    uptown_graph_crs2263 = uptown_graph_consolidated
    uptown_graph_crs4326 = ox.projection.project_graph(
        uptown_graph_consolidated, to_crs="4326"
    )
    uptown_graph_crs4326 = ox.distance.add_edge_lengths(uptown_graph_crs4326)
    return uptown_graph_crs2263, uptown_graph_crs4326


@app.cell
def _(uptown_graph_crs2263):
    uptown_graph_crs2263.graph["crs"]
    return


@app.cell
def _(uptown_graph_crs2263):
    _, _streets = ox.graph_to_gdfs(uptown_graph_crs2263)
    _streets
    return


@app.cell
def _(uptown_graph_crs4326):
    uptown_graph_crs4326.graph["crs"]
    return


@app.cell
def _(uptown_graph_crs4326):
    _, _streets = ox.graph_to_gdfs(uptown_graph_crs4326)
    _streets
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ### Places
    """)
    return


@app.cell
def _(uptown_polygon):
    tags = {
        "amenity": ["library"],
    }
    # polygon must be in unprojected latitude-longitude degrees (EPSG:4326)
    uptown_libraries = ox.features.features_from_polygon(uptown_polygon, tags)
    uptown_libraries
    return (uptown_libraries,)


@app.cell
def _(uptown_graph_crs2263, uptown_graph_crs4326, uptown_libraries):
    uptown_libraries["point_geometry"] = uptown_libraries.representative_point()
    uptown_libraries["nearest_node"] = ox.distance.nearest_nodes(
        uptown_graph_crs4326,
        uptown_libraries["point_geometry"].x,
        uptown_libraries["point_geometry"].y,
    )
    uptown_libraries_crs2263 = uptown_libraries.to_crs(
        uptown_graph_crs2263.graph["crs"]
    )
    _points_crs2263 = uptown_libraries["point_geometry"].to_crs(
        crs=uptown_graph_crs2263.graph["crs"]
    )
    uptown_libraries_crs2263["point_geometry"] = _points_crs2263

    uptown_libraries
    return (uptown_libraries_crs2263,)


@app.cell
def _(uptown_libraries_crs2263):
    uptown_libraries_crs2263
    return


@app.cell
def _(uptown_graph_crs4326):
    uptown_intersection, uptown_streets = ox.graph_to_gdfs(uptown_graph_crs4326)
    uptown_streets.crs
    return (uptown_streets,)


@app.cell
def _(uptown_blocks):
    uptown_blocks.crs
    return


@app.cell
def _(uptown_libraries):
    uptown_libraries.crs
    return


@app.cell
def _(uptown_blocks, uptown_libraries):
    uptown_blocks_projected = uptown_blocks.to_crs(uptown_libraries.crs)
    return (uptown_blocks_projected,)


@app.cell
def _(uptown_blocks_projected, uptown_libraries, uptown_streets):
    _, _ax = plt.subplots(1, 1, figsize=(6, 6))
    _ax.set_title(
        "Uptown, New York, NY\nLibraries, Census Blocks, Walkable Streets"
    )
    uptown_blocks_projected.plot(
        "Pop1",
        cmap="copper",
        alpha=0.3,
        ax=_ax,
        linewidth=0.25,
        edgecolor="k",
    )
    uptown_streets.plot(
        linewidth=0.25,
        ax=_ax,
        color="w",
        alpha=0.6,
    )
    uptown_libraries["point_geometry"].plot(
        ax=_ax,
        fc="green",
        ec="none",
        markersize=50,
    )
    _ax.axis(uptown_blocks_projected.total_bounds[[0, 2, 1, 3]])
    _ax.axis("off")
    _ax
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## Calculate access (miles and custom logic)
    """)
    return


@app.cell
def _():
    travel_speed_mph = 3  # mph
    trip_time = 15  # minutes
    travel_speed_fpm = travel_speed_mph * 88  # feet per minute
    travel_speed_fpm
    return travel_speed_fpm, travel_speed_mph, trip_time


@app.cell
def _(travel_speed_fpm, uptown_graph_crs2263):
    # add an edge attribute for time in minutes required to traverse each edge
    for _, _, _, _edges in uptown_graph_crs2263.edges(data=True, keys=True):
        _edges["time"] = _edges["length"] / travel_speed_fpm
    return


@app.cell
def _(uptown_graph_crs2263):
    _, _streets = ox.graph_to_gdfs(uptown_graph_crs2263)
    _streets
    return


@app.cell
def _(uptown_graph_crs2263):
    _, _streets = ox.graph_to_gdfs(uptown_graph_crs2263)
    _ax = _streets.plot(
        linewidth=0.25,
        column="time",
        alpha=0.6,
    )
    _ = _ax.axis("off")
    _ax
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ### Access from the center
    """)
    return


@app.cell
def _(uptown_graph_crs2263):
    _nodes = ox.convert.graph_to_gdfs(uptown_graph_crs2263, edges=False)
    _x, _y = _nodes["geometry"].union_all().centroid.xy
    uptown_graph_crs2263_center_node_id = ox.distance.nearest_nodes(
        uptown_graph_crs2263, _x[0], _y[0]
    )
    uptown_graph_crs2263_center_node_id
    return (uptown_graph_crs2263_center_node_id,)


@app.cell
def _(uptown_graph_crs2263, uptown_graph_crs2263_center_node_id):
    # 40°51'34.5"N 73°55'40.9"W
    uptown_graph_crs2263_center_node = uptown_graph_crs2263.nodes()[
        uptown_graph_crs2263_center_node_id
    ]
    uptown_graph_crs2263_center_node
    return


@app.cell
def _(trip_time, uptown_graph_crs2263, uptown_graph_crs2263_center_node_id):
    uptown_graph_crs2263_subgraph = nx.ego_graph(
        uptown_graph_crs2263,
        uptown_graph_crs2263_center_node_id,
        radius=trip_time,
        distance="time",
    )
    uptown_graph_crs2263_subgraph_colors = {}

    _node_in_subgraph_color = "#88aaaa"

    for _node in uptown_graph_crs2263_subgraph.nodes():
        uptown_graph_crs2263_subgraph_colors[_node] = _node_in_subgraph_color

    uptown_graph_crs2263_subgraph_node_colors = [
        uptown_graph_crs2263_subgraph_colors.get(node, "none")
        for node in uptown_graph_crs2263.nodes()
    ]
    return (
        uptown_graph_crs2263_subgraph_colors,
        uptown_graph_crs2263_subgraph_node_colors,
    )


@app.cell
def _(
    uptown_graph_crs2263,
    uptown_graph_crs2263_center_node_id,
    uptown_graph_crs2263_subgraph_colors,
    uptown_graph_crs2263_subgraph_node_colors,
):
    _node_sizes = [
        10 if node in uptown_graph_crs2263_subgraph_colors else 0
        for node in uptown_graph_crs2263.nodes()
    ]

    _, _ax = ox.plot.plot_graph(
        uptown_graph_crs2263,
        node_color=uptown_graph_crs2263_subgraph_node_colors,
        node_size=_node_sizes,
        node_alpha=0.8,
        edge_linewidth=0.2,
        edge_color="#999999",
        show=False,
    )
    ox.plot.plot_graph_route(
        uptown_graph_crs2263,
        [uptown_graph_crs2263_center_node_id],
        orig_dest_size=30,
        show=False,
        ax=_ax,
    )
    _ax
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ### Inspect results
    """)
    return


@app.cell
def _():
    # last_nearby_node_id = list(nearby_node_colors.keys())[-1]
    last_nearby_node_id = 239
    last_nearby_node_id
    return (last_nearby_node_id,)


@app.cell
def _(last_nearby_node_id, uptown_graph_crs4326):
    _last_nearby_node = uptown_graph_crs4326.nodes()[last_nearby_node_id]
    _last_nearby_node
    return


@app.cell
def _(
    last_nearby_node_id,
    uptown_graph_crs2263,
    uptown_graph_crs2263_center_node_id,
    uptown_graph_crs2263_subgraph_node_colors,
):
    _, _ax = ox.plot.plot_graph(
        uptown_graph_crs2263,
        node_color=uptown_graph_crs2263_subgraph_node_colors,
        edge_linewidth=0.2,
        edge_color="#999999",
        show=False,
    )
    ox.plot.plot_graph_route(
        uptown_graph_crs2263,
        [uptown_graph_crs2263_center_node_id],
        orig_dest_size=30,
        show=False,
        ax=_ax,
    )
    ox.plot.plot_graph_route(
        uptown_graph_crs2263,
        [last_nearby_node_id],
        orig_dest_size=30,
        show=False,
        ax=_ax,
    )
    _ax
    return


@app.cell
def _(
    last_nearby_node_id,
    uptown_graph_crs2263,
    uptown_graph_crs2263_center_node_id,
):
    # Google Maps says this is about a 20 minutes walk
    route_1 = ox.routing.shortest_path(
        uptown_graph_crs2263,
        uptown_graph_crs2263_center_node_id,
        last_nearby_node_id,
        weight="time",
    )
    route_1_time = int(
        sum(
            ox.routing.route_to_gdf(uptown_graph_crs2263, route_1, weight="time")[
                "time"
            ]
        )
    )
    route_1_time
    return (route_1,)


@app.cell
def _(route_1, uptown_graph_crs2263):
    _, _ = ox.plot.plot_graph_routes(
        uptown_graph_crs2263,
        routes=[route_1],
        route_colors=["r"],
        route_linewidth=6,
        node_size=0,
    )
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## Calculate Access (kilometers and built-in functions)
    """)
    return


@app.cell
def _(travel_speed_mph):
    travel_speed_kph = travel_speed_mph * 1.60934
    travel_speed_mpm = travel_speed_kph * 16.6667  # meters per minute
    travel_speed_mpm
    return (travel_speed_kph,)


@app.cell
def _(travel_speed_kph, uptown_graph_crs4326):
    uptown_graph_crs32118 = ox.projection.project_graph(
        uptown_graph_crs4326, to_crs="32118"
    )
    # uptown_graph_crs32118 = ox.distance.add_edge_lengths(uptown_graph_crs32118)
    # add speed_kph attribute expected by other osmnx functions
    nx.set_edge_attributes(
        uptown_graph_crs32118, values=travel_speed_kph, name="speed_kph"
    )
    # add edge travel time (seconds) to graph as new travel_time edge attributes
    uptown_graph_crs32118 = ox.add_edge_travel_times(uptown_graph_crs32118)
    uptown_graph_crs32118.graph["crs"]
    return (uptown_graph_crs32118,)


@app.cell
def _(uptown_graph_crs32118):
    _, _streets = ox.graph_to_gdfs(uptown_graph_crs32118)
    _streets
    return


@app.cell
def _(uptown_graph_crs32118):
    # fix results from necessary use of meter-based length, kilometer-based speed, and second-based travel time
    # add an edge attribute for time in minutes required to traverse each edge
    for _, _, _, _edges in uptown_graph_crs32118.edges(data=True, keys=True):
        _edges["travel_time_s"] = _edges["travel_time"]
        # _edges["travel_time_s"] = _edges["travel_time"] / 1000
        _edges["travel_time_m"] = _edges["travel_time_s"] / 60

    _, _streets = ox.graph_to_gdfs(uptown_graph_crs32118)
    _streets
    return


@app.cell
def _(uptown_graph_crs32118):
    _, _streets = ox.graph_to_gdfs(uptown_graph_crs32118)
    _ax = _streets.plot(
        linewidth=0.25,
        column="travel_time_m",
        alpha=0.6,
    )
    _ = _ax.axis("off")
    _ax
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ### Access from the center
    """)
    return


@app.cell
def _(uptown_graph_crs32118):
    _nodes = ox.convert.graph_to_gdfs(uptown_graph_crs32118, edges=False)
    _x, _y = _nodes["geometry"].union_all().centroid.xy
    uptown_graph_crs32118_center_node_id = ox.distance.nearest_nodes(
        uptown_graph_crs32118, _x[0], _y[0]
    )
    return (uptown_graph_crs32118_center_node_id,)


@app.cell
def _(trip_time, uptown_graph_crs32118, uptown_graph_crs32118_center_node_id):
    uptown_graph_crs32118_subgraph = nx.ego_graph(
        uptown_graph_crs32118,
        uptown_graph_crs32118_center_node_id,
        radius=trip_time,
        distance="time",
    )

    uptown_graph_crs32118_subgraph_colors = {}

    _node_in_subgraph_color = "#88aaaa"

    for _node in uptown_graph_crs32118_subgraph.nodes():
        uptown_graph_crs32118_subgraph_colors[_node] = _node_in_subgraph_color

    uptown_graph_crs32118_subgraph_node_colors = [
        uptown_graph_crs32118_subgraph_colors.get(node, "none")
        for node in uptown_graph_crs32118.nodes()
    ]
    return (
        uptown_graph_crs32118_subgraph_colors,
        uptown_graph_crs32118_subgraph_node_colors,
    )


@app.cell
def _(
    uptown_graph_crs32118,
    uptown_graph_crs32118_center_node_id,
    uptown_graph_crs32118_subgraph_colors,
    uptown_graph_crs32118_subgraph_node_colors,
):
    _node_sizes = [
        10 if node in uptown_graph_crs32118_subgraph_colors else 0
        for node in uptown_graph_crs32118.nodes()
    ]

    _, _ax = ox.plot.plot_graph(
        uptown_graph_crs32118,
        node_color=uptown_graph_crs32118_subgraph_node_colors,
        node_size=_node_sizes,
        node_alpha=0.8,
        edge_linewidth=0.2,
        edge_color="#999999",
        show=False,
    )
    ox.plot.plot_graph_route(
        uptown_graph_crs32118,
        [uptown_graph_crs32118_center_node_id],
        orig_dest_size=30,
        show=False,
        ax=_ax,
    )
    _ax
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ### Inspect results
    """)
    return


@app.cell
def _(
    last_nearby_node_id,
    uptown_graph_crs32118,
    uptown_graph_crs32118_center_node_id,
    uptown_graph_crs32118_subgraph_node_colors,
):
    _, _ax = ox.plot.plot_graph(
        uptown_graph_crs32118,
        node_color=uptown_graph_crs32118_subgraph_node_colors,
        edge_linewidth=0.2,
        edge_color="#999999",
        show=False,
    )
    ox.plot.plot_graph_route(
        uptown_graph_crs32118,
        [uptown_graph_crs32118_center_node_id],
        orig_dest_size=30,
        show=False,
        ax=_ax,
    )
    ox.plot.plot_graph_route(
        uptown_graph_crs32118,
        [last_nearby_node_id],
        orig_dest_size=30,
        show=False,
        ax=_ax,
    )
    _ax
    return


@app.cell
def _(
    last_nearby_node_id,
    uptown_graph_crs32118,
    uptown_graph_crs32118_center_node_id,
):
    # Google Maps says this is about a 20 minutes walk
    route_1_crs32118 = ox.routing.shortest_path(
        uptown_graph_crs32118,
        uptown_graph_crs32118_center_node_id,
        last_nearby_node_id,
        weight="travel_time",
    )
    route_1_crs32118_time = int(
        sum(
            ox.routing.route_to_gdf(
                uptown_graph_crs32118, route_1_crs32118, weight="travel_time"
            )["travel_time"]
        )
    )
    route_1_crs32118_time
    return (route_1_crs32118,)


@app.cell
def _(route_1_crs32118, uptown_graph_crs32118):
    _, _ = ox.plot.plot_graph_routes(
        uptown_graph_crs32118,
        routes=[route_1_crs32118],
        route_colors=["r"],
        route_linewidth=6,
        node_size=0,
    )
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## Custom vs built-in logic

    Both approaches seem to result in the same travel times/subgraphs.

    Custom logic using the foot-based CRS is less complicated and more explicit because the build-in logic has required column names, requires metric units, and uses conflicting units (seconds, meters, kilometers).
    """)
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## Calculate library access for all intersections

    For each library, get the nearby subgraph and update all nodes in it to include that library's details.
    """)
    return


@app.cell
def _(uptown_libraries):
    uptown_libraries
    return


@app.cell
def _(trip_time):
    trip_time_factor = 3 / 4  # minutes
    trip_time_adjusted = trip_time * trip_time_factor
    trip_time_adjusted
    return (trip_time_adjusted,)


@app.cell
def _(trip_time_adjusted, uptown_graph_crs2263, uptown_libraries):
    uptown_library_subgraphs = {}

    for _index, _row in uptown_libraries.reset_index().iterrows():
        uptown_library_subgraphs[_row["id"]] = nx.ego_graph(
            uptown_graph_crs2263,
            _row["nearest_node"],
            radius=trip_time_adjusted,
            distance="time",
        )
    uptown_library_subgraphs
    return (uptown_library_subgraphs,)


@app.cell
def _(uptown_graph_crs2263, uptown_library_subgraphs):
    # _, _ax = plt.subplots(1, 1, figsize=(6, 6))
    _ax = ox.graph_to_gdfs(uptown_graph_crs2263, nodes=False).plot(
        linewidth=0.25,
        # ax=_ax,
        color="w",
        alpha=0.6,
    )
    ox.graph_to_gdfs(uptown_library_subgraphs[275118436], edges=False).plot(
        ax=_ax,
        fc="green",
        ec="none",
        markersize=10,
    )
    _ = _ax.axis("off")
    _ax
    return


@app.cell
def _(uptown_graph_crs2263, uptown_libraries, uptown_library_subgraphs):
    _fig, _axs = plt.subplots(1, 3, figsize=(10, 5), sharex=True, sharey=True)
    _axis_idx = 0
    for _library_id, _ in uptown_library_subgraphs.items():
        _ax = _axs[_axis_idx]
        _library_name = uptown_libraries.xs(_library_id, level="id")["name"][0]
        _ax.set_title(_library_name)
        ox.graph_to_gdfs(uptown_graph_crs2263, nodes=False).plot(
            linewidth=0.25,
            ax=_ax,
            color="w",
            alpha=0.6,
        )
        ox.graph_to_gdfs(uptown_library_subgraphs[_library_id], edges=False).plot(
            ax=_ax,
            fc="green",
            ec="none",
            markersize=10,
        )
        _ax.axis("off")
        _axis_idx += 1
    _fig.tight_layout()
    _fig
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ### Add libraries to nodes they're near
    """)
    return


@app.cell
def _(uptown_libraries, uptown_library_subgraphs):
    def add_libraries_to_nodes(graph):
        for library_id, library_subgraph in uptown_library_subgraphs.items():
            library_name = uptown_libraries.xs(library_id, level="id")["name"][0]
            print(f"adding '{library_name}' nodes ...")
            for node in library_subgraph:
                node_places = graph.nodes[node].get("places", [])
                node_places.append(f"library:{library_name}")
                node_places = sorted(list(set(node_places)))
                graph.nodes[node].update({"places": node_places})
                graph.nodes[node].update({"places_count": len(node_places)})
        for node, data in graph.nodes(data=True):
            # print(data)
            if "places" not in data:
                graph.nodes[node]["places"] = []
                graph.nodes[node]["places_count"] = 0
            # if isinstance(data["places"], list):
            #     print("node has a places list!")
            #     continue
            # print(data["places"])
            # if "places" in data:
            # if data["places"] == "default_value":
            #     graph.nodes[node]["places"] = []
            # print("updated node!")
        return graph
    return (add_libraries_to_nodes,)


@app.cell
def _(uptown_graph_crs2263):
    uptown_graph = uptown_graph_crs2263.copy()
    return (uptown_graph,)


@app.cell
def _(add_libraries_to_nodes, uptown_graph):
    uptown_library_graph = add_libraries_to_nodes(uptown_graph)
    ox.graph_to_gdfs(uptown_library_graph, edges=False)
    return (uptown_library_graph,)


@app.cell
def _(uptown_library_graph):
    ox.graph_to_gdfs(uptown_library_graph, edges=False)[
        "places_count"
    ].value_counts(dropna=False)
    return


@app.cell
def _(uptown_library_graph):
    ox.graph_to_gdfs(uptown_library_graph, edges=False)[
        ["places", "places_count"]
    ].astype(str).value_counts(dropna=False)
    return


@app.cell
def _(uptown_graph_crs2263, uptown_libraries_crs2263, uptown_library_graph):
    _nodes, _ = ox.graph_to_gdfs(uptown_library_graph)

    _, _ax = plt.subplots(figsize=(10, 10))
    _ax.set_title(
        "Libraries within a 15-minute walk\nUptown, New York", fontsize=16
    )

    nodes_plot = ox.graph_to_gdfs(uptown_graph_crs2263, nodes=False).plot(
        linewidth=0.25,
        color="w",
        alpha=0.6,
        ax=_ax,
    )

    _cmap = "Reds_r"
    _ax = _nodes.plot(
        label="Intersections",
        column="places_count",
        cmap=_cmap,
        ec="none",
        markersize=10,
        ax=_ax,
    )

    uptown_libraries_crs2263["point_geometry"].plot(
        ax=_ax,
        fc="green",
        ec="none",
        markersize=50,
    )

    _color_bar = plt.colorbar(
        _ax.collections[1],
        ax=_ax,
        orientation="vertical",
        shrink=0.2,
        aspect=15,
    )

    _color_bar.ax.yaxis.set_major_locator(MaxNLocator(integer=True))
    _color_bar.ax.tick_params(labelsize=5)

    _ = _ax.axis("off")
    _ax
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## Aggregate to hexagon tiles
    """)
    return


@app.cell
def _(uptown_library_graph):
    uptown_library_access_nodes_crs2263 = ox.graph_to_gdfs(
        uptown_library_graph, edges=False
    )
    uptown_library_access_nodes_crs4326 = (
        uptown_library_access_nodes_crs2263.to_crs("4326")
    ).reset_index()
    uptown_library_access_nodes_crs4326
    return (uptown_library_access_nodes_crs4326,)


@app.cell
def _(uptown_library_access_nodes_crs4326):
    import h3

    resolution = 9
    cell_id_col = f"h3_{resolution}"
    uptown_library_access_nodes_crs4326[cell_id_col] = (
        uptown_library_access_nodes_crs4326.apply(
            lambda row: str(
                h3.latlng_to_cell(row.geometry.y, row.geometry.x, resolution)
            ),
            axis=1,
        )
    )
    uptown_library_access_nodes_crs4326
    return cell_id_col, h3, resolution


@app.cell
def _(cell_id_col, uptown_library_access_nodes_crs4326):
    tile_counts = (
        uptown_library_access_nodes_crs4326.groupby(cell_id_col)
        .count()
        .rename(columns={"geometry": "point_count"})
    )
    # tile_counts
    tile_aggregations = (
        uptown_library_access_nodes_crs4326.groupby(cell_id_col)
        .agg(
            total_intersections=("osmid", "sum"),
            total_places=("places_count", "sum"),
            average_places=("places_count", "mean"),
        )
        .reset_index()
    )
    tile_aggregations
    return (tile_aggregations,)


@app.cell
def _(h3, resolution, uptown_polygon):
    cells_from_geo = h3.geo_to_cells(uptown_polygon, resolution)
    h3shape_from_cells = h3.cells_to_h3shape(cells_from_geo)
    cell_area_gdf = gpd.GeoDataFrame(
        {"geometry": [h3shape_from_cells]}, crs="EPSG:4326"
    )
    cell_area_gdf.plot()
    return (cells_from_geo,)


@app.cell
def _(h3):
    from shapely import geometry


    def cell_to_shapely(cell):
        coords = h3.cell_to_boundary(cell)
        flipped = tuple(coord[::-1] for coord in coords)
        return geometry.Polygon(flipped)
    return (cell_to_shapely,)


@app.cell
def _(cell_to_shapely, cells_from_geo):
    cells_gdf = gpd.GeoDataFrame({"cell_id": cells_from_geo})
    cells_geoms = cells_gdf["cell_id"].apply(lambda x: cell_to_shapely(x))
    cells_geoms = gpd.GeoDataFrame(data=cells_gdf, geometry=cells_geoms, crs=4326)
    cells_geoms
    return (cells_geoms,)


@app.cell
def _(cell_id_col, cells_geoms, tile_aggregations):
    import pandas as pd

    tile_results = pd.merge(
        cells_geoms,
        tile_aggregations,
        left_on="cell_id",
        right_on=cell_id_col,
        how="left",
    )
    tile_results
    return (tile_results,)


@app.cell
def _(tile_results):
    import contextily as cx

    _, _ax = plt.subplots(figsize=(7, 7))
    _ax.set_title(
        "Libraries within a 15-minute walk\nUptown, New York", fontsize=16
    )
    tile_results.plot(
        ax=_ax,
        column="average_places",
        cmap="Reds_r",
        # edgecolor="k",
        alpha=0.6,
    )
    # _ax.get_xaxis().set_visible(False)
    # _ax.get_yaxis().set_visible(False)
    _ax.axis("off")

    _color_bar = plt.colorbar(
        _ax.collections[0],
        ax=_ax,
        orientation="vertical",
        shrink=0.2,
        aspect=15,
    )
    _color_bar.ax.yaxis.set_major_locator(MaxNLocator(integer=True))
    _color_bar.ax.tick_params(labelsize=10)

    cx.add_basemap(_ax, crs=tile_results.crs, source=cx.providers.CartoDB.Positron)
    _ax
    return


if __name__ == "__main__":
    app.run()
