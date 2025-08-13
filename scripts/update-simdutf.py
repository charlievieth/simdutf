#!/usr/bin/env python3

import json
import logging
import os.path
import re
import shutil
import subprocess
import sys
import tempfile
import urllib.parse
import urllib.request
import zipfile
from functools import cache
from typing import Any
from typing import Callable

SEMVER_RE = r"^v\d+\.\d+\.\d+$"

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))


def get_logger(level: int = logging.INFO) -> logging.Logger:
    logging.basicConfig(
        level=level,
        format="[%(levelname)s] [%(filename)s:%(lineno)d]: %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )
    return logging.getLogger("update-simdutf")


# Global logger
log = get_logger()


def current_simdutf_version() -> str:
    """Return the version of the bundled simdutf library."""
    with open(os.path.join(PROJECT_ROOT, "SIMDUTF_VERSION"), encoding="utf-8") as f:
        return f.read().strip()


@cache
def latest_simdutf_release() -> dict[str, Any]:
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    req = urllib.request.Request(
        url="https://api.github.com/repos/simdutf/simdutf/releases/latest",
        headers=headers,
        method="GET",
    )
    with urllib.request.urlopen(req, timeout=5) as f:
        return json.load(f)


def modify_file(filename: str, fn: Callable[[str], str]) -> None:
    with open(filename, mode="r+t", encoding="utf-8") as f:
        src = f.read()
        f.seek(0, 0)
        f.truncate(0)
        f.write(fn(src))


def append_go_build_tag(filename: str) -> None:
    def fn(src: str) -> str:
        if "//go:build !libsimdutf" not in src:
            src = "//go:build !libsimdutf\n\n" + src
        return src

    modify_file(filename, fn)


def update_release(version: str) -> None:
    req = urllib.request.Request(
        url=f"https://github.com/simdutf/simdutf/releases/download/{version}/singleheader.zip",
        method="GET",
    )

    with tempfile.TemporaryDirectory(prefix="go-simdutf-") as tmp:
        dst = os.path.join(tmp, "singleheader.zip")
        with open(dst, mode="xb") as out:
            with urllib.request.urlopen(req, timeout=5) as rf:
                out.write(rf.read())
            with zipfile.ZipFile(dst, "r") as zf:
                zf.extractall(tmp)

        for name in ["simdutf.cpp", "simdutf.h"]:
            # Append Go build tags so that these files are excluded
            # when we link to a system installed simdutf library.
            append_go_build_tag(os.path.join(tmp, name))
            shutil.copyfile(
                src=os.path.join(tmp, name),
                dst=os.path.join(PROJECT_ROOT, name),
            )

    def update_readme(src: str) -> str:
        # The earliest supported version of simdutf is v7.x.x
        for m in re.findall(r"(v[7-9]\d*\.\d+\.\d+)", src):
            src = src.replace(m, version)
        return src

    modify_file(
        os.path.join(PROJECT_ROOT, "README.md"),
        update_readme,
    )
    modify_file(
        os.path.join(PROJECT_ROOT, "SIMDUTF_VERSION"),
        lambda _: f"{version}\n",
    )


def run_go_tests() -> None:
    subprocess.check_call(
        ["go", "test", "-race", "./..."],
        cwd=PROJECT_ROOT,
        stdout=sys.stdout,
        stderr=sys.stderr,
    )


def latest_simdutf_version() -> str:
    ver = latest_simdutf_release()["tag_name"]
    if not re.match(SEMVER_RE, ver):
        raise Exception(f"invalid semver: {ver}")
    return ver


def git(*args) -> str:
    try:
        return subprocess.check_output(
            ["git"] + list(args),
            cwd=PROJECT_ROOT,
            stderr=subprocess.STDOUT,
            encoding="utf-8",
        )
    except subprocess.CalledProcessError as e:
        log.error(
            "Command '%s' exited with code: %d: %s",
            e.cmd,
            e.returncode,
            e.output.strip() if e.output else "<NONE>",
        )
        raise e


def pr_exists(branch_name: str) -> bool:
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    query = urllib.parse.urlencode({"head": f"charlievieth:{branch_name}"})
    req = urllib.request.Request(
        url=f"https://api.github.com/repos/charlievieth/simdutf/pulls?{query}",
        headers=headers,
        method="GET",
    )
    with urllib.request.urlopen(req, timeout=5) as f:
        return len(json.load(f)) == 0


def modified_files() -> set[str]:
    pattern = re.compile(r"^\s*M\s+(.*)")
    modified = []
    for line in git("status", "--porcelain").splitlines():
        if len(m := pattern.findall(line)):
            modified.append(m[0])
    return set(modified)


def branch_name(version: str) -> str:
    return f"deps/{version}"


def create_pr(old_version: str, new_version: str) -> str:
    if not modified_files():
        raise RuntimeError("no files were modified")

    branch = branch_name(new_version)
    git("checkout", "-b", branch)
    git("add", "--update", "simdutf.h", "simdutf.cpp", "SIMDUTF_VERSION", "README.md")
    git(
        "commit",
        "-m",
        f"deps: update bundled library version from {old_version} to {new_version}",
        "-m",
        f"Update the bundled simdutf library from version {old_version} to {new_version}.",
    )
    return branch


def push_pr(branch: str, old_version: str, new_version: str, auth_token: str) -> None:
    if pr_exists(branch):
        log.warn("PR already exists for version %s: nothing to do", new_version)
        return

    title = f"deps: update bundled library version from {old_version} to {new_version}"
    old_url = f"[{old_version}](https://github.com/simdutf/simdutf/releases/tag/{old_version})"
    new_url = f"[{new_version}](https://github.com/simdutf/simdutf/releases/tag/{new_version})"
    body = {
        "title": title,
        "body": f"This commit updates the bundled simdutf library from version {old_url} to {new_url}",
        "head": branch,
        "base": "master",
    }
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": auth_token,
        "X-GitHub-Api-Version": "2022-11-28",
    }
    req = urllib.request.Request(
        url="https://api.github.com/repos/charlievieth/simdutf/releases/latest",
        headers=headers,
        data=json.dumps(body).encode("utf-8"),
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=5) as f:
        res = json.load(f)
    log.info("-- created pr:")
    json.dump(sys.stdout, res, indent=4)
    log.info("--")


def main() -> int:
    current_version = current_simdutf_version()
    latest_version = latest_simdutf_version()
    if current_version == latest_version:
        log.info(
            "nothing to do here: simdutf version %s is the latest: exiting",
            current_version,
        )
        return 0

    rel = latest_simdutf_release()
    if rel["draft"] or rel["prerelease"]:
        log.warn(
            "refusing to update to draft/pre-release version: %s",
            rel["tag_name"],
        )

    update_release(latest_version)
    run_go_tests()

    branch_name = create_pr(
        old_version=current_version,
        new_version=latest_version,
    )
    if not branch_name:
        return 0  # Nothing to do

    # TODO: add local version that uses `gh`
    if not os.environ.get("SIMDUTF_GH_ACTIONS"):
        log.fatal("missing SIMDUTF_GH_ACTIONS token - cannot create PR")
        return 1
    push_pr(
        branch=branch_name,
        old_version=current_version,
        new_version=latest_version,
        auth_token=os.environ["SIMDUTF_GH_ACTIONS"],
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
