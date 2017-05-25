import os
import re
import json
import requests
import webbrowser
from urllib.parse import quote_plus

SEARCH_URL = 'http://libgen.io/search.php?req={}&res=100&column=def'
LOOKUP_URL = 'http://libgen.io/json.php?ids={}&fields={}'
DOWNLOAD_URL = 'http://libgen.io/get.php?md5={}'

def search(query,fields=['title', 'author', 'year', 'edition', 'pages', 'identifier', 'extension', 'filesize', 'md5']):
    url = SEARCH_URL.format(quote_plus(query))
    r = requests.get(url); r.raise_for_status()
    ids = re.findall("<tr.*?><td>(\d+)", r.text)
    return requests.get(LOOKUP_URL.format(','.join(ids), ','.join(fields))).json()

def get_download_url(md5):
    url = DOWNLOAD_URL.format(md5)
    r = requests.get(url); r.raise_for_status()
    key = re.findall("&key=(.*?)'", r.text)[0]
    return url + '&key={}'.format(key)

def download(x):
    r = requests.get(get_download_url(x['md5'])); r.raise_for_status()

    with open(os.path.join('.', x['md5']), 'wb') as f:
        for chunk in r.iter_content(1024):
            f.write(chunk)
