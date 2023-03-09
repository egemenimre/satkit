# satkit: Satellite Mission Analysis and Design for Python
#
# Copyright (C) 2023 Egemen Imre
#
# Licensed under GNU GPL v3.0. See LICENSE.rst for more info.
"""
Tests for satkit

"""
from pathlib import Path

from orekit.pyhelpers import setup_orekit_curdir

from satkit import process_paths

extra_path = Path(
    "..",
    "..",
)

orekit_data_file_path = Path("data", "orekit-data", "orekit-data-reference.zip")


def common_test_setup_module():
    """setup any state specific to the execution of the module."""

    #  Init Orekit data
    data_file = process_paths(extra_path, orekit_data_file_path).resolve()

    setup_orekit_curdir(str(data_file))
