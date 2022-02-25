import pandas as pd

from evident.diversity_handler import _BaseDiversityHandler


def effect_size_by_category(
    diversity_handler: _BaseDiversityHandler,
    columns: list = None
):
    dh = diversity_handler
    effect_size_dict = dict()
    for col in columns:
        num_choices = len(dh.metadata[col].unique())
        effect_size = dh.calculate_effect_size(col)
        if num_choices == 2:
            metric = "cohens_d"
        else:
            metric = "cohens_f"
        effect_size_dict[col] = {"metric": metric, "value": effect_size}

    return pd.DataFrame.from_dict(effect_size_dict, orient="index")
