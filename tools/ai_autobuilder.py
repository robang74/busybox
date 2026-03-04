#!/usr/bin/env python3

import sys
from pathlib import Path

from ai_config import MAX_ATTEMPTS, BUILD_CMD, BUSYBOX_HINT
from ai_repo import get_repo_tree, get_recent_diff, tail_build_log
from ai_build import run_build
from ai_llm import call_llm
from ai_patch import extract_unified_diff, apply_patch

# build intelligence
from build.detect import detect_build_type
from build.knowledge import record
from build.websearch import search_build_fix

# self-training memory
from ai_memory.memory import store_failure, store_fix, search_memory

PROJECT_ROOT = Path(".")


PROMPT = """You are an automated build fixer working in a Git repository.

Goal:
Fix build failures by editing files.

Detected build system:
{build_type}

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

Web hint (if available):
{web_hint}

Rules:
- Return ONLY a unified diff
- Start with --- and +++
- Minimal safe edits
- Prefer fixing configuration or build scripts
"""


def extract_first_error(log):

    """Try to extract the most useful error line"""

    lines = log.split("\n")

    for l in reversed(lines):
        if "error" in l.lower():
            return l

    return lines[-1] if lines else ""


def main():

    print("== AI Autobuilder ==")

    # detect build system
    build_type = detect_build_type(PROJECT_ROOT)

    print(f"Detected build system: {build_type}")

    code = run_build()

    log_tail = tail_build_log()

    # record run
    record(build_type, code == 0, log_tail)

    if code == 0:
        print("Build already works.")
        return 0

    # store failure for training
    store_failure(build_type, log_tail)

    attempts = 0

    while attempts < MAX_ATTEMPTS:

        attempts += 1

        print(f"\nAttempt {attempts}/{MAX_ATTEMPTS}")

        log_tail = tail_build_log()

        # check memory first
        mem_patch = search_memory(log_tail)

        if mem_patch:
            print("Found matching fix in local memory.")
            diff = mem_patch
        else:

            web_hint = ""

            try:
                err = extract_first_error(log_tail)
                web_hint = search_build_fix(err)
            except Exception:
                pass

            prompt = PROMPT.format(
                build_type=build_type,
                repo_tree=get_repo_tree(),
                recent_diff=get_recent_diff(),
                build_cmd=BUILD_CMD,
                build_tail=log_tail,
                project_hint=BUSYBOX_HINT if build_type == "busybox" else "",
                web_hint=web_hint
            )

            llm_out = call_llm(prompt)

            diff = extract_unified_diff(llm_out)

        if not diff:
            print("No valid patch returned.")
            break

        print("\nPatch preview:\n")
        print(diff[:1500])

        if not apply_patch(diff):
            print("Patch failed to apply.")
            break

        # save successful fix
        store_fix(diff)

        code = run_build()

        record(build_type, code == 0, tail_build_log())

        if code == 0:
            print("Build fixed!")
            return 0

    print("Still failing.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
