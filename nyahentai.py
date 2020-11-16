# coding:utf-8
import os
import re

import requests
import multiprocessing as mp
from scrapy.selector import Selector

_base_url = ''
_name_xpath = '//*[@id="info"]/h1/text()'
_page_xpath = '//*[@id="thumbnail-container"]/div[*]/a/@href'
# _img_xpath = '//*[@id="image-container"]/a/img/@src'
_img_xpath = '/html/body/div[1]/div/section[2]/a/img/@src'


def img_dl(filename, url):
    try:
        html = requests.get(url)

        if html.status_code == 404:
            name = os.path.basename(filename)

            url, _ = url.split(name)
            filename, _ = filename.split(name)

            name, back = name.split('.')
            back = '.jpg' if back == 'png' else '.png'
            name = name + back

            url = url + name
            filename = filename + name

            html = requests.get(url)

        img = html.content
        if len(img) == 0:
            with open('cache', 'a') as f:
                f.write(filename+' '+url+'\n')
        with open(filename, 'wb') as f:
            f.write(img)
    except:
        with open('cache', 'a') as f:
            f.write(filename+' '+url+'\n')


def name_g(selector):
    name = selector.xpath(_name_xpath).get()
    return filename_verify(name) if name else False


def pages_g(selector):
    pages = selector.xpath(_page_xpath).getall()
    return pages


def src_g(href):
    url = _base_url + href
    html = requests.get(url).content
    selector = Selector(text=html)
    src = selector.xpath(_img_xpath).get()
    return src


def filename_verify(title):
    rstr = r"[\/\\\:\*\?\"\<\>\| ]"
    new_title = re.sub(rstr, "_", title)
    return new_title


def book_p(url, pool, path='D:/user/Pictures/New'):
    global _base_url
    _base_url = url.split('/g/')[0]
    print(_base_url)
    html = requests.get(url).content
    selector = Selector(text=html)

    book_name = name_g(selector)
    if not book_name:
        with open('fail_url.txt', 'a') as f:
            f.write(url + '\n')
        return

    path = os.path.join(path, book_name)
    if not os.path.exists(path):
        os.mkdir(path)

    pages = pages_g(selector)
    if not pages:
        with open('fail_url.txt', 'a') as f:
            f.write(url + '\n')
        return

    for href in pages:
        try:
            src = src_g(href)
            print(src)
        except:
            with open('fail_url.txt', 'a') as f:
                f.write(url + '\n')
            return
        name = os.path.basename(src)
        filename = os.path.join(path, name)
        pool.apply_async(img_dl, (filename, src, ))

        # src, _ = src.split(name)
        # name, back = name.split('.')
        # back = '.jpg' if back == 'png' else '.png'
        # name = name + back
        # src = src + name
        # filename = os.path.join(path, name)
        # pool.apply_async(img_dl, (filename, src, ))


if __name__ == "__main__":
    pool = mp.Pool(mp.cpu_count())

    with open('url.txt', 'r') as f:
        url_iter = map(str.strip, f.readlines())
    for url in url_iter:
        print(url)
        book_p(url, pool)

    # while os.path.getsize('cache') != 0:
    #     with open('cache', 'r+') as f:
    #         lines = map(str.strip, f.readlines())
    #         pages = map(str.split, lines)
    #         f.truncate()
    #     for filename, url in pages:
    #         print(url)
    #         pool.apply_async(img_dl, (filename, url, ))

    # while os.path.getsize('fail_url.txt') != 0:
    #     with open('fail_url.txt', 'r+') as f:
    #         url_iter = map(str.strip, f.readlines())
    #         f.truncate()
    #     for url in url_iter:
    #         print(url)
    #         book_p(url, pool)

    pool.close()
    pool.join()
