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
        # lambda src: src.replace(current_simdutf_version(), version),
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
    return subprocess.check_output(
        ["git"] + list(*args),
        cwd=PROJECT_ROOT,
        stderr=subprocess.STDOUT,
        encoding="utf-8",
    )


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


def create_pr(old_version: str, new_version: str, auth_token: str) -> None:
    branch = branch_name(new_version)
    if pr_exists(branch):
        log.warn("PR already exists for version %s: nothing to do", new_version)
        return

    if not modified_files():
        raise RuntimeError("no files were modified")

    git("checkout", "-b", branch)
    git("add", "--update", "simdutf.h", "simdutf.cpp", "SIMDUTF_VERSION", "README.md")

    title = f"deps: update bundled library version from {old_version} to {new_version}"
    git(
        "commit",
        "-m",
        title,
        "-m",
        "Update the bundled simdutf library from version {old_version} to {new_version}.",
    )

    def rel_url(version: str) -> str:
        return f"[{version}](https://github.com/simdutf/simdutf/releases/tag/{version})"

    body = {
        "title": title,
        "body": "This commit updates the bundled simdutf library from version "
        + f"{rel_url(old_version)} to {rel_url(new_version)}.",
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
        return 1

    update_release(latest_version)
    run_go_tests()
    if not os.environ["SIMDUTF_GH_ACTIONS"]:
        log.fatal("missing SIMDUTF_GH_ACTIONS token - cannot create PR")
        return 1
    create_pr(
        old_version=current_version,
        new_version=latest_version,
        auth_token=os.environ["SIMDUTF_GH_ACTIONS"],
    )

    return 0


class Semver:
    __slots__ = ("major", "minor", "patch", "tag")

    def __init__(self, major: int, minor: int, patch: int, tag: str = ""):
        self.major = major
        self.minor = minor
        self.patch = patch
        self.tag = tag

    def __str__(self) -> str:
        if self.tag:
            return f"v{self.major}.{self.minor}.{self.patch}-{self.tag}"
        return f"v{self.major}.{self.minor}.{self.patch}"

    def __repr__(self) -> str:
        if self.tag:
            return f"Semver({self.major}, {self.minor}, {self.patch}, {self.tag!r})"
        return f"Semver({self.major}, {self.minor}, {self.patch})"

    def __hash__(self) -> int:
        return hash((self.major, self.minor, self.patch, self.tag))

    def _compare(self, other: object) -> int:
        if not isinstance(other, Semver):
            return NotImplemented
        if (
            self.major == other.major
            and self.minor == other.minor
            and self.patch == other.patch
        ):
            if self.tag == other.tag:
                return 0
            return 1 if self.tag > other.tag else -1
        if (
            self.major < other.major
            or self.minor < other.minor
            or self.patch < other.patch
        ):
            return -1
        return 1

    # TODO: consider using a lambda
    # # TODO: consider using this
    # def _cmp(self, other: object, op: Callable[[int, int], bool], exp: int) -> bool:
    #     res = self._compare(other)
    #     if res is NotImplemented:
    #         return NotImplemented
    #     return op(res, exp)

    def __eq__(self, other: object) -> bool:
        # return self._cmp(other, operator.eq, 0)
        if not isinstance(other, Semver):
            return NotImplemented
        return self._compare(other) == 0

    def __ne__(self, other: object) -> bool:
        if not isinstance(other, Semver):
            return NotImplemented
        return self._compare(other) != 0

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, Semver):
            return NotImplemented
        return self._compare(other) < 0

    def __le__(self, other: object) -> bool:
        if not isinstance(other, Semver):
            return NotImplemented
        return self._compare(other) <= 0

    def __gt__(self, other: object) -> bool:
        if not isinstance(other, Semver):
            return NotImplemented
        return self._compare(other) > 0

    def __ge__(self, other: object) -> bool:
        if not isinstance(other, Semver):
            return NotImplemented
        return self._compare(other) >= 0

    @classmethod
    def parse(cls, ver: str) -> "Semver":
        orig = ver
        if ver.startswith("v"):
            ver = ver[1:]
        tag = ""
        if "-" in ver:
            (ver, tag) = ver.split("-", 1)
        a = ver.split(".")
        if len(a) == 3:
            return Semver(int(a[0]), int(a[1]), int(a[2]), tag)
        elif len(a) == 2:
            return Semver(int(a[0]), int(a[1]), 0, tag)
        elif len(a) == 1:
            return Semver(int(a[0]), 0, 0, tag)
        raise ValueError(f"semver: invalid format: '{orig}'")


if __name__ == "__main__":
    sys.exit(main())
