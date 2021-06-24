# cvpr-crawler
Download all conference posters and papers from CVPR.


# intall

Require: Python >= 3.6

```bash
pip install bs4 requests
```

# usage

Login to the [conference page](https://www.eventscribe.net/2021/2021CVPR/),
and get cookies from your favorite browser,
and save them in `cookies.json`:
```json
{
    "XXXXX": "AccountKey=XXXXXXXX",
    "ASPSESSIONIDCWBSCQDA": "XXXXXXXXXXXXXXXXXXXXXXXX",
    "ASPSESSIONIDCWRBASDC": "XXXXXXXXXXXXXXXXXXXXXXXX"
}
```

Run the following command:
```bash
python crawl.py
```
