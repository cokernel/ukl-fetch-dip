from ukl_fetch_dip.fetcher import Fetcher


if __name__ == "__main__":
    fetcher = Fetcher(ark="xt7x3f4knz7q", download_dir="test_329mb_xt7x3f4knz77q")
    fetcher.fetch_payload(threads=100)
