#!/usr/bin/env python

# -----------------------------------------------------------------------------
# Copyright (c) 2018, The Evident Development Team.
#
# Distributed under the terms of the BSD 3-clause License.
#
# The full license is in the file LICENSE, distributed with this software.
# -----------------------------------------------------------------------------

import pandas as pd
from os import listdir
from os.path import join
import pickle
from statsmodels.sandbox.stats.multicomp import multipletests
import seaborn as sns
import numpy as np
import matplotlib as mpl


def summarize(input_fp, output_fp, check_pval):
    pickles = [f for f in listdir(input_fp) if f.endswith('.pickle')]

    rows = []
    for idx, p in enumerate(pickles):
        with open(join(input_fp, p), 'rb') as f:
            results = pickle.load(f)
            rows.append((idx, (results['div_file'], results['mapping_file'],
                               results['mapping_col'], results['pooled_pval'],
                               results['pairwise_comparisons'])))
    results_df = pd.DataFrame.from_items(rows, orient='index', columns=[
            'fname', 'mapping_file', 'column_name',
            'pooled_pval', 'pairwise_comparisons'])

    alpha = 0.05
    for name, df in results_df.groupby(['fname', 'mapping_file']):
        rejects, pvals, _, _ = multipletests(df.pooled_pval.values,
                                             alpha=alpha, method='fdr_bh',
                                             returnsorted=False)
        significant_variables = df[rejects]
        R = significant_variables.shape[0]
        m = df.shape[0]
        qi = len(df.pairwise_comparisons)
        pval_corrected = (R/(m*qi))*alpha

        all_effect_sizes = []
        for index, row in df.iterrows():
            max_effect_size = [-1, None, -1]
            for pairwise_compare in row.pairwise_comparisons:
                pval, x, len_x, var_x, mean_x, y, len_y, var_y, \
                    mean_y = pairwise_compare
                if check_pval and pval > pval_corrected:
                    continue
                pooled_variance_numerator = (
                    (len_x - 1) * var_x) + ((len_y - 1) * var_y)
                pooled_variance_denominator = (len_x - 1) + (len_y - 1)
                pooled_variance = (
                    pooled_variance_numerator / pooled_variance_denominator)
                pooled_std = np.sqrt(pooled_variance)

                effect_size = np.abs((mean_x - mean_y) / pooled_std)

                if effect_size > max_effect_size[0]:
                    max_effect_size = [effect_size, "%s vs. %s" % (x, y), pval]
            if max_effect_size[0] > -1:
                all_effect_sizes.append((1, (
                    row.column_name, max_effect_size[0],
                    np.square(max_effect_size[0]), max_effect_size[1],
                    pval_corrected, max_effect_size[2])))

        if bool(all_effect_sizes):
            effect_sizes = pd.DataFrame.from_items(
                all_effect_sizes, orient='index', columns=[
                    'column_name', 'effect_size', 'effect_size_square',
                    'max_effect_size_categories', 'pval_corrected', 'pval'])
            if not effect_sizes.empty:
                effect_sizes.sort_values('effect_size',
                                         ascending=False).to_csv(
                    join(output_fp, '%s.tsv') % '.'.join(name), sep='\t')
                with sns.color_palette("PuBuGn_d"):
                    sns.set_style("ticks")
                    img = sns.barplot(y="column_name", x="effect_size",
                                      data=effect_sizes.sort_values(
                                        'effect_size', ascending=False).head(
                                        n=20))
                    sns.despine()
                fig = img.get_figure()
                fig.savefig(join(output_fp, "%s-effect_size.pdf" %
                                 '.'.join(name)), bbox_inches='tight')
                fig.clf()

                with sns.color_palette("PuBuGn_d"):
                    sns.set_style("ticks")
                    img = sns.barplot(y="column_name", x="effect_size_square",
                                      data=effect_sizes.sort_values(
                                        'effect_size_square',
                                        ascending=False).head(n=20))
                    sns.despine()
                fig = img.get_figure()
                fig.savefig(join(output_fp,
                            "%s-effect_size_square.pdf" % '.'.join(name)),
                            bbox_inches='tight')
                fig.clf()


if __name__ == '__main__':
    mpl.rcParams['pdf.fonttype'] = 42
    summarize()
