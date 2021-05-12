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

"""
run_all_drc.py --- A script that will run run_standard_drc for all .gds files
under the cells/ folder.

Must be run from repository root.

Usage: python3 run_all_drc.py --help

Results:

  Prints a report to standard output.
"""

import os
import re
import subprocess
import traceback

from concurrent import futures
from typing import List, Tuple

import click

acceptable_errors = []

SCRIPT_DIR = os.path.realpath(os.path.dirname(__file__))
STANDARD_DRC_SCRIPT = os.path.join(SCRIPT_DIR, "run_standard_drc.py")
PDK_SUBSET = os.getenv("PDK_ROOT") or os.path.join(SCRIPT_DIR, "sky130A")

DRCError = Tuple[str, List[str]]


PARSE_DRC_REPORT_EXAMPLE = """
This first set of lines is the 'header':
DRC errors for a cell that doesn't exist
It's skipped over by this function.
--------------------------------------------

This is an acceptable error.
These lines are details for the acceptable error.
There are usually a couple of lines.

This is an unacceptable error.
These lines are details for the unacceptable error.
There are usually a couple of lines.

This is another unacceptable error.
It has less lines of detail.
"""


def parse_drc_report(
        report: str, acceptable_errors: List[str]) -> List[DRCError]:
    """
    Takes a magic report in the format as seen in PARSE_DRC_REPORT_EXAMPLE
    above, and returns all errors as a list of tuples, where the first element
    of the tuple is the name of the error and the other lines are the details.

    >>> from pprint import pprint as p
    >>> p(parse_drc_report(
    ...     PARSE_DRC_REPORT_EXAMPLE.strip(),
    ...     ["This is an acceptable error."]))
    [('This is an unacceptable error.',
      ['These lines are details for the unacceptable error.',
       'There are usually a couple of lines.']),
     ('This is another unacceptable error.', ['It has less lines of detail.'])]
    """
    components = [x.split("\n") for x in report.split("\n\n")]
    errors = []

    header = components.pop(0)  # noqa: F841

    for error in components:
        error_name = error[0]
        if error_name in acceptable_errors:
            continue
        errors.append((error[0], error[1:]))

    return errors


def drc_gds(path: str) -> Tuple[str, List[DRCError]]:
    """
    Takes a GDS path. Returns the name of the cell and returns a list of
    DRC errors.
    """
    cell_name = os.path.basename(path)[:-4]

    env = os.environ.copy()
    env["PDKPATH"] = PDK_SUBSET

    res = subprocess.run([
        "python3",
        STANDARD_DRC_SCRIPT,
        path
    ], env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    report_path = path[:-4] + "_drc.txt"
    try:
        report = open(report_path).read()

        if os.getenv("ACTIONS_STEP_DEBUG") or False:
            print("::group::%s" % report_path)
            print(report)
            print("::endgroup::")

        return cell_name, parse_drc_report(report, acceptable_errors)
    except FileNotFoundError:
        return cell_name, [
            (
                "Magic did not produce a report.",
                [res.stdout.decode("utf8"), res.stderr.decode("utf8")]
            )
        ]


@click.command()
@click.option(
    "-a",
    "--acceptable-errors-file",
    default="/dev/null",
    help="A file containing a list of newline-delimited acceptable DRC errors."
         " Default: No file will be read and all errors deemed unacceptable."
)
@click.option(
    "-m",
    "--match-directories",
    default=".",
    help="A regex that will match subdirectories under cells/."
         " Default: . (matches everything.)"
)
@click.option(
    "-b",
    "--known-bad",
    default="",
    help="A comma,delimited list of cells that are known bad and"
         " thus do not cause a non-zero exit upon failure."
         " Default: empty string (None of them.)"
)
def run_all_drc(acceptable_errors_file, match_directories, known_bad):
    print("Testing cells in directories matching /%s/…" % match_directories)

    global acceptable_errors
    acceptable_errors_str = open(acceptable_errors_file).read()
    acceptable_errors = acceptable_errors_str.split("\n")

    known_bad_list = known_bad.split(",")

    nproc = os.cpu_count()
    with futures.ThreadPoolExecutor(max_workers=nproc) as executor:
        future_list = []

        cells_dir = "./cells"
        cells = os.listdir(cells_dir)

        for cell in cells:
            if not re.match(match_directories, cell):
                print("Skipping directory %s…" % cell)
                continue

            cell_dir = os.path.join(cells_dir, cell)

            gds_list = list(
                filter(lambda x: x.endswith(".gds"), os.listdir(cell_dir))
            )

            for gds_name in gds_list:
                gds_path = os.path.join(cell_dir, gds_name)

                future_list.append(executor.submit(drc_gds, gds_path))

        successes = 0
        total = 0
        exit_code = 0
        for future in future_list:
            total += 1
            cell_name, errors = future.result()

            symbol = "❌"
            message = "ERROR"
            if len(errors) == 0:
                successes += 1
                # This tick is rendered black on all major platforms except for
                # Microsoft.
                symbol = "✔\ufe0f"
                message = "CLEAN"
            print("%-64s %s %s" % (cell_name, symbol, message))

            if len(errors) != 0:
                if cell_name not in known_bad_list:
                    exit_code = 65
                for error in errors:
                    print("* %s" % error[0])
                    for line in error[1]:
                        print("  %s" % line)

        success_rate = (successes / total * 100)
        print("%i/%i successes (%0.1f%%)" % (successes, total, success_rate))

        exit(exit_code)


def main():
    try:
        run_all_drc()
    except Exception:
        print("An unhandled exception has occurred.", traceback.format_exc())
        exit(69)


if __name__ == '__main__':
    main()
