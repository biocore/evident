
# -----------------------------------------------------------------------------
# Copyright (c) 2018, The Evident Development Team.
#
# Distributed under the terms of the BSD 3-clause License.
#
# The full license is in the file LICENSE, distributed with this software.
# -----------------------------------------------------------------------------

import joblib
import pickle

import pandas as pd
import numpy as np

from os.path import join, basename, exists

from itertools import combinations
from functools import partial
from skbio import DistanceMatrix
from scipy.stats import mannwhitneyu
from skbio.stats.distance import permanova


def effect_size(mappings, alphas, betas, output, jobs, permutations,
                overwrite, na_values):
    # As we can have multiple mapping, alpha or beta files, we will construct
    # a mfs dictionary with all the dataframes. Additionally, we will load the
    # data_dictionary.csv file so we can use it to process the data
    mappings = {f: pd.read_csv(f, sep='\t', dtype=str, na_values=na_values)
                for f in mappings}
    for m, mf in mappings.items():
        mappings[m].set_index('#SampleID', inplace=True)
    if betas:
        betas = {f: DistanceMatrix.read(f) for f in betas}
        print(
            'maps: %d, betas: %d, cols: %s' % (
                len(mappings), len(betas), [
                    len(m.columns.values) for _, m in mappings.items()]))

        with joblib.parallel.Parallel(n_jobs=jobs, verbose=100) as par:
            par(joblib.delayed(
                _process_column)(bf, c, fname, alphas, betas, permutations)
                for bf, c, fname in _generate_betas(
                betas, mappings, permutations, output, overwrite))
    else:
        alphas = {f: pd.read_csv(f, sep='\t', dtype=str, na_values=na_values)
                  for f in alphas}
        for a, af in alphas.items():
            alphas[a].set_index('#SampleID', inplace=True)

        for af, c, fname in _generate_alphas(alphas, mappings,
                                             output, overwrite):
            _process_column(af, c, fname, alphas, betas, permutations)


def _beta(permutations, data, xvalues, yvalues):
    x_ids = list(xvalues.index.values)
    y_ids = list(yvalues.index.values)
    ids = x_ids + y_ids
    data_test = data.filter(ids)
    permanova_result = permanova(
        distance_matrix=data_test,
        # we can use use either x or y cause they are the same
        column=xvalues.name,
        grouping=pd.concat([xvalues, yvalues]).to_frame(),
        permutations=permutations).to_dict()
    xvals = list(
        data_test.filter(xvalues.index.values).to_series().dropna().values)
    yvals = list(
        data_test.filter(yvalues.index.values).to_series().dropna().values)
    return (permanova_result['p-value'], permanova_result['test statistic'],
            xvals, yvals)


def _alpha(data, xvalues, yvalues):
    x_data = data.loc[xvalues.index.values].dropna().tolist()
    y_data = data.loc[yvalues.index.values].dropna().tolist()
    stat, pval = mannwhitneyu(x_data, y_data, alternative='two-sided')
    return pval, stat, x_data, y_data


def _generate_betas(betas, mappings, permutations, output, overwrite):
    # method = partial(_beta, permutations)
    for beta, bf in betas.items():
        bfp = basename(beta)
        for mapping, mf in mappings.items():
            mfp = basename(mapping)
            for col in mf.columns.values:
                fname = join(output, '%s.%s.%s.%d.pickle' % (
                    bfp, mfp, col, permutations))
                if not exists(fname) or overwrite:
                    yield (bf, mf[col].dropna(), fname)


def _generate_alphas(alphas, mappings, output, overwrite):
    for alpha, af in alphas.items():
        afp = basename(alpha)
        for ac in af.columns.values:
            for mapping, mf in mappings.items():
                mfp = basename(mapping)
                for col in mf.columns.values:
                    fname = join(output, '%s.%s.%s.%s.pickle' % (
                        afp, ac, mfp, col))
                    if not exists(fname) or overwrite:
                        yield (
                            pd.to_numeric(af[ac], errors='coerce'),
                            mf[col].dropna(), fname)


def _process_column(data, cseries, fname, alphas, betas, permutations):
    """calculate significant comparisons and return them as a list/rows

    Parameters
    ===========
    """
    values = {k: df.dropna() for k, df in cseries.groupby(cseries)}
    # Step 1. Pairwise pvals, only keeping those ones that are significant
    qip = []
    pairwise_comparisons = []
    for x, y in combinations(values.keys(), 2):
        if betas:
            method = partial(_beta, permutations)
        else:
            method = _alpha
        pval, stat, xval, yval = method(data, values[x], values[y])
        if np.isnan(pval) or np.isnan(stat):
            continue
        qip.append(pval)
        pairwise_comparisons.append(
            (pval,
             x, len(xval), np.var(xval), np.mean(xval),
             y, len(yval), np.var(yval), np.mean(yval)))

    if qip:
        pooled_pval = len(qip) * np.min(qip)
    else:
        pooled_pval = None
    results = {'cseries': cseries.name,
               'pairwise_comparisons': pairwise_comparisons,
               'pooled_pval': pooled_pval}

    with open(fname, 'wb') as f:
        pickle.dump(results, f)

    return []
