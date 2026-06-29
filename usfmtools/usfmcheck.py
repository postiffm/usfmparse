#!/usr/bin/env python3
"""
USFM Checker - Validates USFM files for marker correctness.

Checks for paired markers not explicitly closed and unknown markers.

Usage:
    python usfmtools/usfmcheck.py file.usfm
    python usfmtools/usfmcheck.py *.usfm
    python usfmtools/usfmcheck.py --no-unknown file.usfm
    python usfmtools/usfmcheck.py --no-unclosed file.usfm
"""

import sys
import io
import click
from usfmtools.usfmcheckerlib import UsfmChecker


if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


@click.command()
@click.option(
    '--unclosed/--no-unclosed',
    default=True,
    help='Check for paired markers not explicitly closed. Default: True'
)
@click.option(
    '--unknown/--no-unknown',
    default=True,
    help='Check for unknown/illegal markers. Default: True'
)
@click.argument('files', nargs=-1, required=True)
def main(unclosed: bool, unknown: bool, files: tuple) -> None:
    """
    Check USFM files for marker correctness.

    Processes one or more USFM files and reports issues to stdout.
    Exit code is 0 if no issues found, 1 if issues were found.
    """
    checker = UsfmChecker(check_unclosed=unclosed, check_unknown=unknown)
    total_issues = 0

    for filename in files:
        try:
            issues = checker.check_file(filename)
            for issue in issues:
                print(issue)
            total_issues += len(issues)
        except FileNotFoundError:
            print(f"Error: File not found: {filename}", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print(f"Error processing {filename}: {e}", file=sys.stderr)
            sys.exit(1)

    if total_issues == 0:
        print("No issues found.")
    else:
        print(f"\n{total_issues} issue(s) found.")

    sys.exit(0 if total_issues == 0 else 1)


if __name__ == '__main__':
    main()
