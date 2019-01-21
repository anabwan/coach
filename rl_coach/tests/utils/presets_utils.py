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
"""Manage all preset"""

import os
from importlib import import_module


def import_preset(preset_name):
    """

    :param preset_name:
    :return:
    """
    return import_module('rl_coach.presets.{}'.format(preset_name))


def validation_params(preset_name):
    """

    :param preset_name:
    :return:
    """
    return import_preset(preset_name).graph_manager.preset_validation_params


def all_presets():
    """

    :return:
    """
    return [
        f[:-3] for f in os.listdir(os.path.join('rl_coach', 'presets'))
        if f[-3:] == '.py' and not f == '__init__.py'
    ]


def importable(preset_name):
    """

    :param preset_name:
    :return:
    """
    try:
        import_preset(preset_name)
        return True
    except BaseException:
        return False


def has_test_parameters(preset_name):
    """

    :param preset_name:
    :return:
    """
    return bool(validation_params(preset_name).test)


def collect_presets():
    """

    :return:
    """
    for preset_name in all_presets():
        # if it isn't importable, still include it so we can fail the test
        if not importable(preset_name):
            yield preset_name
        # otherwise, make sure it has test parameters before including it
        elif has_test_parameters(preset_name):
            yield preset_name
