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
"""
Definitions file:

It's main functionality are:
1) housing project constants and enums.
2) housing configuration parameters.
3) housing resource paths.
"""


class Definitions:
    GROUP_NAME = "rl_coach"
    PROCESS_NAME = "coach"

    class Flags:
        PRESET = "-p, --preset, --presets"
        # TODO: add all flags

    class Prests:
        # TODO Add dynamically list
        pass