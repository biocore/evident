from evident.effect_size import (effect_size_by_category,
                                 pairwise_effect_size_by_category)


def test_bootstrap_alpha(alpha_mock):
    boot_es = alpha_mock.calculate_effect_size(
        column="classification",
        bootstrap_iterations=100
    )
    assert boot_es.lower_es < boot_es.effect_size < boot_es.upper_es
    assert boot_es.iterations == 100


def test_bootstrap_beta(beta_mock):
    boot_es = beta_mock.calculate_effect_size(
        column="classification",
        bootstrap_iterations=100
    )
    assert boot_es.lower_es < boot_es.effect_size < boot_es.upper_es
    assert boot_es.iterations == 100


def test_es_by_category_bootstrap(alpha_mock):
    boot_res = effect_size_by_category(
        alpha_mock,
        ["classification", "cd_resection"],
        bootstrap_iterations=100
    )
    for es in boot_res:
        assert es.lower_es < es.effect_size < es.upper_es


def test_pw_es_by_category_bootstrap(alpha_mock):
    boot_res = pairwise_effect_size_by_category(
        alpha_mock,
        ["cd_behavior", "ibd_subtype"],
        bootstrap_iterations=100
    )
    for es in boot_res:
        assert es.lower_es < es.effect_size < es.upper_es
