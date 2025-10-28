import marimo

__generated_with = "0.17.2"
app = marimo.App(width="medium")

with app.setup:
    import marimo as mo
    import h3
    import pandas as pd
    import geopandas
    from shapely import geometry
    import contextily as cx
    import matplotlib.pyplot as plt
    import pygris


@app.cell
def _():
    # plotting helper functions to visualize the shapes
    def plot_df(df, column=None, ax=None):
        "Plot based on the `geometry` column of a GeoPandas dataframe"
        df = df.copy()

        if ax is None:
            _, ax = plt.subplots(figsize=(8, 8))
        ax.get_xaxis().set_visible(False)
        ax.get_yaxis().set_visible(False)

        df.plot(
            ax=ax,
            alpha=0.5,
            edgecolor="k",
            column=column,
            categorical=True,
            legend=True,
            legend_kwds={"loc": "upper left"},
        )
        cx.add_basemap(ax, crs=df.crs, source=cx.providers.CartoDB.Positron)
        return ax


    def plot_shape(shape, ax=None):
        df = geopandas.GeoDataFrame({"geometry": [shape]}, crs="EPSG:4326")
        ax = plot_df(df, ax=ax)
        return ax


    def plot_cells(cells, ax=None):
        shape = h3.cells_to_h3shape(cells)
        plot_shape(shape, ax=ax)
        return ax


    def plot_geo_and_cells(geo, resolution=9):
        fig, axs = plt.subplots(1, 2, figsize=(10, 5), sharex=True, sharey=True)
        plot_shape(geo, ax=axs[0])
        plot_cells(h3.geo_to_cells(geo, resolution), ax=axs[1])
        fig.tight_layout()
        return fig


    def plot_shape_and_cells(shape, resolution=9):
        fig, axs = plt.subplots(1, 2, figsize=(10, 5), sharex=True, sharey=True)
        plot_shape(shape, ax=axs[0])
        plot_cells(h3.h3shape_to_cells(shape, resolution), ax=axs[1])
        fig.tight_layout()
        return fig
    return plot_df, plot_geo_and_cells, plot_shape


@app.cell(hide_code=True)
def _():
    mo.md(r"""## Make hexagons based on census tracts""")
    return


@app.cell
def _():
    nyc_tracts = pygris.tracts(state="NY", county="New York")
    return (nyc_tracts,)


@app.cell
def _(nyc_tracts):
    nyc_tracts_union = nyc_tracts.union_all()
    nyc_tracts_hull = nyc_tracts_union.convex_hull
    return (nyc_tracts_union,)


@app.cell
def _(nyc_tracts_union, plot_shape):
    _ax = plot_shape(nyc_tracts_union)
    _ax
    return


@app.cell
def _(nyc_tracts_union, plot_geo_and_cells):
    plot_geo_and_cells(nyc_tracts_union, 7)
    return


@app.cell
def _(nyc_tracts_union, plot_geo_and_cells):
    plot_geo_and_cells(nyc_tracts_union, 9)
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""## Inspect and hexagons""")
    return


@app.cell
def _(nyc_tracts_union):
    nyc_tracts_cells = h3.geo_to_cells(nyc_tracts_union, 9)
    nyc_tracts_cells
    return (nyc_tracts_cells,)


@app.function
def cell_to_shapely(cell):
    coords = h3.cell_to_boundary(cell)
    flipped = tuple(coord[::-1] for coord in coords)
    return geometry.Polygon(flipped)


@app.cell
def _(nyc_tracts_cells):
    cells_df = geopandas.GeoDataFrame({"cell_id": nyc_tracts_cells})
    cells_df
    return (cells_df,)


@app.cell
def _(cells_df):
    cells_df_geoms = cells_df["cell_id"].apply(lambda x: cell_to_shapely(x))
    cells_gdf = geopandas.GeoDataFrame(
        data=cells_df, geometry=cells_df_geoms, crs=4326
    )
    cells_gdf
    return (cells_gdf,)


@app.cell
def _(cells_gdf, plot_df):
    plot_df(cells_gdf)
    return


@app.cell
def _(nyc_tracts_cells):
    cells_shape = h3.cells_to_h3shape(nyc_tracts_cells)
    cells_geo = h3.cells_to_geo(nyc_tracts_cells)
    return cells_geo, cells_shape


@app.cell
def _(cells_shape):
    cells_shape
    return


@app.cell
def _(cells_geo):
    cells_geo
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""## Points in hexagons""")
    return


@app.cell
def _():
    resolution = 8
    return (resolution,)


@app.cell
def _(nyc_tracts_union, resolution):
    nyc_tracts_cells_for_points = h3.geo_to_cells(nyc_tracts_union, resolution)
    cell_shape_for_points = h3.cells_to_h3shape(nyc_tracts_cells_for_points)
    cell_area_gdf_for_points = geopandas.GeoDataFrame(
        {"geometry": [cell_shape_for_points]}, crs="EPSG:4326"
    )
    cell_area_gdf_for_points.plot()
    return cell_area_gdf_for_points, nyc_tracts_cells_for_points


@app.cell
def _(nyc_tracts_cells_for_points):
    cells_gdf_for_points = geopandas.GeoDataFrame(
        {"cell_id": nyc_tracts_cells_for_points}
    )
    cells_geoms_for_points = cells_gdf_for_points["cell_id"].apply(
        lambda x: cell_to_shapely(x)
    )
    cells_geoms_for_points = geopandas.GeoDataFrame(
        data=cells_gdf_for_points, geometry=cells_geoms_for_points, crs=4326
    )
    cells_geoms_for_points
    return (cells_geoms_for_points,)


@app.cell
def _(cell_area_gdf_for_points):
    sampled_points_multipoint = cell_area_gdf_for_points.geometry.sample_points(
        1000, seed=1
    )
    random_points = geopandas.GeoDataFrame(
        geometry=sampled_points_multipoint, crs=cell_area_gdf_for_points.crs
    ).explode(ignore_index=True)
    random_points.plot()
    return (random_points,)


@app.cell
def _(random_points, resolution):
    cell_id_col = f"h3_{resolution}"
    random_points[cell_id_col] = random_points.apply(
        lambda row: str(
            h3.latlng_to_cell(row.geometry.y, row.geometry.x, resolution)
        ),
        axis=1,
    )
    random_points
    return (cell_id_col,)


@app.cell
def _(cell_id_col, random_points):
    cell_pount_counts = (
        random_points.groupby(cell_id_col)
        .count()
        .rename(columns={"geometry": "point_count"})
    )
    cell_pount_counts
    return (cell_pount_counts,)


@app.cell
def _(cell_id_col, cell_pount_counts, cells_geoms_for_points):
    cell_results = pd.merge(
        cells_geoms_for_points,
        cell_pount_counts,
        left_on="cell_id",
        right_on=cell_id_col,
        how="left",
    )
    cell_results
    return (cell_results,)


@app.cell
def _(cell_results):
    _, _ax = plt.subplots(figsize=(7, 7))
    cell_results.plot(
        ax=_ax,
        alpha=0.5,
        edgecolor="k",
        column="point_count",
        legend=True,
    )
    _ax.get_xaxis().set_visible(False)
    _ax.get_yaxis().set_visible(False)
    cx.add_basemap(_ax, crs=cell_results.crs, source=cx.providers.CartoDB.Positron)
    _ax
    return


if __name__ == "__main__":
    app.run()
