import os
import glob

import numpy as np
import pandas as pd
import pytest

from evident.interactive import create_bokeh_app


@pytest.mark.parametrize("mock", ["alpha_mock", "beta_mock"])
def test_interactive(mock, request, tmpdir):
    dh = request.getfixturevalue(mock)
    na_vals = ["missing: not provided", "not applicable"]
    dh.metadata = dh.metadata.replace({x: np.nan for x in na_vals})
    dh.metadata = dh.metadata.dropna(axis=1, how="all")
    dh.metadata = dh.metadata.dropna(axis=0, how="any")

    outdir = f"{tmpdir}/{mock}"
    create_bokeh_app(dh, f"{outdir}")
    files = glob.glob(f"{outdir}/**/*", recursive=True)
    files = set([os.path.relpath(x, start=outdir) for x in files])

    exp_files = {
        "templates",
        "main.py",
        "data",
        "templates/index.html",
        "data/metadata.tsv"
    }
    if mock == "alpha_mock":
        exp_files.add("data/diversity.alpha.tsv")
    else:
        exp_files.add("data/diversity.beta.lsmat")
    assert files == exp_files

    md = pd.read_table(os.path.join(outdir, "data/metadata.tsv"), sep="\t",
                       index_col=0)
    exp_cols = [
        "cd_behavior",
        "cd_location",
        "cd_resection",
        "ibd_subtype",
        "perianal_disease",
        "sex",
        "classification"
    ]
    assert (exp_cols == md.columns).all()
