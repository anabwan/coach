#
# INTEL CONFIDENTIAL
# Copyright 2017-2019 Intel Corporation.
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
"""Golden tests"""

import argparse
import os
import shutil
import subprocess
import numpy as np
import pandas as pd
import time
import pytest
import rl_coach.tests.utils.presets_utils as p_utils
import rl_coach.tests.utils.test_utils as test_utils
from rl_coach.logger import screen
from os import path


@pytest.mark.golden_test
def test_preset_reward(preset_name, time_limit=60*60, progress_bar=False,
                       verbose=False):
    """tests presets reward"""

    p_valid_params = p_utils.validation_params(preset_name)
    win_size = 10

    test_name = '__test_reward_{}'.format(preset_name)
    test_path = os.path.join('./experiments', test_name)
    if path.exists(test_path):
        shutil.rmtree(test_path)

    # run the experiment in a separate thread
    screen.log_title("Running test {}".format(preset_name))
    log_file_name = 'test_log_{}.txt'.format(preset_name)
    cmd = [
        'python3',
        'rl_coach/coach.py',
        '-p', '{preset_name}'.format(preset_name=preset_name),
        '-e', '{test_name}'.format(test_name=test_name),
        '-n', '{num_workers}'.format(num_workers=p_valid_params.num_workers),
        '--seed', '0',
        '-c'
    ]
    if p_valid_params.reward_test_level:
        cmd += ['-lvl', '{level}'.format(level=p_valid_params.reward_test_level)]

    stdout = open(log_file_name, 'w')

    p = subprocess.Popen(cmd, stdout=stdout, stderr=stdout)

    start_time = time.time()

    reward_str = 'Evaluation Reward'
    if p_valid_params.num_workers > 1:
        filename_pattern = 'worker_0*.csv'
    else:
        filename_pattern = '*.csv'

    test_passed = False

    # get the csv with the results
    csv_paths = test_utils.read_csv_paths(test_path, filename_pattern)

    if csv_paths:
        csv_path = csv_paths[0]

        # verify results
        csv = None
        time.sleep(1)
        averaged_rewards = [0]

        last_num_episodes = 0

        if not progress_bar:
            test_utils.print_progress(averaged_rewards, last_num_episodes,
                                      p_valid_params, start_time, time_limit)

        while csv is None or \
                (csv['Episode #'].values[-1] < p_valid_params.max_episodes_to_achieve_reward and time.time() - start_time < time_limit):
            try:
                csv = pd.read_csv(csv_path)
            except:
                # sometimes the csv is being written at the same time we are
                # trying to read it. no problem -> try again
                continue

            if reward_str not in csv.keys():
                continue

            rewards = csv[reward_str].values
            rewards = rewards[~np.isnan(rewards)]

            if len(rewards) >= 1:
                averaged_rewards = np.convolve(rewards, np.ones(min(len(rewards), win_size)) / win_size, mode='valid')
            else:
                time.sleep(1)
                continue

            if not progress_bar:
                test_utils.print_progress(averaged_rewards, last_num_episodes,
                                          p_valid_params, start_time,
                                          time_limit)

            if csv['Episode #'].shape[0] - last_num_episodes <= 0:
                continue

            last_num_episodes = csv['Episode #'].values[-1]

            # check if reward is enough
            if np.any(averaged_rewards >= p_valid_params.min_reward_threshold):
                test_passed = True
                break
            time.sleep(1)

    # kill test and print result
    # os.killpg(os.getpgid(p.pid), signal.SIGKILL)
    p.kill()
    screen.log('')
    if test_passed:
        screen.success("Passed successfully")
    else:
        if time.time() - start_time > time_limit:
            screen.error("Failed due to exceeding time limit", crash=False)
            if verbose:
                screen.error("command exitcode: {}".format(p.returncode), crash=False)
                screen.error(open(log_file_name).read(), crash=False)
        elif csv_paths:
            screen.error("Failed due to insufficient reward", crash=False)
            if verbose:
                screen.error("command exitcode: {}".format(p.returncode), crash=False)
                screen.error(open(log_file_name).read(), crash=False)
            screen.error("preset_validation_params.max_episodes_to_achieve_reward: {}".format(
                p_valid_params.max_episodes_to_achieve_reward), crash=False)
            screen.error("preset_validation_params.min_reward_threshold: {}".format(
                p_valid_params.min_reward_threshold), crash=False)
            screen.error("averaged_rewards: {}".format(averaged_rewards), crash=False)
            screen.error("episode number: {}".format(csv['Episode #'].values[-1]), crash=False)
        else:
            screen.error("csv file never found", crash=False)
            if verbose:
                screen.error("command exitcode: {}".format(p.returncode), crash=False)
                screen.error(open(log_file_name).read(), crash=False)

    shutil.rmtree(test_path)
    os.remove(log_file_name)
    return test_passed


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--preset', '--presets',
                        help="(string) Name of preset(s) to run (comma separated, and as configured in presets.py)",
                        default=None,
                        type=str)
    parser.add_argument('-ip', '--ignore_presets',
                        help="(string) Name of preset(s) to ignore (comma separated, and as configured in presets.py)",
                        default=None,
                        type=str)
    parser.add_argument('-v', '--verbose',
                        help="(flag) display verbose logs in the event of an error",
                        action='store_true')
    parser.add_argument('--stop_after_first_failure',
                        help="(flag) stop executing tests after the first error",
                        action='store_true')
    parser.add_argument('-tl', '--time_limit',
                        help="time limit for each test in minutes",
                        default=60,  # setting time limit to be so high due to DDPG being very slow - its tests are long
                        type=int)
    parser.add_argument('-np', '--no_progress_bar',
                        help="(flag) Don't print the progress bar (makes jenkins logs more readable)",
                        action='store_true')

    args = parser.parse_args()
    if args.preset is not None:
        presets_lists = args.preset.split(',')
    else:
        presets_lists = p_utils.all_presets()

    fail_count = 0
    test_count = 0

    args.time_limit = 60 * args.time_limit

    if args.ignore_presets is not None:
        presets_to_ignore = args.ignore_presets.split(',')
    else:
        presets_to_ignore = []
    for idx, preset_name in enumerate(sorted(presets_lists)):
        if args.stop_after_first_failure and fail_count > 0:
            break
        if preset_name not in presets_to_ignore:
            print("Attempting to run Preset: %s" % preset_name)
            if not p_utils.importable(preset_name):
                screen.error("Failed to load preset <{}>".format(preset_name),
                             crash=False)
                fail_count += 1
                test_count += 1
                continue

            if not p_utils.has_test_parameters(preset_name):
                continue

            test_count += 1
            test_passed = test_preset_reward(preset_name, args.progress_bar,
                                             args.time_limit, args.verbose)
            if not test_passed:
                fail_count += 1

    screen.separator()
    if fail_count == 0:
        screen.success(" Summary: " + str(test_count) + "/" + str(test_count)
                       + " tests passed successfully")
    else:
        screen.error(" Summary: " + str(test_count - fail_count) + "/"
                     + str(test_count) + " tests passed successfully")


if __name__ == '__main__':
    main()
