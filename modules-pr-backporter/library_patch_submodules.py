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
from library_submodules import git
from library_submodules import out_v
from library_submodules import previous_v
from library_submodules import get_sequence_number
from library_submodules import git_issue_comment
from library_submodules import git_issue_close
from library_submodules import get_git_root
from library_submodules import git_fetch
from library_submodules import get_lib_versions
from library_submodules import git_clean


__dir__ = os.path.dirname(__file__)

GH_PULLREQUEST_NAMESPACE = 'backport/{pr_id}/{seq_id}/{branch}'


def library_patch_submodules(
        patchfile, pull_request_id, repo_name, access_token, commit_hash):

    assert os.path.exists(patchfile), patchfile
    assert os.path.isfile(patchfile), patchfile

    print()
    print()
    git_root = get_git_root()

    git_fetch(git_root)

    versions = get_lib_versions(git_root)
    failed = True
    apply_idx = 0
    for i, v in enumerate(versions):
        pv = previous_v(v, versions)
        ov = out_v(v, versions)

        v_branch = "branch-{}.{}.{}".format(*ov)
        v_tag = "v{}.{}.{}".format(*ov)

        print()
        print("Was:", pv, "Now patching", (v_branch, v_tag), "with", patchfile)
        print('-'*20, flush=True)

        # Get us back to a very clean tree.
        # git('reset --hard HEAD', git_root)
        git_clean(git_root)

        # Checkout the right branch
        git('checkout {0}'.format(v_branch), git_root)

        diff_pos = 'branch-{}.{}.{}'.format(*pv)

        # Update the contents
        if v == versions[apply_idx]:
            if git('am {}'.format(patchfile),
                    git_root, can_fail=True) is False:
                apply_idx += 1
                git('am --abort', git_root)
            failed = False
            continue
        # Create the merge commit
        git('merge {} --no-ff --no-commit --strategy=recursive'
            .format(diff_pos),
            git_root)
        git('commit -C HEAD@{1}', git_root)
    if failed:
        return False
    git('branch -D master', git_root, can_fail=True)
    git('branch master', git_root)

    print('='*75, flush=True)

    old_git_sequence = int(get_sequence_number(pull_request_id))
    sequence_increment = 1
    if old_git_sequence != -1:
        old_pr_branch = \
            GH_PULLREQUEST_NAMESPACE.format(
                pr_id=pull_request_id,
                seq_id=old_git_sequence,
                branch='master')
        git('checkout {0}'.format(old_pr_branch), git_root)
        internal_patch = subprocess.check_output(
            'git diff {0}..master'.format(old_pr_branch),
            shell=True).decode('utf-8').strip()
        print(internal_patch)
        print('**********************')
        if not len(internal_patch):
            sequence_increment = 0
        print(sequence_increment)
    git_sequence = old_git_sequence + sequence_increment

    n_branch_links = ""
    for i, v in enumerate(versions):
        ov = out_v(v, versions)
        v_branch = "branch-{}.{}.{}".format(*ov)
        v_tag = "v{}.{}.{}".format(*ov)
        print()
        print("Now Pushing", (v_branch, v_tag))
        print('-'*20, flush=True)

        n_branch = GH_PULLREQUEST_NAMESPACE.format(
            pr_id=pull_request_id, seq_id=git_sequence, branch=v_branch)
        branch_link = "https://github.com/{0}/tree/{1}".format(
            repo_name, n_branch)
        n_branch_links += "\n- {0}".format(branch_link)
        print("Now Pushing", n_branch)
        if git('push -f origin {0}:{1}'.format(v_branch, n_branch),
                git_root, can_fail=True) is False:
            print("""\
Pull Request {0} is coming from a fork and trying to update the workflow. \
We will skip it!!! \
""")
            return False

    print()
    n_branch = GH_PULLREQUEST_NAMESPACE.format(
        pr_id=pull_request_id, seq_id=git_sequence, branch='master')
    branch_link = "https://github.com/{0}/tree/{1}".format(repo_name, n_branch)
    n_branch_links += "\n- {0}".format(branch_link)

    print("Now Pushing", n_branch)
    print('-'*20, flush=True)
    if git('push -f origin master:{0}'.format(n_branch),
            git_root, can_fail=True) is False:
        print("""\
Pull Request {0} is coming from a fork and trying to update the workflow. \
We will skip it!!! \
""")
        return False

    if sequence_increment:
        comment_body = """\
The latest commit of this PR, commit {0} has been applied to the branches, \
please check the links here:
 {1}
""".format(commit_hash, n_branch_links)
        git_issue_comment(repo_name,
                          pull_request_id,
                          comment_body,
                          access_token)
    return True


def library_merge_submodules(pull_request_id, repo_name, access_token):
    print()
    print()
    git_root = get_git_root()

    git_fetch(git_root)

    versions = get_lib_versions(git_root)
    for i, v in enumerate(versions):
        pv = previous_v(v, versions)
        ov = out_v(v, versions)

        v_branch = "branch-{}.{}.{}".format(*ov)
        v_tag = "v{}.{}.{}".format(*ov)
        git_sequence = int(get_sequence_number(pull_request_id))
        n_branch = GH_PULLREQUEST_NAMESPACE.format(
            pr_id=pull_request_id, seq_id=git_sequence, branch=v_branch)
        print()
        print("Was:", pv, "Now updating", (v_branch, v_tag), "with", n_branch)
        print('-'*20, flush=True)

        # Get us back to a very clean tree.
        # git('reset --hard HEAD', git_root)
        git_clean(git_root)

        # Checkout the right branch
        git('checkout {0}'.format(v_branch), git_root)
        print("Now reseting ", v_branch, " to ", n_branch)
        git('reset --hard origin/{0}'.format(n_branch), git_root)
        print("Now Pushing", v_branch)
        git('push -f origin {0}:{0}'.format(v_branch), git_root)
        for i in range(git_sequence + 1):
            d_branch = GH_PULLREQUEST_NAMESPACE.format(
                pr_id=pull_request_id, seq_id=i, branch=v_branch)
            git('push origin --delete {0}'.format(d_branch),
                git_root)

    git_clean(git_root)
    n_branch = GH_PULLREQUEST_NAMESPACE.format(
        pr_id=pull_request_id, seq_id=git_sequence, branch='master')
    git('checkout master', git_root)
    print("Now reseting master to ", n_branch)
    git('reset --hard origin/{0}'.format(n_branch), git_root)
    print("Now Pushing", v_branch)
    git('push -f origin master:master', git_root)
    for i in range(git_sequence + 1):
        d_branch = GH_PULLREQUEST_NAMESPACE.format(
            pr_id=pull_request_id, seq_id=i, branch='master')
        git('push origin --delete {0}'.format(d_branch),
            git_root)
    git_issue_close(repo_name, pull_request_id, access_token)
    comment_body = """\
Thank you for your pull request. This pull request will be closed, because \
the Pull-Request Merger has successfully applied it internally to all \
branches.
"""
    git_issue_comment(repo_name, pull_request_id, comment_body, access_token)


def library_rebase_submodules(pull_request_id):
    print()
    print()
    git_root = get_git_root()

    git_fetch(git_root)

    versions = get_lib_versions(git_root)
    for i, v in enumerate(versions):
        pv = previous_v(v, versions)
        ov = out_v(v, versions)

        v_branch = "branch-{}.{}.{}".format(*ov)
        v_tag = "v{}.{}.{}".format(*ov)
        git_sequence = int(get_sequence_number(pull_request_id))
        n_branch = GH_PULLREQUEST_NAMESPACE.format(
            pr_id=pull_request_id, seq_id=git_sequence, branch=v_branch)
        print()
        print("Was:", pv,
              "Now rebasing ", n_branch,
              " with ", (v_branch, v_tag))
        print('-'*20, flush=True)

        # Get us back to a very clean tree.
        # git('reset --hard HEAD', git_root)
        git_clean(git_root)

        # Checkout the right branch
        git('checkout {0}'.format(n_branch), git_root)
        git('rebase origin/{0}'.format(v_branch), git_root)
        print("Now Pushing", n_branch)
        git('push -f origin {0}:{0}'.format(n_branch), git_root)

    git_clean(git_root)
    n_branch = GH_PULLREQUEST_NAMESPACE.format(
        pr_id=pull_request_id, seq_id=git_sequence, branch='master')
    git('checkout {0}'.format(n_branch), git_root)
    git('rebase origin/master', git_root)
    print("Now Pushing", n_branch)
    git('push -f origin {0}:{0}'.format(n_branch), git_root)


def library_clean_submodules(all_open_pull_requests):
    print()
    print()
    print("Cleaning up pull request branches for closed pull requests.")
    git_root = get_git_root()

    git_fetch(git_root)

    all_branches = subprocess.check_output('git branch -r',
                                           shell=True).decode('utf-8').split()
    print("All branchs:", all_branches)
    for br in all_branches:
        if "origin/pullrequest/temp/" in br \
                and br.split('/')[3] not in all_open_pull_requests:
            print('Deleting ', br)
            git('push origin --delete {0}'.format(br.split('origin/', 1)[1]),
                git_root)


def main(args):
    assert len(args) == 5
    patchfile = os.path.abspath(args.pop(0))
    pull_request_id = args.pop(0)
    repo_name = args.pop(0)
    access_token = args.pop(0)
    commit_hash = args.pop(0)
    library_patch_submodules(
        patchfile, pull_request_id, repo_name, access_token, commit_hash)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
