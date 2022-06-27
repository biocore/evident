def test_bootstrap(alpha_mock):
    boot_es = alpha_mock.calculate_bootstrapped_effect_size(
        column="classification",
        iterations=1000
    )
    assert boot_es.lower < boot_es.effect_size < boot_es.upper
    assert boot_es.iterations == 1000
