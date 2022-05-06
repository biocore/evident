import os
import shutil

from evident.data_handler import (_BaseDataHandler,
                                       UnivariateDataHandler,
                                       BivariateDataHandler)


def create_bokeh_app(
    data_handler: _BaseDataHandler,
    output: os.PathLike,
) -> None:
    """Creates interactive power analysis using Bokeh.

    :param data_handler: Handler with diversity data
    :type data_handler: evident.data_handler._BaseDataHandler

    :param output: Location to create Bokeh app
    :type output: os.PathLike
    """
    curr_path = os.path.dirname(__file__)
    support_files = os.path.join(curr_path, "support_files")

    # Copy support files (Bokeh template + script) and data directory
    shutil.copytree(support_files, output)
    data_dir = os.path.join(output, "data")
    os.mkdir(data_dir)

    md = data_handler.metadata.copy()
    md_loc = os.path.join(data_dir, "metadata.tsv")
    md.to_csv(md_loc, sep="\t", index=True)

    data = data_handler.data
    if isinstance(data_handler, UnivariateDataHandler):
        data_loc = os.path.join(data_dir, "diversity.alpha.tsv")
        data.to_csv(data_loc, sep="\t", index=True)
    elif isinstance(data_handler, BivariateDataHandler):
        data_loc = os.path.join(data_dir, "diversity.beta.lsmat")
        data.write(data_loc)
    else:
        raise ValueError("No valid data found!")
