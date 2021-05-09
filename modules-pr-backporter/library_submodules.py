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

import base64
import json
import os
import requests
import subprocess
import sys
import time

import ssh_keys


def run(cmd, **kw):
    sys.stdout.flush()
    sys.stderr.flush()
    if 'config' not in cmd:
        print(cmd, '-'*5, flush=True)
    else:
        print(cmd.split('config')[0], '...', '-'*5, flush=True)
    subprocess.check_call(cmd, shell=True, stderr=subprocess.STDOUT, **kw)
    print('-'*5, flush=True)
    sys.stdout.flush()
    sys.stderr.flush()


DATE = None  # 'Mon Oct 06 16:55:02 2020 -0700'


def git(cmd, gitdir, can_fail=False, **kw):
    env = dict(os.environ)
    if DATE:
        env['GIT_AUTHOR_DATE'] = DATE
        env['GIT_COMMITTER_DATE'] = DATE
    env['GIT_COMMITTER_NAME'] = "GitHub Actions Bot"
    env['GIT_COMMITTER_EMAIL'] = 'actions_bot@github.com'
    env['GIT_AUTHOR_NAME'] = "GitHub Actions Bot"
    env['GIT_AUTHOR_EMAIL'] = 'actions_bot@github.com'

    if 'push' in cmd:
        cmd += ' --verbose --progress'

    i = 0
    while True:
        try:
            run('git '+cmd, cwd=gitdir, env=env, **kw)
            break
        except subprocess.CalledProcessError:
            if can_fail:
                return False
            i += 1
            if i < 5:
                time.sleep(10)
                continue
            raise


def git_head(gitdir, branch='HEAD'):
    output = subprocess.check_output(['git', 'rev-parse', '--verify', branch], cwd=gitdir)
    return output.decode('utf-8').strip()


def git_config(gitdir, key, value, level='local'):
    if level != 'local':
        gitdir = None
    git("config --{} '{}' '{}'".format(level, key, value), gitdir)


#def github_auth_set(gitdir, access_token):
#    auth_token = base64.b64encode('x-access-token:{}'.format(access_token).encode('utf-8'))
#    extra_header = "AUTHORIZATION: basic {}".format(auth_token.decode())
#    git_config(gitdir, 'http.https://github.com/.extraheader', extra_header)


def github_auth_set(gitdir):
    ssh_keys.import_keys()
    #git_config(gitdir, "protocol.allow", "never", level='system')
    #git_config(gitdir, "protocol.ssh.allow", "always", level='system')


def out_v(v, versions):
    if (0, 0, 0) in versions:
        return (v[0], v[1], v[2]+1)
    return v


def previous_v(v, versions):
    assert v in versions, (v, versions)
    vers = [(0, 0, 0)]+[out_v(x, versions) for x in list(versions)]
    ov = out_v(v, versions)
    assert ov in vers, (ov, vers)
    i = vers.index(ov)
    assert i > 0, (i, ov, vers)
    return vers[i-1]


def reset_branches(git_root):
    all_local_branches = subprocess.check_output(
        'git branch', shell=True).decode('utf-8').split()
    for branch in all_local_branches:
        if branch != "*":
            git('checkout {0}'.format(branch), git_root)
            git('reset --hard origin/{0}'.format(branch), git_root)


def label_exists(repo_name, pull_request_id, label):
    r = requests.get(
        'https://api.github.com/repos/{0}/issues/{1}/labels'.format(
            repo_name, pull_request_id))
    for item in r.json():
        if item['name'] == label:
            return True
    return False


def git_issue_comment(repo_name, pull_request_id, body, access_token):
    url = 'https://api.github.com/repos/{0}/issues/{1}/comments'.format(
        repo_name, pull_request_id)
    payload = {'body': body}
    headers = {'Authorization': 'token {0}'.format(access_token)}
    requests.post(url, data=json.dumps(payload), headers=headers)


def git_issue_close(repo_name, pull_request_id, access_token):
    url = 'https://api.github.com/repos/{0}/issues/{1}'.format(
        repo_name, pull_request_id)
    payload = {'state': 'closed'}
    headers = {'Authorization': 'token {0}'.format(access_token)}
    requests.post(url, data=json.dumps(payload), headers=headers)


def get_git_root():
    return subprocess.check_output(
        'git rev-parse --show-toplevel', shell=True).decode('utf-8').strip()


def git_fetch(git_root):
    print()
    print()
    git('fetch origin', git_root)
    git('fetch origin --tags', git_root)
    git('status', git_root)
    print('-'*20, flush=True)


def get_lib_versions(git_root):
    tags = subprocess.check_output('git tag -l', shell=True, cwd=git_root)

    tags = tags.decode('utf-8')

    versions = [tuple(int(i) for i in v[1:].split('.')) for v in tags.split()]
    if (0, 0, 0) in versions:
        versions.remove((0, 0, 0))
    return versions


def git_clean(git_root):
    git('clean -f', git_root)
    git('clean -x -f', git_root)
