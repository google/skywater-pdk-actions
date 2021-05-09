``skywater-pdk-actions`` - ``modules-pr-backporter``
====================================================

This is a Pull Request Merger Action that works on repos with release
branch structure.

This is mainly done for the ``google/skywater-pdk-libs-*`` repositories.

Workflow
========

Current Workflow when the action is invoked:

- The Action will loop over all open PRs and download each as a patch.

- The Action will apply the patch to all version branches merging upward
  whenever applying is possible.

- The Action will reset the master to the latest version branch.

- The changes will be saved in new branches named as
  ``backport/<pull request ID>/<sequence number>/<branch name>`` where sequence
  number reflects the number of the latest commit added to this PR incremented
  with each commit to that PR.

- If a PR is labeled ``ready-to-merge``, branch
  ``backport/<pull request ID>/<sequence number>/<branch name>`` becomes
  ``<branch name>`` for all the branches in the repository to which the patch
  applies.

Release branches should follow this structure: ``branch-*.*.*``

Each branch should have a tag with this structure: ``v*.*.\*``


Usage:
======

In Pull-Request Invoked Workflow, add the following:

.. literalinclude:: examples/workflow.yml
    :language: yml


Examples
========

There is an example `here <examples/pull_request_merger.yml>`__


.. include:: ../docs/contributing.rst

.. include:: ../docs/license.rst
