ukl-fetch-dip
=============

`ukl-fetch-dip` is a multithreaded DIP downloader for [ExploreUK](https://exploreuk.uky.edu).

This is experimental software and may become a more generic BagIt bag downloader
as development continues. As it stands it is very ExploreUK-centric.


Usage
-----

```python
from ukl_fetch_dip.fetcher import Fetcher

fetcher = Fetcher(ark="xt7x3f4knz7q", download_dir="test_329mb_xt7x3f4knz77q")
fetcher.fetch_payload(threads=100)
```


License
-------

Copyright (C) 2024 MLE Slone. Licensed under the [MIT license](LICENSE.md).

The worker pool is based on [code](https://stackoverflow.com/a/59278125/) by StackOverflow user [Ari](https://stackoverflow.com/users/5091805/ari) and is licensed under CC-by-SA.
