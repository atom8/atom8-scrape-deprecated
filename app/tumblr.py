import etc
import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

# Provides access to tumblr blog and returns 25 of photo posts starting from
# a variable index.
REQUEST_COUNT = 25
BASE_TUMBLR_REQUEST = \
    'http://{0}.tumblr.com/api/read?type=photo&num=' + str(REQUEST_COUNT) + \
    '&start={1}'


def retrieve_tumblr_blog_photo_posts(tumblr_blog, verbose=False, days=7):
    '''
    Retrive posts from a tumblr blog
    '''

    expire_date = datetime.now() - timedelta(days=days)

    start = 0
    image_URLs = []

    processing = True
    while processing:
        response = requests.get(BASE_TUMBLR_REQUEST.format(tumblr_blog, start))

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

            # ignore anything without a photo-url
            photo_url = post.find('photo-url')
            if photo_url is None:
                continue

            post_info = {
                'id': post['id'],
                'url': post.find('photo-url').text
            }
            image_URLs.append(post_info)

        start += REQUEST_COUNT

    if verbose:
        print('')

    return image_URLs


def scrape(tumblr_blogs, export_directory, verbose=False, days=7):
    # BASE_REQUEST = 'http://thecollectibles.tumblr.com'

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
        _, ext = os.path.splitext(tumblr_post['url'])

        etc.download_image_from_url(
            tumblr_post['url'], export_directory, tumblr_post['id'] + ext)


if __name__ == '__main__':
    TEST_BLOGS = ['thecollectibles', 'gamedevinspo']

    export_directory = etc.timestamp_directory(
        etc.find_desktop(), prefix='tumblr')
    etc.create_directory(export_directory)

    scrape(TEST_BLOGS, export_directory, verbose=True)
