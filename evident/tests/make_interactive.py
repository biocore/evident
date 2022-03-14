import os

import click
import pandas as pd
from skbio import DistanceMatrix

from evident import AlphaDiversityHandler, BetaDiversityHandler
from evident.interactive import create_bokeh_app


@click.command()
@click.option("--output", type=click.Path())
@click.option("--diversity-type", type=str, default="alpha")
@click.option("--exist-ok", type=bool, default=False)
def interactive(output, diversity_type, exist_ok):
    na_vals = ["missing: not provided", "not applicable"]
    curr_path = os.path.dirname(__file__)
    fname = os.path.join(curr_path, "data/metadata.tsv")
    df = pd.read_table(fname, sep="\t", index_col=0, na_values=na_vals)

    if diversity_type == "alpha":
        dh = AlphaDiversityHandler(df["faith_pd"], df)
    elif diversity_type == "beta":
        dm_loc = os.path.join(curr_path, "data/distance_matrix.lsmat.gz")
        dm = DistanceMatrix.read(dm_loc)
        dh = BetaDiversityHandler(dm, df)
    else:
        raise ValueError("No valid data!")

    create_bokeh_app(dh, output, exist_ok=exist_ok)


if __name__ == "__main__":
    interactive()
