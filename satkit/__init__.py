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
from orekit.pyhelpers import setup_orekit_curdir
from pint import UnitRegistry

# Init units
u = UnitRegistry()

# Init Java Virtual Machine
vm = orekit.initVM()


def init_satkit(filepath: Path, *search_dirs: Path):
    """
    Inits Orekit using the orekit data file provided.

    Searches the file first in the given path, then in the
    current working directory. If it does not exist, tries the
    alternate directories. Returns `None` if the file is not found
    in any of the directories.

    - Nominal path: `current working dir` + `filepath`
    - Alternate paths: `current working dir` + `alternate search dir` + `filepath`

    Parameters
    ----------
    filepath
        File path
    search_dirs
        Alternate search directories

    Returns
    -------
    Path
        Path of the file, `None` if not found
    """
    #  Init Orekit data (add alternative path to look for the reference data)
    orekit_data_file_path = process_paths(filepath, *search_dirs)
    setup_orekit_curdir(str(orekit_data_file_path))

    return orekit_data_file_path


def process_paths(filepath: Path, *search_dirs: Path):
    """
    Inits a filepath with different alternative locations.

    Searches the file first in the given path, then in the
    current working directory. If it does not exist, tries the
    alternate directories. Returns `None` if the file is not found
    in any of the directories.

    - Nominal path: `current working dir` + `filepath`
    - Alternate paths: `current working dir` + `alternate search dir` + `filepath`

    Parameters
    ----------
    filepath
        File path
    search_dirs
        Alternate search directories

    Returns
    -------
    Path
        Path of the file, `None` if not found
    """
    working_dir = Path.cwd()

    if Path(filepath).exists():
        # check whether the file is at the current working dir
        return filepath.resolve()
    else:
        # build the file path at the current working dir
        file_path = working_dir.joinpath(filepath)
        if file_path.exists():
            return file_path.resolve()
        else:
            # search the remaining directories
            for search_dir in search_dirs:
                file_path = working_dir.joinpath(search_dir).joinpath(filepath)
                if file_path.exists():
                    return file_path.resolve()

    # File is nowhere to be found, return None
    return None
