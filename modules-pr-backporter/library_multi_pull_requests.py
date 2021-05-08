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

import os
import subprocess
import sys
import urllib3
import requests
from library_submodules import reset_branches
from library_submodules import label_exists
from library_submodules import get_git_root
from library_submodules import git_fetch
from library_patch_submodules import library_patch_submodules
from library_patch_submodules import library_merge_submodules
from library_patch_submodules import library_clean_submodules

__dir__ = os.path.dirname(__file__)


def handle_pull_requests(args):
    print(args)
    assert len(args) == 6
    dmp = args.pop(0)
    repo_name = args.pop(0)
    dmp = args.pop(0)
    access_token = args.pop(0)
    dmp = args.pop(0)
    external_path = args.pop(0)
    print(dmp)
    print()
    print()

    git_root = get_git_root()

    git_fetch(git_root)
    r = requests.get(
        'https://api.github.com/repos/{0}/pulls?state=open'.format(
            repo_name))
    all_open_pull_requests = \
        sorted(list(set([str(item['number']) for item in r.json()])))
    pr_hash_list = subprocess.check_output(
        "git ls-remote origin 'pull/*/head'",
        shell=True).decode('utf-8').split('\n')
    print("All Open Pull Requests: ", all_open_pull_requests)
    library_clean_submodules(all_open_pull_requests)
    for pull_request_id in all_open_pull_requests:
        print()
        print("Processing:", str(pull_request_id))
        print('-'*20, flush=True)
        commit_hash = ''
        for pr_hash in pr_hash_list:
            if 'pull/{0}/head'.format(pull_request_id) in pr_hash:
                commit_hash = pr_hash.split()[0]
                break
        print("head commit hash: ", commit_hash)
        print()
        print("Getting Patch")
        print()
        http = urllib3.PoolManager()
        patch_request = \
            http.request('GET',
                         'https://github.com/{0}/pull/{1}.patch'
                         .format(repo_name, pull_request_id))
        if patch_request.status != 200:
            print('Unable to get patch. Skipping...')
            continue

        patchfile = '{0}/{1}.patch'.format(external_path, pull_request_id)
        with open(patchfile, 'w') as f:
            f.write(patch_request.data.decode('utf-8'))
        print("Will try to apply: ", patchfile)

        if library_patch_submodules(
                patchfile, pull_request_id, repo_name, access_token,
                commit_hash):
            print()
            print("Pull Request Handled: ", str(pull_request_id))
            print('-'*20, flush=True)
            if label_exists(repo_name, pull_request_id, 'ready-to-merge'):
                print("PR {0} is now ready to be merged.."
                      .format(pull_request_id))
                library_merge_submodules(
                    pull_request_id, repo_name, access_token)
        print("Resetting Branches")
        reset_branches(git_root)
        print("Reset Branches Done!")

    print('-'*20, flush=True)
    print("Done Creating PR branches!")
    print('-'*20, flush=True)


if __name__ == "__main__":
    sys.exit(handle_pull_requests(sys.argv[1:]))
