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
"""Test for test code itself."""

import os


path = os.path.dirname(__file__)


def test_pep8_conformance():
    """Check for python sources for PEP8 conformance."""
    import pep8
    style = pep8.StyleGuide()
    result = style.check_files([path])
    assert result.total_errors == 0


def test_pyflakes_conformance():
    """Check python sources pyflakes."""
    import pyflakes.api
    assert pyflakes.api.checkRecursive([path], reporter=None) == 0
