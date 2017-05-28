import os
import re
import json
import requests
import webbrowser
import sys
import time
from pprint import pprint
from urllib.parse import quote_plus

SEARCH_URL = 'http://libgen.io/search.php?req={}&res=25&column=def'
LOOKUP_URL = 'http://libgen.io/json.php?ids={}&fields={}'
DOWNLOAD_URL = 'http://libgen.io/get.php?md5={}'

def pp(x):
    for i, v in enumerate(x): print("[%i]::n: %s, ed: %s, ext: %s, author: %s" % (i, v['title'], v['edition'], v['extension'], v['author']))

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

def download(x, path, name):
    with open(os.path.join(path, name), 'wb') as f:
        print("Downloading %s" % name)
        t_start=time.time() # Time just before download stream...
        r = requests.get(get_download_url(x['md5']), stream=True);
        length = r.headers.get('content-length')

        if length is None:
            print("Couldn't find length in response headers")
            f.write(r.content)
        else:
            dl = 0
            length = int(length)
            for data in r.iter_content(chunk_size=4096):
                dl += len(data)
                f.write(data)
                done = int(50 * dl / length)
                seconds = int(time.time() - t_start) % 60
                sys.stdout.write("\r[%s%s][%s/%s/%s secs] " % ('=' * done, ' ' * (50-done), dl, length, seconds) )
                sys.stdout.flush()
            print("/n")
