import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from . import etc

# Provides access to tumblr blog and returns 25 of photo posts starting from
# a variable index.
REQUEST_COUNT = 25
BASE_TUMBLR_REQUEST = \
    'http://{0}.tumblr.com/api/read?type=photo&num=' + str(REQUEST_COUNT) + \
    '&start={1}'


def retrieve_tumblr_blog_photo_posts(tumblr_blog, days=7, verbose=True):
    '''
    Retrive posts from a tumblr blog
    '''

    expire_date = datetime.now() - timedelta(days=days)

    start = 0
    image_URLs = []

    processing = True
    while processing:
        req = BASE_TUMBLR_REQUEST.format(tumblr_blog, start)
        response = requests.get(req)

        if not response.ok:
            if verbose:
                print("[ERROR] Bad response (" + req + ")")
            processing = False
            break

        tumblr_data = BeautifulSoup(response.text, 'lxml')
        tumblr_posts = tumblr_data.find_all('post')

        for post in tumblr_posts:

            if verbose:
                print('.', end='')

            # ignore if post was before expire date
            posted_on = datetime.strptime(
                post['date'],
                '%a, %d %b %Y %H:%M:%S')
            if posted_on < expire_date:
                processing = False
                break

            # caption
            caption = post.find('photo-caption')
            if caption is not None:
                caption = caption.text
            else:
                caption = ''

            # ignore anything without a photo-url
            photo_url = post.find('photo-url')
            if photo_url is None:
                continue

            _, ext = os.path.splitext(photo_url.text)
            post_info = {
                'author': tumblr_blog,
                'date': str(posted_on),
                'ref': post['id'] + ext,
                'source': photo_url.text,
                'text': caption
            }
            image_URLs.append(post_info)

        start += REQUEST_COUNT

    if verbose:
        print('')

    return image_URLs


def scrape(tumblr_blogs, export_directory, days=7, verbose=True):
    if verbose:
        tumblr_blogs = etc.verbose_iter(tumblr_blogs, 'Scanning tumblr blogs')

    tumblr_posts = []
    for tumblr_blog in tumblr_blogs:
        tumblr_posts += retrieve_tumblr_blog_photo_posts(
            tumblr_blog, days=days, verbose=verbose)

    if verbose:
        tumblr_posts = etc.verbose_iter(
            tumblr_posts, 'Downloading tumblr images')

    for tumblr_post in tumblr_posts:
        etc.download_image_from_url(
            tumblr_post['source'], export_directory, tumblr_post['ref'],
            metadata=tumblr_post)
