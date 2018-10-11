import pickle
import numpy as np

from os import remove
from os.path import exists, isfile, join, dirname, abspath
from shutil import rmtree
from inspect import currentframe, getfile
from tempfile import mkdtemp
from unittest import TestCase, main
from functools import partial

from evident import effect_size as _effect_size


class TestEffectSize(TestCase):

    def setUp(self):
        self._clean_up_files = []
        self.filepath = join(dirname(abspath(getfile(currentframe()))),
                             'support_files')

        mapping = join(self.filepath, 'mappings.txt')
        mapping_age = join(self.filepath, 'mapping_age.txt')
        mapping_gender = join(self.filepath, 'mapping_gender.txt')
        mapping_country = join(self.filepath, 'mapping_country.txt')

        self.mappings = [mapping, mapping_age, mapping_gender,
                         mapping_country]

    def tearDown(self):
        for fp in self._clean_up_files:
            if exists(fp):
                if isfile(fp):
                    remove(fp)
                else:
                    rmtree(fp)

    def test_effect_size_alpha(self):
        alpha = join(self.filepath, 'alphas.txt')
        alpha_pd = join(self.filepath, 'alpha_pd.txt')
        alpha_sn = join(self.filepath, 'alpha_sn.txt')
        alpha_otu = join(self.filepath, 'alpha_otu.txt')

        alphas = [alpha, alpha_pd, alpha_sn, alpha_otu]
        na_values = ['nan', 'Not applicable', 'Missing: Not provided',
                     'None']

        output = mkdtemp()
        self._clean_up_files.append(output)

        _effect_size.effect_size(mappings=self.mappings, alphas=alphas,
                                 output=output, betas=None, jobs=None,
                                 permutations=None,
                                 na_values=na_values,
                                 overwrite=True)

        # check effect size calculation for gender (two-group categorical)
        pfp = partial(join, output)
        gender_results = [
            ('alpha_pd.txt.Faith_PD.mapping_gender.txt.Gender.pickle',
             'alpha_pd.txt.Faith_PD.mappings.txt.Gender.pickle',
             'alpha_sn.txt.Shannon.mapping_gender.txt.Gender.pickle',
             'alpha_sn.txt.Shannon.mappings.txt.Gender.pickle',
             'alpha_otu.txt.Observed_OTUs.mapping_gender.txt.Gender.pickle',
             'alpha_otu.txt.Observed_OTUs.mappings.txt.Gender.pickle')]

        for gen_files in gender_results:
            (gender_pd, gender_pd_g, gender_sn,
             gender_sn_g, gender_otu, gender_otu_g) = gen_files

            with open(pfp(gender_pd), "rb") as file_gender_pd, \
                open(pfp(gender_pd_g), "rb") as file_gender_pd_g, \
                open(pfp(gender_sn), "rb") as file_gender_sn, \
                open(pfp(gender_sn_g), "rb") as file_gender_sn_g, \
                open(pfp(gender_otu), "rb") as file_gender_otu, \
                open(pfp(gender_otu_g), "rb") as file_gender_otu_g:

                results_gender_pd = pickle.load(file_gender_pd)
                results_gender_pd_g = pickle.load(file_gender_pd_g)
                results_gender_sn = pickle.load(file_gender_sn)
                results_gender_sn_g = pickle.load(file_gender_sn_g)
                results_gender_otu = pickle.load(file_gender_otu)
                results_gender_otu_g = pickle.load(file_gender_otu_g)

                np.testing.assert_equal(
                    len(results_gender_pd['pairwise_comparisons']),
                    len(results_gender_pd_g['pairwise_comparisons']))
                np.testing.assert_equal(
                    results_gender_pd['pooled_pval'],
                    results_gender_pd_g['pooled_pval'])

                np.testing.assert_equal(
                    len(results_gender_sn['pairwise_comparisons']),
                    len(results_gender_sn_g['pairwise_comparisons']))
                np.testing.assert_equal(
                    results_gender_sn['pooled_pval'],
                    results_gender_sn_g['pooled_pval'])

                np.testing.assert_equal(
                    len(results_gender_otu['pairwise_comparisons']),
                    len(results_gender_otu_g['pairwise_comparisons']))
                np.testing.assert_equal(
                    results_gender_otu['pooled_pval'],
                    results_gender_otu_g['pooled_pval'])

                np.testing.assert_array_less(
                    results_gender_sn['pooled_pval'],
                    results_gender_otu['pooled_pval'])
                np.testing.assert_array_less(
                    results_gender_otu['pooled_pval'],
                    results_gender_pd['pooled_pval'])

        # check effect size calculation for country (four-group categorical)
        country_results = [
            ('alpha_pd.txt.Faith_PD.mapping_country.txt.Country.pickle',
             'alpha_pd.txt.Faith_PD.mappings.txt.Country.pickle',
             'alpha_sn.txt.Shannon.mapping_country.txt.Country.pickle',
             'alpha_sn.txt.Shannon.mappings.txt.Country.pickle',
             'alpha_otu.txt.Observed_OTUs.mapping_country.txt.Country.pickle',
             'alpha_otu.txt.Observed_OTUs.mappings.txt.Country.pickle')]

        for country_files in country_results:
            (country_pd, country_pd_g, country_sn,
             country_sn_g, country_otu, country_otu_g) = country_files

            with open(pfp(country_pd), "rb") as file_country_pd, \
                open(pfp(country_pd_g), "rb") as file_country_pd_g, \
                open(pfp(country_sn), "rb") as file_country_sn, \
                open(pfp(country_sn_g), "rb") as file_country_sn_g, \
                open(pfp(country_otu), "rb") as file_country_otu, \
                open(pfp(country_otu_g), "rb") as file_country_otu_g:

                results_country_pd = pickle.load(file_country_pd)
                results_country_pd_g = pickle.load(file_country_pd_g)
                results_country_sn = pickle.load(file_country_sn)
                results_country_sn_g = pickle.load(file_country_sn_g)
                results_country_otu = pickle.load(file_country_otu)
                results_country_otu_g = pickle.load(file_country_otu_g)

                np.testing.assert_equal(
                    len(results_country_pd['pairwise_comparisons']),
                    len(results_country_pd_g['pairwise_comparisons']))
                np.testing.assert_equal(
                    results_country_pd['pooled_pval'],
                    results_country_pd_g['pooled_pval'])

                np.testing.assert_equal(
                    len(results_country_sn['pairwise_comparisons']),
                    len(results_country_sn_g['pairwise_comparisons']))
                np.testing.assert_equal(
                    results_country_sn['pooled_pval'],
                    results_country_sn_g['pooled_pval'])

                np.testing.assert_equal(
                    len(results_country_otu['pairwise_comparisons']),
                    len(results_country_otu_g['pairwise_comparisons']))
                np.testing.assert_equal(
                    results_country_otu['pooled_pval'],
                    results_country_otu_g['pooled_pval'])

                np.testing.assert_array_less(
                    results_country_sn['pooled_pval'],
                    results_country_otu['pooled_pval'])
                np.testing.assert_array_less(
                    results_country_otu['pooled_pval'],
                    results_country_pd['pooled_pval'])

        # check effect size calculation for age (continous)
        age_results = [
            ('alpha_pd.txt.Faith_PD.mapping_age.txt.Age.pickle',
             'alpha_pd.txt.Faith_PD.mappings.txt.Age.pickle',
             'alpha_sn.txt.Shannon.mapping_age.txt.Age.pickle',
             'alpha_sn.txt.Shannon.mappings.txt.Age.pickle',
             'alpha_otu.txt.Observed_OTUs.mapping_age.txt.Age.pickle',
             'alpha_otu.txt.Observed_OTUs.mappings.txt.Age.pickle')]

        for age_files in age_results:
            (age_pd, age_pd_g, age_sn,
             age_sn_g, age_otu, age_otu_g) = age_files

            with open(pfp(age_pd), "rb") as file_age_pd, \
                open(pfp(age_pd_g), "rb") as file_age_pd_g, \
                open(pfp(age_sn), "rb") as file_age_sn, \
                open(pfp(age_sn_g), "rb") as file_age_sn_g, \
                open(pfp(age_otu), "rb") as file_age_otu, \
                open(pfp(age_otu_g), "rb") as file_age_otu_g:

                results_age_pd = pickle.load(file_age_pd)
                results_age_pd_g = pickle.load(file_age_pd_g)
                results_age_sn = pickle.load(file_age_sn)
                results_age_sn_g = pickle.load(file_age_sn_g)
                results_age_otu = pickle.load(file_age_otu)
                results_age_otu_g = pickle.load(file_age_otu_g)

                np.testing.assert_equal(
                    len(results_age_pd['pairwise_comparisons']),
                    len(results_age_pd_g['pairwise_comparisons']))
                np.testing.assert_equal(
                    results_age_pd['pooled_pval'],
                    results_age_pd_g['pooled_pval'])

                np.testing.assert_equal(
                    len(results_age_sn['pairwise_comparisons']),
                    len(results_age_sn_g['pairwise_comparisons']))
                np.testing.assert_equal(
                    results_age_sn['pooled_pval'],
                    results_age_sn_g['pooled_pval'])

                np.testing.assert_equal(
                    len(results_age_otu['pairwise_comparisons']),
                    len(results_age_otu_g['pairwise_comparisons']))
                np.testing.assert_equal(
                    results_age_otu['pooled_pval'],
                    results_age_otu_g['pooled_pval'])

                np.testing.assert_array_less(
                    results_age_sn['pooled_pval'],
                    results_age_otu['pooled_pval'])
                np.testing.assert_array_less(
                    results_age_otu['pooled_pval'],
                    results_age_pd['pooled_pval'])


if __name__ == "__main__":
    main()
