import marimo

__generated_with = "0.17.6"
app = marimo.App(width="medium", sql_output="pandas")

with app.setup:
    import marimo as mo
    import pandas as pd
    import pygris
    import matplotlib.pyplot as plt
    from pathlib import Path


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## Load census data
    """)
    return


@app.cell
def _():
    # assuming notebook was started from the repository root directory
    repository_root_directory = Path.cwd()
    repository_root_directory
    return (repository_root_directory,)


@app.cell
def _(repository_root_directory):
    # data from NYC Department of City Planning (https://www.nyc.gov/content/planning/pages/resources/datasets/decennial-census)
    nyc_decennialcensus_2020 = pd.read_csv(
        f"{repository_root_directory}/data/nyc_decennialcensus_2020.csv",
        thousands=",",
    )
    nyc_decennialcensus_2020
    return (nyc_decennialcensus_2020,)


@app.cell
def _(nyc_decennialcensus_2020):
    _df = mo.sql(
        f"""
        SELECT * FROM nyc_decennialcensus_2020
        """
    )
    return


@app.cell
def _(nyc_decennialcensus_2020):
    nyc_block_data = mo.sql(
        f"""
        SELECT * FROM nyc_decennialcensus_2020
        WHERE GeogType = 'CB2020'
        """
    )
    return (nyc_block_data,)


@app.cell
def _(nyc_decennialcensus_2020):
    _df = mo.sql(
        f"""
        SELECT * FROM nyc_decennialcensus_2020
        WHERE GeogType = 'CB2020' and GeogName = 'Manhattan'
        """
    )
    return


@app.cell
def _(nyc_decennialcensus_2020):
    _df = mo.sql(
        f"""
        SELECT distinct GeogName, FIPSCode FROM nyc_decennialcensus_2020
        WHERE GeogType = 'CB2020'
        """
    )
    return


@app.cell
def _(nyc_block_data):
    nyc_block_data["FIPSCODE_COUNTY"] = "36" + nyc_block_data["FIPSCode"].astype(
        str
    ).str.zfill(3)
    nyc_block_data["GEOID_KEY"] = (
        nyc_block_data["FIPSCODE_COUNTY"]
        + nyc_block_data["GeoID"].astype(str).str[1:]
    )
    nyc_block_data["GEOID_KEY"].value_counts().sort_index()
    return


@app.cell
def _(nyc_block_data):
    _df = mo.sql(
        f"""
        SELECT distinct GeogName, FIPSCODE_COUNTY FROM nyc_block_data
        WHERE GeogType = 'CB2020'
        """
    )
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## Load census geometries
    """)
    return


@app.cell
def _():
    manhattan_block_geometries = pygris.blocks(state="NY", county="New York")
    manhattan_block_geometries.plot()
    return (manhattan_block_geometries,)


@app.cell
def _(manhattan_block_geometries):
    manhattan_block_geometries
    return


@app.cell
def _(manhattan_block_geometries):
    manhattan_block_geometries["GEOID_KEY"] = manhattan_block_geometries[
        "GEOID20"
    ].astype(str)
    return


@app.cell
def _(manhattan_block_geometries):
    manhattan_block_geometries["GEOID_KEY"].value_counts().sort_index()
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## Join data and geometries
    """)
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ### Manhattan only
    """)
    return


@app.cell
def _(manhattan_block_geometries, nyc_block_data):
    manhattan_blocks = pd.merge(
        manhattan_block_geometries,
        nyc_block_data,
        left_on="GEOID_KEY",
        right_on="GEOID_KEY",
        how="left",
        indicator=True,
        validate="one_to_one",
    )
    manhattan_blocks
    return (manhattan_blocks,)


@app.cell
def _(manhattan_blocks):
    manhattan_blocks["_merge"].value_counts()
    return


@app.cell
def _(manhattan_blocks):
    _, _ax = plt.subplots(figsize=(7, 7))
    manhattan_blocks.plot(
        ax=_ax,
        column="Pop1",
        cmap="copper",
    )
    _ax.get_xaxis().set_visible(False)
    _ax.get_yaxis().set_visible(False)
    _ax
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ### All of NYC
    """)
    return


@app.cell
def _():
    m_block_geometries = pygris.blocks(state="NY", county="New York")
    m_block_geometries.plot()
    return (m_block_geometries,)


@app.cell
def _():
    bx_block_geometries = pygris.blocks(state="NY", county="Bronx")
    bx_block_geometries.plot()
    return (bx_block_geometries,)


@app.cell
def _(bx_block_geometries):
    bx_block_geometries
    return


@app.cell
def _():
    q_block_geometries = pygris.blocks(state="NY", county="Queens")
    q_block_geometries.plot()
    return (q_block_geometries,)


@app.cell
def _():
    bk_block_geometries = pygris.blocks(state="NY", county="Kings")
    bk_block_geometries.plot()
    return (bk_block_geometries,)


@app.cell
def _():
    staten_island_block_geometries = pygris.blocks(state="NY", county="Richmond")
    staten_island_block_geometries.plot()
    return (staten_island_block_geometries,)


@app.cell
def _(
    bk_block_geometries,
    bx_block_geometries,
    m_block_geometries,
    q_block_geometries,
    staten_island_block_geometries,
):
    nyc_block_geometries = pd.concat(
        [
            m_block_geometries,
            bx_block_geometries,
            q_block_geometries,
            bk_block_geometries,
            staten_island_block_geometries,
        ]
    )
    nyc_block_geometries.plot()
    return (nyc_block_geometries,)


@app.cell
def _(nyc_block_geometries):
    nyc_block_geometries
    return


@app.cell
def _(nyc_block_geometries):
    nyc_block_geometries["GEOID_KEY"] = nyc_block_geometries["GEOID20"].astype(str)
    return


@app.cell
def _(nyc_block_geometries, repository_root_directory):
    nyc_block_geometries.to_parquet(
        Path(repository_root_directory / "data" / "nyc_block_geometries.parquet")
    )
    return


@app.cell
def _(nyc_block_data, nyc_block_geometries):
    nyc_blocks = pd.merge(
        nyc_block_geometries,
        nyc_block_data,
        left_on="GEOID_KEY",
        right_on="GEOID_KEY",
        how="left",
        indicator=True,
        validate="one_to_one",
    )
    nyc_blocks
    return (nyc_blocks,)


@app.cell
def _(nyc_blocks):
    nyc_blocks["_merge"].value_counts()
    return


@app.cell
def _(nyc_blocks):
    _, _ax = plt.subplots(figsize=(7, 7))
    nyc_blocks.plot(
        ax=_ax,
        column="Pop1",
        cmap="copper",
    )
    _ax.get_xaxis().set_visible(False)
    _ax.get_yaxis().set_visible(False)
    _ax
    return


@app.cell
def _(nyc_blocks, repository_root_directory):
    nyc_blocks.to_parquet(
        Path(repository_root_directory / "data" / "nyc_blocks.parquet")
    )
    return


if __name__ == "__main__":
    app.run()
