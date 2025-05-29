#!/usr/bin/env python3

import json
import os.path
import pprint
import re
import shutil
import subprocess
import sys
import tempfile
import urllib.request
import zipfile
from functools import cache
from typing import Any

SEMVER_RE = r"^v\d+\.\d+\.\d+$"

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

# class Semver:
#     major = 0
#     minor = 0
#     patch = 0
#
#     def __init__(self, major: int, minor: int, patch: int):
#         self.major = major
#         self.minor = minor
#         self.patch = patch


def perror(*values: object) -> None:
    print(file=sys.stderr, *values)


def current_simdutf_version() -> str:
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


def append_go_build_tag(filename: str) -> None:
    with open(filename, mode="r+t", encoding="utf-8") as f:
        src = f.read()
        f.seek(0, 0)
        f.truncate(0)
        f.write("//go:build !libsimdutf\n\n")
        f.write(src)


# TODO: rename to indicate that we also update the files
def download_release(version: str) -> None:
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

    version_file = os.path.join(PROJECT_ROOT, "SIMDUTF_VERSION")
    with open(version_file, mode="w+", encoding="utf-8") as f:
        f.write(f"{version}\n")


def test_new_release() -> None:
    subprocess.check_output(["go", "test", "-race", "./..."], cwd=PROJECT_ROOT)


def latest_simdutf_version() -> str:
    ver = latest_simdutf_release()["tag_name"]
    if not re.match(SEMVER_RE, ver):
        raise Exception(f"invalid semver: {ver}")
    return ver


def get_singleheader_download_url(rel: dict[str, Any]) -> str:
    for a in rel["assets"]:
        if a["name"] == "singleheader.zip":
            return a["browser_download_url"]
    raise Exception("singleheader not found in release")


def update_simdutf(target: str) -> None:
    rel = latest_simdutf_release()
    if rel["tag_name"] != target:
        raise Exception(f"latest simdutf release {rel["tag_name"]} != {target}")
    url = get_singleheader_download_url(rel)


def main() -> int:
    if current_simdutf_version() == latest_simdutf_version():
        return 0

    rel = latest_simdutf_release()
    if rel["draft"] or rel["prerelease"]:
        perror(f"Refusing to update to draft/pre-release version: {rel["tag_name"]}")
        return 1

    download_release(rel["tag_name"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
