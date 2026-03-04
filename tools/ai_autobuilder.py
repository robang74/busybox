#!/usr/bin/env python3

import sys

from ai_config import MAX_ATTEMPTS, BUILD_CMD, BUSYBOX_HINT
from ai_repo import get_repo_tree, get_recent_diff, tail_build_log
from ai_build import run_build
from ai_llm import call_llm
from ai_patch import extract_unified_diff, apply_patch

PROMPT = """You are an automated build fixer working in a Git repository.

Goal:
Fix BusyBox build failures by editing files.

Repository files:
{repo_tree}

Recent git diff:
{recent_diff}

Build command:
{build_cmd}

Build log:
{build_tail}

Project notes:
{project_hint}

Rules:
- Return ONLY a unified diff
- Start with --- and +++
- Minimal safe edits
- Prefer fixing .config or Makefile for BusyBox
"""


def main():

    print("== AI BusyBox Autobuilder ==")

    code = run_build()

    if code == 0:
        print("Build already works.")
        return 0

    attempts = 0

    while attempts < MAX_ATTEMPTS:

        attempts += 1

        print(f"\nAttempt {attempts}/{MAX_ATTEMPTS}")

        prompt = PROMPT.format(
            repo_tree=get_repo_tree(),
            recent_diff=get_recent_diff(),
            build_cmd=BUILD_CMD,
            build_tail=tail_build_log(),
            project_hint=BUSYBOX_HINT
        )

        llm_out = call_llm(prompt)

        diff = extract_unified_diff(llm_out)

        if not diff:
            print("No valid patch returned.")
            break

        print("\nPatch preview:\n")
        print(diff[:1500])

        if not apply_patch(diff):
            break

        code = run_build()

        if code == 0:
            print("Build fixed!")
            return 0

    print("Still failing.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
