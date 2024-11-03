from os.path import dirname, isdir, isfile, join
from os import makedirs
import queue
import re
import requests
import threading
import time


class ManifestReader():
    def __init__(self, manifest):
        self.entries = []
        for line in manifest.splitlines():
            line = line.rstrip()
            checksum, path = re.split(r"\s+", line, 1)
            self.entries.append({
                "path": path,
                "checksum": checksum,
            })



class Manifest():
    url = None

    def __init__(self, **kwargs):
        if "url" in kwargs:
            self.url = kwargs["url"]
            r = requests.get(self.url)
            self.manifest_reader = ManifestReader(r.content.decode())
            self.entries = self.manifest_reader.entries


class Tagmanifest(Manifest):
    def manifest_base(self):
        for entry in self.entries:
            if re.match(r"^manifest-\w+.txt$", entry["path"]):
                return entry["path"]


class Fetcher():
    preferred_algos = [
        "sha256",
        "md5",
    ]

    dips_host = "https://exploreuk.uky.edu/dips"
    download_dir = None
    tagmanifest_url = None
    tagmanifest = None
    manifest_url = None
    manifest = None
    q = queue.Queue()

    def __init__(self, **kwargs):
        if "download_dir" in kwargs:
            self.download_dir = kwargs["download_dir"]
        if "ark" in kwargs:
            self.ark = kwargs["ark"]
            self.tagmanifest_url = None
            for algo in self.preferred_algos:
                tagmanifest_url = f"{self.dips_host}/{self.ark}/tagmanifest-{algo}.txt"
                r = requests.head(tagmanifest_url)
                if r.status_code == 200:
                    self.tagmanifest_url = tagmanifest_url
                    if self.tagmanifest_url is not None:
                        self.tagmanifest = Tagmanifest(url=self.tagmanifest_url)
                        if self.download_dir is not None:
                            self.fetch_metadata()
                            manifest_base = self.tagmanifest.manifest_base()
                            self.manifest_url = f"{self.dips_host}/{self.ark}/{manifest_base}"
                            if self.manifest_url is not None:
                                self.manifest = Manifest(url=self.manifest_url)
                    break

    def fetch_metadata(self):
        for entry in self.tagmanifest.entries:
            file = join(self.download_dir, entry["path"])
            if isfile(file):
                continue
            url = f"{self.dips_host}/{self.ark}/{entry["path"]}"
            r = requests.get(url, allow_redirects=True)
            if not(isdir(dirname(file))):
                makedirs(dirname(file), mode=0o775)
            with open(file, "wb") as file:
                file.write(r.content)


    # Worker pool is based on
    #    https://stackoverflow.com/a/59278125/
    def fetch_worker(self):
        while True:
            item = self.q.get()
            if item is None:
                break
            print(f"({self.q.qsize()}) Downloading {item}", flush=True)
            if not(isfile(item)):
                url = f"{self.dips_host}/{self.ark}/{item}"
                downloaded = False
                fiba = 0
                fibb = 1
                fibc = 1
                while not(downloaded):
                    r = requests.get(url, allow_redirects=True)
                    if r.status_code == 200:
                        downloaded = True
                        break
                    plural = "s" if (fibc != 1) else ""
                    print(f"*Delay on {item}, sleeping {fibc} second{plural} and trying again", flush=True)
                    time.sleep(fibc)
                    fiba = fibb
                    fibb = fibc
                    fibc = fiba + fibb
                file = join(self.download_dir, item)
                if not(isdir(dirname(file))):
                    try:
                        makedirs(dirname(file), mode=0o775)
                    except:
                        pass
                with open(file, "wb") as file:
                    file.write(r.content)
            time.sleep(1)
            self.q.task_done()


    def start_workers(self):
        self.threads = []
        for _ in range(self.thread_count):
            t = threading.Thread(target=self.fetch_worker)
            t.start()
            self.threads.append(t)


    def stop_workers(self):
        for _ in self.threads:
            self.q.put(None)
        for t in self.threads:
            t.join()
            

    def fetch_payload(self, **kwargs):
        if "threads" in kwargs:
            self.thread_count = kwargs["threads"]
        else:
            self.thread_count = 1
        self.workers = self.start_workers()
        for entry in self.manifest.entries:
            self.q.put(entry["path"])
        self.q.join()
        self.stop_workers()
