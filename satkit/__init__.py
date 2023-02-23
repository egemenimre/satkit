# satkit: Satellite Mission Analysis and Design for Python
#
# Copyright (C) 2023 Egemen Imre
#
# Licensed under GNU GPL v3.0. See LICENSE.rst for more info.
"""
satkit entry module.
"""
__version__ = "0.0.1"

from pathlib import Path

import orekit
from pint import UnitRegistry

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


def process_paths(alt_intermediate_dir, path):
    """
    Processes the path depending on the run environment.
    Checks the Nominal Path, if it does not exist, tries the alternate path.

    Nominal path: `current working dir` + `path`

    Alternate path: `current working dir` + `alternate intermediate dir` + `path`

    Parameters
    ----------
    alt_intermediate_dir : Path
        Alternate intermediate directory
    path: Path
        Filepath
    """
    working_dir = Path.cwd()

    file_path = working_dir.joinpath(path)
    if not working_dir.joinpath(file_path).exists():
        file_path = working_dir.joinpath(alt_intermediate_dir).joinpath(path)

    return file_path.resolve()
