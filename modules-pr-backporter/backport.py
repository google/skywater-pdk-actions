#!/usr/bin/env python3
# Copyright 2020 SkyWater PDK Authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# SPDX-License-Identifier: Apache-2.0

import json
import logging
import os
import pathlib
import subprocess
import urllib3

from backport_pr import handle_pull_request
from backport_checks import handle_workflow_run

from backport_common import *


def handle_event(args):
    logging.basicConfig(level=logging.DEBUG)
    http = urllib3.PoolManager()

    event_json_path = os.environ.get('GITHUB_EVENT_PATH', None)
    if not event_json_path:
        print("Did not find GITHUB_EVENT_NAME environment value.")
        return -1
    event_json_path = pathlib.Path(event_json_path)
    if not event_json_path.exists():
        print(f"Path {event_json_path} was not found.")
        return -2

    group_start('git config', debug)
    git_config_out = subprocess.check_output(['git', 'config', '--show-origin', '--list'])
    debug(git_config_out.decode('utf-8'))
    group_end()

    event_json_data = open(event_json_path).read()
    group_start('Raw event_json_data', debug)
    debug(event_json_data)
    group_end()

    event_json = json.load(open(event_json_path))
    group_start("Event data")
    pprint.pprint(event_json)
    group_end()

    if 'pull_request' in event_json:
        return handle_pull_request(http, event_json)

    elif 'workflow_run' in event_json:
        return handle_workflow_run(http, event_json)


if __name__ == "__main__":
    sys.exit(handle_event(sys.argv[1:]))
