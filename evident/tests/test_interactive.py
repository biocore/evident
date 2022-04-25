import os
import glob

import pandas as pd
import pytest

from evident.interactive import create_bokeh_app


@pytest.mark.parametrize("mock", ["alpha_mock", "beta_mock"])
def test_interactive(mock, request, tmpdir):
    outdir = f"{tmpdir}/{mock}"

    with pytest.warns(UserWarning) as warn_info:
        dh = request.getfixturevalue(mock)
        create_bokeh_app(dh, f"{outdir}")

    exp_msg_1 = (
        "Some categories have been dropped because they had either only "
        "one level or too many. Use the max_levels_per_category "
        "argument to modify this threshold."
    )
    assert exp_msg_1 in warn_info[0].message.args[0]

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
