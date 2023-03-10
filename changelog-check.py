#!/usr/bin/env python3

import argparse
import subprocess

from pathlib import Path
from typing import List


path = str(Path.cwd().absolute())


def run_command(command: List[str]):
    return subprocess.run(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=path,
    ).stdout.decode()


def skip_check(keyword: str, upstream_hash: str):
    # TODO decide whether it is needed for each commit
    # to contain the skip key-word or this solution is ok
    commit_messages = run_command(["git", "log", "--pretty=format:%b", f"{upstream_hash}.."])
    print(f"Commit messages: {commit_messages}")
    return keyword in commit_messages


def get_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--changelog-file-name",
        default="CHANGELOG.md"
    )
    parser.add_argument(
        "--skip-keyword",
        default="[changelog-check skip]"
    )
    parser.add_argument(
        "remote_url"
    )

    return parser.parse_args()


def main():
    args = get_arguments()
    upstream_hash = run_command(["git", "ls-remote", args.remote_url, "HEAD"]).split()[0]

    git_log_output = run_command(["git", "log", "--pretty=format:%H", f"{upstream_hash}.."])
    print(f"Git log output: {git_log_output})")

    if skip_check(args.skip_keyword, upstream_hash):
        print("Changelog check is being skipped.")
        return 0

    changed_files_output = run_command(
        ["git", "diff", "--name-only", f"{upstream_hash}..."],
    )
    print(f"Changed files output: {changed_files_output}")

    changed_files = changed_files_output.strip().split('\n')

    if args.changelog_file_name in changed_files:
        return 0

    print(f"The changes against {args.branch_to_compare} do not contain any update"
          f" of {args.changelog_file_name}!")
    return 1


if __name__ == "__main__":
    exit(main())
