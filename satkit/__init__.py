# satkit: Satellite Mission Analysis and Design for Python
#
# Copyright (C) 2023 Egemen Imre
#
# Licensed under GNU GPL v3.0. See LICENSE.rst for more info.
"""
satkit
=========
Satellite Mission Analysis and Design in Python.
"""
__version__ = "0.0.1"

from pint import UnitRegistry
import orekit
from pathlib import Path


# init unit registry
u = UnitRegistry()

# Init Java VM
orekit.initVM()

#  File path part 1 for Orekit setup files
extra_path = Path(
    "..",
    "..",
    "..",
)


def process_paths(path):
    """
    Processes the path depending on the run environment.
    """
    working_dir = Path.cwd()

    file_path = working_dir.joinpath(path)
    if not working_dir.joinpath(file_path).exists():
        file_path = working_dir.joinpath(extra_path).joinpath(path)

    return file_path
