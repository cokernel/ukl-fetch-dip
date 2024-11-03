import pytest
import re

from ukl_fetch_dip.fetcher import Fetcher

def test_when_looking_for_tagmanifest_tries_sha256_first():
    fetcher = Fetcher()
    assert fetcher.preferred_algos[0] == "sha256"


# brittle
def test_can_find_tagmanifest(tmp_path):
    tmp_dir = tmp_path / "download_dir"
    tmp_dir.mkdir()
    fetcher = Fetcher(ark="xt7x3f4knz7q", download_dir=tmp_path)
    assert fetcher.tagmanifest.url == "https://exploreuk.uky.edu/dips/xt7x3f4knz7q/tagmanifest-sha256.txt"


def test_can_find_tagmanifest_if_not_preferred(tmp_path):
    tmp_dir = tmp_path / "download_dir"
    tmp_dir.mkdir()
    fetcher = Fetcher(ark="xt7w3r0pt52q", download_dir=tmp_path)
    assert fetcher.tagmanifest.url == "https://exploreuk.uky.edu/dips/xt7w3r0pt52q/tagmanifest-md5.txt"


def test_can_download_bag_metadata(tmp_path):
    tmp_dir = tmp_path / "download_dir"
    tmp_dir.mkdir()
    fetcher = Fetcher(ark="xt7x3f4knz7q", download_dir=tmp_dir)
    expected_files = [
        "bag-info.txt",
        "bagit.txt",
        "manifest-sha256.txt",
        "manifest-md5.txt",
    ]
    for file in expected_files:
        path = tmp_dir / file
        assert path.is_file()


def test_can_find_manifest(tmp_path):
    tmp_dir = tmp_path / "download_dir"
    tmp_dir.mkdir()
    fetcher = Fetcher(ark="xt7x3f4knz7q", download_dir=tmp_dir)
    assert re.match(r"^https://exploreuk.uky.edu/dips/xt7x3f4knz7q/manifest-\w+.txt", fetcher.manifest.url)


def test_can_fetch_payload(tmp_path):
    tmp_dir = tmp_path / "download_dir"
    tmp_dir.mkdir()
    fetcher = Fetcher(ark="xt7w3r0pt52q", download_dir=tmp_dir)
    print("fetching payload...", flush=True)
    fetcher.fetch_payload()
    print("Done", flush=True)
    for entry in fetcher.manifest.entries:
        path = tmp_dir / entry["path"]
        assert path.is_file()
