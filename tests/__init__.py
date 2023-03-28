# satkit: Satellite Mission Analysis and Design for Python
#
# Copyright (C) 2023 Egemen Imre
#
# Licensed under GNU GPL v3.0. See LICENSE.rst for more info.
"""
Tests for satkit.

"""
from pathlib import Path

from satkit import init_satkit

extra_path = Path(
    "..",
    "..",
)

orekit_data_file_path = Path("data", "orekit-data", "orekit-data-reference.zip")


def common_test_setup_module():
    """setup any state specific to the execution of the module."""

    init_satkit(orekit_data_file_path, extra_path)
