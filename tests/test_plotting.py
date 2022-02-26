import pytest

from evident.plotting import plot_power_curve


@pytest.mark.parametrize("mock", ["alpha_mock", "beta_mock"])
def test_plot_power_curve(mock, request):
    dh = request.getfixturevalue(mock)

    alpha = [0.01, 0.05, 0.1]
    res = dh.power_analysis(column="classification", alpha=alpha, power=0.8)
    plot_power_curve(res)
