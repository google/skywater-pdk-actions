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

How to Contribute
=================

We'd love to accept your patches and contributions to this project.
There are just a few small guidelines you need to follow.

Contributor License Agreement
-----------------------------

Contributions to this project must be accompanied by a Contributor
License Agreement. You (or your employer) retain the copyright to your
contribution; this simply gives us permission to use and redistribute
your contributions as part of the project. Head over to
https://cla.developers.google.com/ to see your current agreements on
file or to sign a new one.

You generally only need to submit a CLA once, so if you've already
submitted one (even if it was for a different project), you probably
don't need to do it again.

Code reviews
------------

All submissions, including submissions by project members, require
review. We use GitHub pull requests for this purpose. Consult `GitHub
Help <https://help.github.com/articles/about-pull-requests/>`__ for more
information on using pull requests.

Community Guidelines
--------------------

This project follows `Google's Open Source Community
Guidelines <https://opensource.google/conduct/>`__.

At Google, we recognize and celebrate the creativity and collaboration
of open source contributors and the diversity of skills, experiences,
cultures, and opinions they bring to the projects and communities they
participate in.

Every one of Google's open source projects and communities are inclusive
environments, based on treating all individuals respectfully, regardless
of gender identity and expression, sexual orientation, disabilities,
neurodiversity, physical appearance, body size, ethnicity, nationality,
race, age, religion, or similar personal characteristic.

We value diverse opinions, but we value respectful behavior more.

Respectful behavior includes:

-  Being considerate, kind, constructive, and helpful.
-  Not engaging in demeaning, discriminatory, harassing, hateful,
   sexualized, or physically threatening behavior, speech, and imagery.
-  Not engaging in unwanted physical contact.

Some Google open source projects
`may adopt <https://opensource.google/docs/releasing/preparing/#conduct>`__
an explicit project code of conduct, which may have additional detailed
expectations for participants. Most of those projects will use our
`modified Contributor Covenant <https://opensource.google/docs/releasing/template/CODE_OF_CONDUCT/>`__.

Resolve peacefully
~~~~~~~~~~~~~~~~~~

We do not believe that all conflict is necessarily bad; healthy debate
and disagreement often yields positive results. However, it is never
okay to be disrespectful.

If you see someone behaving disrespectfully, you are encouraged to
address the behavior directly with those involved. Many issues can be
resolved quickly and easily, and this gives people more control over the
outcome of their dispute. If you are unable to resolve the matter for
any reason, or if the behavior is threatening or harassing, report it.
We are dedicated to providing an environment where participants feel
welcome and safe.

Reporting problems
~~~~~~~~~~~~~~~~~~

Some Google open source projects may adopt a project-specific code of
conduct. In those cases, a Google employee will be identified as the
Project Steward, who will receive and handle reports of code of conduct
violations. In the event that a project hasn’t identified a Project
Steward, you can report problems by emailing opensource@google.com.

We will investigate every complaint, but you may not receive a direct
response. We will use our discretion in determining when and how to
follow up on reported incidents, which may range from not taking action
to permanent expulsion from the project and project-sponsored spaces. We
will notify the accused of the report and provide them an opportunity to
discuss it before any action is taken. The identity of the reporter will
be omitted from the details of the report supplied to the accused. In
potentially harmful situations, such as ongoing harassment or threats to
anyone's safety, we may take action without notice.

*This document was adapted from the*
`IndieWeb Code of Conduct <https://indieweb.org/code-of-conduct>`_
*and can also be found at* <https://opensource.google/conduct/>.

License
=======

The SkyWater Open Source PDK GitHub actions are released under the
`Apache 2.0 license <https://github.com/google/skywater-pdk/blob/master/LICENSE>`_.

The copyright details (which should also be found at the top of every file) are;

::

   Copyright 2021 SkyWater PDK Authors

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.

