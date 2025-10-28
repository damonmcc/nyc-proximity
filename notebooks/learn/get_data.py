import marimo

__generated_with = "0.17.2"
app = marimo.App(width="medium")

with app.setup:
    import marimo as mo
    import geopandas as gpd
    import pygris
    import osmnx as ox
    import matplotlib.pyplot as plt


@app.cell(hide_code=True)
def _():
    mo.md(r"""## Get census data""")
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""Tracts""")
    return


@app.cell
def _():
    nyc_tracts = pygris.tracts(state="NY", county="New York")
    nyc_tracts_carto = pygris.tracts(state="NY", county="New York", cb=True)
    return nyc_tracts, nyc_tracts_carto


@app.cell
def _(nyc_tracts):
    nyc_tracts.plot()
    return


@app.cell
def _(nyc_tracts_carto):
    nyc_tracts_carto.plot()
    return


@app.cell
def _(nyc_tracts):
    len(nyc_tracts)
    return


@app.cell
def _(nyc_tracts_carto):
    len(nyc_tracts_carto)
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""Blocks""")
    return


@app.cell
def _():
    nyc_blocks = pygris.blocks(state="NY", county="New York")
    nyc_blocks.plot()
    return (nyc_blocks,)


@app.cell
def _(nyc_blocks):
    nyc_blocks
    return


@app.cell
def _():
    # list compiled via NYC Population Factfinder (https://popfactfinder.planning.nyc.gov)
    census_block_ids = [
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
    return (census_block_ids,)


@app.cell
def _(census_block_ids):
    census_block_ids_fixed = ["3606" + x for x in census_block_ids]
    census_block_ids_fixed[0]
    return (census_block_ids_fixed,)


@app.cell
def _(census_block_ids_fixed, nyc_blocks):
    focus_nyc_blocks = nyc_blocks[
        nyc_blocks["GEOID20"].isin(census_block_ids_fixed)
    ]
    focus_nyc_blocks.plot()
    return (focus_nyc_blocks,)


@app.cell
def _(focus_nyc_blocks):
    focus_nyc_blocks
    return


@app.cell
def _(focus_nyc_blocks):
    focus_area_polygon = focus_nyc_blocks.union_all().convex_hull
    focus_area = gpd.GeoDataFrame(
        geometry=[focus_area_polygon], crs=focus_nyc_blocks.crs
    )
    focus_area.plot()
    return (focus_area_polygon,)


@app.cell(hide_code=True)
def _():
    mo.md(r"""## Get networks""")
    return


@app.cell
def _():
    area_graph = ox.graph.graph_from_address(
        "4881 Broadway, New York, NY",
        dist=500,
        dist_type="network",
        network_type="walk",
        simplify=True,
    )
    return (area_graph,)


@app.cell
def _(area_graph):
    area_proj = ox.projection.project_graph(area_graph)
    _, _ax = ox.plot.plot_graph(
        area_proj, node_size=0, edge_color="w", edge_linewidth=0.2
    )
    return (area_proj,)


@app.cell
def _(area_proj):
    len(area_proj)
    return


@app.cell
def _(area_proj):
    area_consolidated = ox.simplification.consolidate_intersections(
        area_proj,
        rebuild_graph=True,
        tolerance=10,
        dead_ends=False,
    )
    len(area_consolidated)
    return (area_consolidated,)


@app.cell
def _(area_consolidated):
    _, _ax = ox.plot.plot_graph(
        area_consolidated, node_size=0, edge_color="w", edge_linewidth=0.2
    )
    _ = _ax.axis("off")
    return


@app.cell
def _(focus_area_polygon):
    focus_area_graph_raw = ox.graph.graph_from_polygon(
        focus_area_polygon, truncate_by_edge=True
    )
    _, _ax = ox.plot.plot_graph(
        focus_area_graph_raw, node_size=0, edge_color="w", edge_linewidth=0.2
    )
    _ = _ax.axis("off")
    return (focus_area_graph_raw,)


@app.cell
def _(focus_area_graph_raw):
    len(focus_area_graph_raw)
    return


@app.cell
def _(focus_area_graph_raw):
    focus_area_graph = ox.simplification.consolidate_intersections(
        ox.projection.project_graph(focus_area_graph_raw),
        rebuild_graph=True,
        tolerance=10,
        dead_ends=False,
    )
    len(focus_area_graph)
    return (focus_area_graph,)


@app.cell
def _(focus_area_graph):
    _, _ax = ox.plot.plot_graph(
        focus_area_graph, node_size=0, edge_color="w", edge_linewidth=0.2
    )
    _ = _ax.axis("off")
    return


@app.cell
def _(focus_area_graph):
    focus_area_nodes, focus_area_streets = ox.graph_to_gdfs(focus_area_graph)
    return (focus_area_streets,)


@app.cell
def _():
    # G_simple = ox.graph.graph_from_place(
    #     "Staten Island, New York, USA", network_type="walk", simplify=True
    # )
    # fig_simple, ax_simple = ox.plot.plot_graph(G_simple)
    return


@app.cell
def _():
    # filepath = "./data/piedmont.graphml"
    # ox.io.save_graphml(G, filepath)
    # # G = ox.io.load_graphml(filepath)
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""## Get places""")
    return


@app.cell
def _(focus_area_polygon):
    tags = {
        "shop": ["supermarket", "greengrocer", "farm"],
        "amenity": ["library"],
    }
    # polygon must be in unprojected latitude-longitude degrees (EPSG:4326)
    focus_area_places = ox.features.features_from_polygon(focus_area_polygon, tags)
    return (focus_area_places,)


@app.cell
def _(focus_area_places):
    focus_area_places
    return


@app.cell
def _(focus_area_places):
    focus_area_places.plot()
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""## Map all elements""")
    return


@app.cell
def _(focus_nyc_blocks):
    focus_nyc_blocks.crs
    return


@app.cell
def _(focus_area_streets):
    focus_area_streets.crs
    return


@app.cell
def _(focus_area_places):
    focus_area_places.crs
    return


@app.cell
def _(focus_area_places, focus_area_streets, focus_nyc_blocks):
    focus_nyc_blocks_projected = focus_nyc_blocks.to_crs(focus_area_places.crs)
    focus_area_streets_projected = focus_area_streets.to_crs(focus_area_places.crs)
    return focus_area_streets_projected, focus_nyc_blocks_projected


@app.cell
def _(
    focus_area_places,
    focus_area_streets_projected,
    focus_nyc_blocks_projected,
):
    _f, _ax = plt.subplots(1, 1, figsize=(6, 6))
    _ax.set_title("Inwood, New York, NY\nPlaces, Census Blocks, Walkable Streets")
    focus_area_places.plot(
        ax=_ax,
        fc="green",
        ec="none",
        markersize=12,
    )
    focus_area_streets_projected.plot(
        linewidth=0.25,
        ax=_ax,
        color="w",
        alpha=0.6,
    )
    focus_nyc_blocks_projected.plot(
        "POP20",
        cmap="copper",
        alpha=0.3,
        ax=_ax,
        linewidth=0.25,
        edgecolor="k",
    )
    _ax.axis(focus_nyc_blocks_projected.total_bounds[[0, 2, 1, 3]])
    _ax.axis("off")
    _ax
    return


if __name__ == "__main__":
    app.run()
