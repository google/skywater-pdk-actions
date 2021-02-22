``skywater-pdk-actions`` - ``modules-pr-backporter``
====================================================

This is a Pull Request Merger Action that works on repos with release
branch structure. This will overwrite the master branch to match the
latest release branch everytime.

This is mainly done for the google/skywater-pdk-libs-\* repositories.

Workflow
========

In collaboration with [@ax3ghazy](https://github.com/ax3ghazy), we
created this workflow for the Pull Request Merger.

Current Workflow when the action is invoked: - The Action will loop over
all open PRs and download each as a patch. - The Action will apply the
patch to all version branches merging upward whenever applying is
possible. - The Action will reset the master to the latest version
branch. - The changes will be saved in new branches named as
``pullrequest/temp/<PR ID>/<sequence number>/<branch name>`` where
sequence number reflects the number of the latest commit added to this
PR incremented with each commit to that PR. - If a PR is labeled
``ready-to-merge``, branch
``pullrequest/temp/<PR ID>/<sequence number>/<branch name>`` becomes
``<branch name>`` for all the branches in the repository to which the
patch applies.

Release branches should follow this structure: branch-*.*.\*

Each branch should have a tag with this strucutre: v*.*.\*

This action should only be invoked in case of a Pull Request. We don’t
handle corner cases at the moment.

Usage:
======

In Pull-Request Invoked Workflow, add the following:

.. code:: yml

       steps:
         - uses: actions/checkout@v2
           with:
             ref: master
             fetch-depth: '50'

         - name: Run The Pull Request Merger
           uses: agorararmard/skywater-pdk-modules-pull-request-backporter-action@main

Examples
========

There is an example `here <examples/pull_request_merger.yml>`__


.. include:: ../docs/contributing.rst

.. include:: ../docs/license.rst
