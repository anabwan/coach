#
# INTEL CONFIDENTIAL
# Copyright 2019 Intel Corporation.
#
# This software and the related documents are Intel copyrighted materials,
# and your use of them is governed by the express license under which they
# were provided to you (License). Unless the License provides otherwise, you
# may not use, modify, copy, publish, distribute, disclose or transmit this
# software or the related documents without Intel's prior written permission.
#
# This software and the related documents are provided as is, with no express
# or implied warranties, other than those that are expressly stated in the
# License.
"""PyTest configuration."""

import configparser as cfgparser
import os
import platform
import shutil
import pytest
import rl_coach.tests.utils.presets_utils as p_utils
from os import path


def pytest_collection_modifyitems(config, items):
    """pytest built in method to pre-process cli options"""
    global test_config
    test_config = cfgparser.ConfigParser()
    str_rootdir = str(config.rootdir)
    str_inifile = str(config.inifile)
    # Get the relative path of the inifile
    # By default is an absolute path but relative path when -c option used
    config_path = os.path.relpath(str_inifile, str_rootdir)
    config_path = os.path.join(str_rootdir, config_path)
    assert (os.path.exists(config_path))
    test_config.read(config_path)


def pytest_runtest_setup(item):
    """Called before test is run."""
    if (item.get_marker("unstable") and
            "unstable" not in item.config.getoption("-m")):
        pytest.skip("skipping unstable test")

    if item.get_marker("linux_only"):
        if platform.system() == 'Windows':
            pytest.skip("Skipping test that not Linux OS.")

    if item.get_marker("golden_test"):
        """ do some custom configuration for golden tests. """
        # TODO: add custom functionality
        pass


@pytest.fixture(scope="module", params=list(p_utils.collect_presets()))
def preset_name(request):
    return request.param


@pytest.fixture(scope="function")
def csv_results():
    # TODO: stil not in use - make it work
    test_name = '__test_reward_{}'.format(preset_name)
    test_path = os.path.join('./experiments', test_name)
    if path.exists(test_path):
        shutil.rmtree(test_path)

    yield


