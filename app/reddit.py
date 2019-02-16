import os
import requests
import time
from datetime import datetime, timedelta
from . import etc


def download_images(posts, export_directory):
    for post in posts:
        try:
            post_name = post['permalink'].split('/')[-2]
            post_url = post['url']
            post_domain = post['domain']

            if post_domain == 'gfycat.com':
                post_url = post_url[:8] + 'zippy.' + post_url[8:] + '.webm'
            if post_url.endswith('gifv'):
                post_url = post_url[:-4] + 'mp4'

            _, extension = os.path.splitext(post_url)
            if extension is not None:
                etc.download_image_from_url(post_url, export_directory,
                                            post_name + extension)
            else:
                etc.download_image_from_url(post_url, export_directory)

        except (FileNotFoundError, OSError):
            pass


def get_subreddit_posts(subreddit, min_karma, days=7, verbose=True):
    '''
    Retrieve posts from a subreddit
    '''

    # Access reddit JSON api and retrieve posts
    # sorted by date (newest first)
    BASE_REQUEST = 'http://reddit.com/r/{}/new.json?sort=new&count=25'\
                   .format(subreddit)
    HEADERS = {'user-agent': 'Mozilla/5.0'}

    # Use any timezone as long as we use the same when converting post UTC
    expire_date = datetime.now() - timedelta(days=days)

    # after changes pages BASE_REQUEST?after=xxx
    # where 'xxx' is defined by the json returned from the last request
    after = ''

    posts = []

    processing = True
    while processing:
        response = requests.get(BASE_REQUEST + '&after=' + after,
                                headers=HEADERS)
        sub_data = response.json()['data']

        for post in sub_data['children']:

            if verbose:
                print('.', end='')

            post = post['data']
            creation_date = datetime.fromtimestamp(
                time.mktime(time.localtime(post['created'])))

            if creation_date < expire_date:
                processing = False
                break
            elif post['ups'] < min_karma:
                continue
            else:
                posts.append(post)

        after = sub_data['after']
        if after == 'null' or after is None:
            processing = False

    if verbose:
        print('')  # newline

    return posts


def scrape(subreddits, export_directory, days=7, verbose=True):
    """Perform reddit scrape routine."""

    if verbose:
        subreddits = etc.verbose_iter(subreddits, 'Scanning subreddits')

    # Retrieve reddit posts
    posts = []
    for subreddit in subreddits:
        posts += get_subreddit_posts(
            subreddit=subreddit['name'],
            min_karma=subreddit['min_karma'],
            days=days,
            verbose=verbose
        )

    # Download files
    if verbose:
        posts = etc.verbose_iter(posts, 'Downloading reddit images')

    download_images(posts, export_directory)
