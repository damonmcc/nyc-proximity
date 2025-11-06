import marimo

__generated_with = "0.17.6"
app = marimo.App(width="medium")

with app.setup(hide_code=True):
    import marimo as mo
    from pathlib import Path
    import pandas as pd
    import geopandas as gpd
    from shapely import geometry
    import osmnx as ox
    import networkx as nx
    import h3
    import contextily as cx
    import matplotlib.pyplot as plt
    from matplotlib.ticker import MaxNLocator


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    # Access to libraries in uptown Manhattan
    """)
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## Get data
    """)
    return


@app.cell
def _():
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## Prepare data
    """)
    return


@app.cell
def _():
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## Calculate access
    """)
    return


@app.cell
def _():
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## Show tiles
    """)
    return


@app.cell
def _():
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    #
    """)
    return


if __name__ == "__main__":
    app.run()
