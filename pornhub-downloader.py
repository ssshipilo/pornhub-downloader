# -*- coding: utf-8 -*-

import os
import re
import time
import execjs
import requests
from tqdm import tqdm
from bs4 import BeautifulSoup
from requests_html import HTMLSession


def download_from_url(url, path, data):
    """
    Downloading videos from a pornhub link
    \n
    Accepts parameters:\n
    \t`url` - direct link to the video\n
    \t`path` - path to download + name of file with .mp4 format\n
    \t`data` - json with cookies and request headers
    """
    print(f"Downloading the video from the link: {url}")
    response = requests.get(url, cookies=data['cookies'], headers=data['headers'], stream=True)
    chunk_size = 1024
    
    if response.status_code == 200 and response.headers.get('Content-Type', '').startswith('video/'):
        try:
            total_size = int(response.headers.get('Content-Length', 0))
            with open(path, 'wb') as f, tqdm(total=total_size, unit='B', unit_scale=True) as pbar:
                for chunk in response.iter_content(chunk_size=chunk_size):
                    if chunk:
                        f.write(chunk)
                        pbar.update(len(chunk))

            return True
        except:
            print('Error downloading video')
            return False
    else:
        print('Error downloading video')
        return False

def get_video(save_path, url):
    """
    Getting a direct link to the video\n
    
    Accepts parameters:\n
    \t`save_path` - full path to save video, with file name (folders should already exist, before downloading)\n
    \t`url` - video link
    """
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.104 Safari/537.36"
    }
    cookies = {
        'accessAgeDisclaimerPH': '1',
        'hasVisited': '1',
        'd_fs': '1',
        '_gat': '1'
    }

    session = HTMLSession()
    r = session.get(url, cookies=cookies, headers=headers, timeout=10)
    html = r.text
    bs = BeautifulSoup(html, 'html.parser')
    
    script = bs.find('div', class_='original mainPlayerDiv').find('script').string
    script = script.strip()
    var_name = re.findall('var flashvars_(.*) =', script)[0]

    js = f"""
    () => {{
    var playerObjList = {{}}
    {script}
    var num = flashvars_{var_name}['mediaDefinitions'].length - 1
    while (flashvars_{var_name}['mediaDefinitions'][num]['format'] != "mp4")
    {{
        num -= 1
    }}
    return flashvars_{var_name}['mediaDefinitions'][num]['videoUrl']
    }}
    """

    r.html.render(script=js)
    time.sleep(1)

    s = session.get(url, cookies=cookies, headers=headers, timeout=5).text
    js_data = re.findall('= media_\d;(var .*?media_\d.*?;)', s)
    urls = []
    for i, j in enumerate(js_data):
        js = 'function test(a){ ' + j + 'return media_' + str(i + 1) + ';}'
        ss = execjs.compile(js)

        x_nul = ss.call('test', '1')
        urls.append(x_nul)
    nul = urls[-1]
    video_url = ''
    count = 0
    while video_url == '':
        video_url = session.get(nul, cookies=cookies, headers=headers, timeout=5).json()[count - 1]['videoUrl']
        count = count - 1
        if count < -3:
            break
    
    data = {"cookies": cookies, "headers": headers}
    return download_from_url(video_url, save_path, data)

if __name__ == '__main__':
    # Example
    FOLDER_DOWNLOAD = os.path.join(os.getcwd(), 'DOWNLOADS')
    path = os.path.join(FOLDER_DOWNLOAD, '3232', '3233.mp4')
    get_video(path, f"https://rt.pornhub.com/view_video.php?viewkey=ph6012baf3be306")