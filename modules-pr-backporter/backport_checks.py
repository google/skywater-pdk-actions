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


import os
import pprint
import requests

from backport_common import *


def github_headers(_headers={}):
    if not _headers:
        # Figure out the GitHub access token.
        access_token = os.environ.get('GH_APP_TOKEN', None)
        if not access_token:
            raise SystemError('Did not find an access token of `GH_APP_TOKEN`')

        _headers['Authorization'] = 'token ' + access_token
        _headers['Accept'] = 'application/vnd.github.v3+json'
    return _headers


def get_github_json(url, *args, **kw):
    full_url = url.format(*args, **kw)
    return send_github_json(full_url, 'GET')


def send_github_json(url, mode, json_data=None):
    assert mode in ('GET', 'POST', 'PATCH'), f"Unknown mode {mode}"

    kw = {
        'url': url,
        'headers': github_headers(),
    }
    if mode == 'POST':
        f = requests.post
        assert json_data is not None, json_data
        kw['json'] = json_data
    elif mode == 'PATCH':
        f = requests.patch
        assert json_data is not None, json_data
        kw['json'] = json_data
    elif mode == 'GET':
        assert json_data is None, json_data
        f = requests.get

    if json_data:
        debug_json(f'{mode} to {url}', json_data)
    json_data = f(**kw).json()
    debug_json(f'Got from {url}', json_data)
    return json_data


BACKPORT_MARKER = 'BACKPORT'

def handle_workflow_run(http, event_json):
    workflow = event_json['workflow']
    workflow_run = event_json['workflow_run']
    head_repo = workflow_run.pop('head_repository')
    repo = workflow_run.pop('repository')

    repo_owner = head_repo['owner']['login']
    repo_name = head_repo['name']
    repo_slug = f"{repo_owner}/{repo_name}"

    debug_json('workflow json', workflow)
    debug_json('workflow_run json', workflow_run)

    head_branch = workflow_run['head_branch']
    if not head_branch.startswith('backport/'):
        raise SystemError('Invalid workflow_run event!')
    pr_id, seq_dat, workflow_branch = backport_branch_info(head_branch)

    print(
        f'Workflow run comes from backport of',
        f'Pull request #{pr_id}',
        f'run #{seq_dat[0]} (with git hash {seq_dat[1]})',
        f'to {workflow_branch}',
    )

    # Check the this workflow's 'checks' json
    workflow_check_runs = get_github_json(workflow_run['check_suite_url']+'/check-runs')
    assert 'check_runs' in workflow_check_runs, workflow_check_runs
    workflow_check_runs = workflow_check_runs['check_runs']

    # Get the pull request's 'checks' json.
    commits_url = head_repo['commits_url']
    SHA_MARKER = '{/sha}'
    assert commits_url.endswith(SHA_MARKER), commits_url
    pr_check_runs = get_github_json(commits_url.replace(SHA_MARKER, f'/{seq_dat[1]}/check-runs'))
    assert 'check_runs' in pr_check_runs, pr_check_runs
    pr_check_runs = pr_check_runs['check_runs']

    head_sha = set()

    backport_check_runs = []
    for check in pr_check_runs:
        check.pop('app')
        head_sha.add(check['head_sha'])

        if check['external_id'].startswith(BACKPORT_MARKER):
            backport_check_runs.append(check)

    assert len(head_sha) == 1, head_sha
    head_sha = head_sha.pop()
    assert head_sha.startswith(seq_dat[1]), (head_sha, seq_dat[1])
    debug()
    debug('Found head_sha values of:', head_sha)
    debug()


    extid2run = {}
    for check in backport_check_runs:
        pr_check_runs.remove(check)

        eid = check['external_id']
        marker, pr_check_branch, workflow_name, check_name = eid.split('$', 4)
        assert marker == BACKPORT_MARKER, eid
        extid2run[(pr_check_branch, workflow_name, check_name)] = check['id']

    group_start('Existing backported check_runs', debug)
    pprint.pprint(extid2run)
    group_end()

    print('='*75)
    for check in workflow_check_runs:
        check.pop('app')
        pprint.pprint(check)
        assert 'name' in check
        extid = (workflow_branch, workflow_run['name'], check['name'])

        key_action = {
            'owner':            'add',
            'repo':             'add',
            'name':             'replace',
            'head_sha' :        'replace',
            'details_url':      'keep',
            'external_id' :     'replace',
            'status':           'keep',
            'started_at':       'keep',
            'conclusion':       'keep',
            'completed_at':     'keep',
            'output':           'keep',

            'check_suite':      'remove',
            'html_url' :        'remove',
            'id':               'remove',
            'node_id':          'remove',
            'pull_requests':    'remove',
            'url':              'remove',
            #'url':              'keep',
        }

        new_check = {}
        for k, v in sorted(check.items()):
            if k not in key_action:
                raise ValueError(f"{k} not found.")

            action = key_action.pop(k)
            if action == 'remove':
                continue

            elif action == 'keep':
                if check[k] is not None:
                    new_check[k] = check[k]

            elif action == 'replace':
                if k == 'external_id':
                    new_check[k] = '$'.join([BACKPORT_MARKER]+list(extid))
                elif k == 'head_sha':
                    new_check[k] = head_sha
                elif k == 'name':
                    new_check[k] = f"{workflow_branch}: {workflow_run['name']} - {check['name']}"
            else:
                raise ValueError(f"Unknown action {action}")

        for k, action in sorted(key_action.items()):
            if action == "add":
                key_action.pop(k)
                assert k not in new_check, f"{k} is already exists in {new_check}"
                if k == 'owner':
                    new_check['owner'] = repo_owner
                elif k == 'repo':
                    new_check['repo'] = repo_name

        assert not key_action, key_action

        # Invalid request. For 'properties/summary', nil is not a string.
        if not new_check['output']['summary']:
            new_check['output']['summary'] = f"""\
Run of {workflow_run['name']} - {check['name']} on Pull Request #{pr_id} (run #{seq_dat[0]} with git hash {seq_dat[1]}) backported to {workflow_branch}.
"""
        # Invalid request. For 'properties/title', nil is not a string.
        if not new_check['output']['title']:
            new_check['output']['title'] = new_check['name']

        # Invalid request. For 'properties/text', nil is not a string.
        if not new_check['output']['text']:
            new_check['output']['text'] = new_check['output']['summary']

        print()
        print("New check")
        print('-'*75)
        pprint.pprint(new_check)
        print('-'*75)

        if extid not in extid2run:
            print()
            print('Need to *create* this check.')
            pr_check_api_url = commits_url.replace('/commits'+SHA_MARKER, f'/check-runs')
            r = send_github_json(pr_check_api_url, 'POST', new_check)
        else:
            print('Need to *update* this check.')
            pr_check_api_url = commits_url.replace('/commits'+SHA_MARKER, f"/check-runs/{extid2run[extid]}")
            r = send_github_json(pr_check_api_url, 'PATCH', new_check)

        print()
        print('Result')
        print('-'*50)
        pprint.pprint(r)
        print('-'*50)
