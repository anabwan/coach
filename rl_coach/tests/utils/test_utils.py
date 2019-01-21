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
"""Common functionality shared across tests."""

import glob
import sys
import time
from os import path


def print_progress(averaged_rewards, last_num_episodes, start_time, time_limit,
                   p_valid_params):
    """
    Print progress bar for preset run test
    :param averaged_rewards:
    :param last_num_episodes:
    :param p_valid_params:
    :param start_time:
    :param time_limit:
    :return:
    """
    max_episodes_to_archive = p_valid_params.max_episodes_to_achieve_reward
    min_reward = p_valid_params.min_reward_threshold
    avg_reward = round(averaged_rewards[-1], 1)
    percentage = int((100 * last_num_episodes) / max_episodes_to_archive)
    cur_time = round(time.time() - start_time, 2)

    sys.stdout.write("\rReward: ({}/{})".format(avg_reward, min_reward))
    sys.stdout.write(' Time (sec): ({}/{})'.format(cur_time, time_limit))
    sys.stdout.write(' Episode: ({}/{})'.format(last_num_episodes,
                                                max_episodes_to_archive))
    sys.stdout.write(' {}%|{}{}|  '
                     .format(percentage, '#' * int(percentage / 10),
                             ' ' * (10 - int(percentage / 10))))

    sys.stdout.flush()


def read_csv_paths(test_path, filename_pattern, read_csv_tries=100):
    """

    :param test_path:
    :param filename_pattern:
    :param read_csv_tries:
    :return:
    """
    csv_paths = []
    tries_counter = 0
    while not csv_paths:
        csv_paths = glob.glob(path.join(test_path, '*', filename_pattern))
        if tries_counter > read_csv_tries:
            break
        tries_counter += 1
        time.sleep(1)
    return csv_paths
