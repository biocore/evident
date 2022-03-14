import pytest

from evident.interactive import create_bokeh_app


@pytest.mark.parametrize("mock", ["alpha_mock", "beta_mock"])
def test_interactive(mock, request, tmpdir):
    dh = request.getfixturevalue(mock)
    create_bokeh_app(dh, tmpdir, exist_ok=True)
