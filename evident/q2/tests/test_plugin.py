import os

import pytest
from qiime2 import Artifact, Metadata
from qiime2.plugins import evident


@pytest.fixture
def alpha_artifact():
    fname = os.path.join(os.path.dirname(__file__), "data/test_alpha_div.qza")
    return Artifact.load(fname)


@pytest.fixture
def metadata():
    fname = os.path.join(os.path.dirname(__file__), "data/test_metadata.qza")
    return Metadata.load(fname)


def test_alpha_pa_single(alpha_artifact, metadata):
    func = evident.methods.alpha_power_analysis_single
    func(
        alpha_artifact,
        metadata.get_column("classification"),
        alpha=0.05,
        power=0.8
    )
