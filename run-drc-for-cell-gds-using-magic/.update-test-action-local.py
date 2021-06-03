#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
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

import pathlib

__dir__ = pathlib.Path(__file__).parent.resolve()

src_action_yml = __dir__ / 'action.yml'
dst_action_yml = (__dir__ / 'tests' / 'action-local' / 'action.yml').resolve()

print('Base action.yml file at:', src_action_yml)
print('Test action.yml file at:', dst_action_yml)

with open(src_action_yml) as f:
    action_data = f.read()

name = 'run-drc-for-cell-gds-using-magic'
action_data = action_data.replace(
    f'image: docker://gcr.io/skywater-pdk/actions/{name}:main',
    'image: ../../Dockerfile',
)

action_data = action_data.replace(
    '\nname:',
    """
# WARNING! Don't modify this file, modify the base `action.yml` file and then
# run `make tests/action-local/action.yml`.

name:""")

with open(dst_action_yml, 'w') as f:
    f.write(action_data)
