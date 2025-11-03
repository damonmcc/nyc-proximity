import marimo

__generated_with = "0.17.6"
app = marimo.App(width="medium")

with app.setup:
    import marimo as mo
    import geopandas as gpd
    import matplotlib.pyplot as plt
    from pathlib import Path


@app.cell
def _():
    DATA_DIRECTORY = Path("./data")
    return (DATA_DIRECTORY,)


@app.cell
def _(DATA_DIRECTORY):
    nyc_blocks = gpd.read_parquet(DATA_DIRECTORY / "nyc_blocks.parquet")
    nyc_blocks
    return (nyc_blocks,)


@app.cell
def _(nyc_blocks):
    nyc_blocks[nyc_blocks["POP20"] != nyc_blocks["Pop1"]]
    return


@app.cell
def _(nyc_blocks):
    nyc_blocks_projected = nyc_blocks.to_crs("2263")
    nyc_blocks_projected["block_area_ft2"] = nyc_blocks_projected.area.round(0).astype(int)
    nyc_blocks_projected["block_area_ft2"]
    return (nyc_blocks_projected,)


@app.cell
def _(nyc_blocks_projected):
    nyc_blocks_projected
    return


@app.cell
def _(nyc_blocks_projected):
    nyc_blocks_projected_has_land = nyc_blocks_projected[nyc_blocks_projected["ALAND20"] != 0]
    nyc_blocks_projected_has_land
    return (nyc_blocks_projected_has_land,)


@app.cell
def _(nyc_blocks_projected_has_land):
    _, _ax = plt.subplots(figsize=(7, 7))
    nyc_blocks_projected_has_land.plot(
        ax=_ax,
        column="block_area_ft2",
        # cmap="copper_r",
    )
    _ax.get_xaxis().set_visible(False)
    _ax.get_yaxis().set_visible(False)
    _ax
    return


@app.cell
def _(nyc_blocks_projected_has_land):
    _, _ax = plt.subplots(figsize=(7, 7))
    nyc_blocks_projected_has_land.plot(
        ax=_ax,
        column="block_area_ft2",
        cmap="copper",
    )
    _ax.get_xaxis().set_visible(False)
    _ax.get_yaxis().set_visible(False)
    _ax
    return


@app.cell
def _(nyc_blocks_projected_has_land):
    _, _ax = plt.subplots(figsize=(7, 7))
    nyc_blocks_projected_has_land.plot(
        ax=_ax,
        column="Pop1",
        # cmap="copper_r",
    )
    _ax.get_xaxis().set_visible(False)
    _ax.get_yaxis().set_visible(False)
    _ax
    return


if __name__ == "__main__":
    app.run()
