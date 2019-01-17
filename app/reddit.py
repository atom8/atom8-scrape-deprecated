import click
import json
import os
import requests
import time
from datetime import datetime, timedelta
from . import etc


def verbose_iter(lst, message):
    tot_length = len(lst)
    curr = 0

    for item in lst:
        curr += 1
        print("%s (%d/%d)" % (message, curr, tot_length))
        yield item


def get_posts_by_date(subreddit, days=7, min_score=None, verbose=False):
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
            post = post['data']
            creation_date = datetime.fromtimestamp(
                time.mktime(time.localtime(post['created'])))

            if creation_date < expire_date:
                processing = False
                break
            elif min_score and post['ups'] < min_score:
                continue
            else:
                posts.append(post)

        after = sub_data['after']
        if after == 'null' or after is None:
            processing = False

        if verbose:
            print("\nAfter: {}\nLast Created: {}".format(after, creation_date))

    return posts


def get_all_posts_from_subreddits(subreddits):
    # TODO different date ranges

    posts = []
    for subreddit in subreddits:
        subreddit_posts = get_posts_by_date(
            subreddit=subreddit['name'],
            min_score=subreddit['min_karma'],
            days=7,
        )
        posts += subreddit_posts
    return posts


def download_images(posts, export_directory):
    post_num = 0
    post_info = ''

    for post in posts:
        post_num += 1
        try:
            post_url = post['url']
            post_domain = post['domain']

            if post_domain == 'gfycat.com':
                post_url = post_url[:8] + 'zippy.' + post_url[8:] + '.webm'
            if post_url.endswith('gifv'):
                post_url = post_url[:-4] + 'mp4'

            _, extension = os.path.splitext(post_url)
            if extension is not None:
                etc.download_image_from_url(post_url, export_directory,
                                            str(post_num) + extension)
            else:
                etc.download_image_from_url(post_url, export_directory)

            post_info += "{:>3}\t{}\n{}\n{}\n\n".format(
                post_num, post['author'],
                post['permalink'].encode('utf-8'),
                post_url)
        except (FileNotFoundError, OSError):
            pass

    return post_info


def scrape(subreddits, export_directory, verbose=False):
    """Perform reddit scrape routine."""

    # Retrieve reddit posts
    reddit_posts = []
    if verbose:
        reddit_posts = get_all_posts_from_subreddits(
            verbose_iter(subreddits, 'Scanning subreddits'))
    else:
        reddit_posts = get_all_posts_from_subreddits(subreddits)

    # Extract post data and download files
    post_results = ''

    if verbose:
        post_results = download_images(
            verbose_iter(reddit_posts, 'Downloading reddit images'),
            export_directory)
    else:
        post_results = download_images(reddit_posts, export_directory)

    # Export post data
    # TODO sort posts by highest karma
    with open(os.path.join(export_directory, 'export_reddit.json'), 'w') as f:
        json.dump(reddit_posts, f, indent=4)

    # Export post_results
    with open(os.path.join(export_directory, 'export_reddit.txt'), 'w') as f:
        f.write(post_results)


def trim_posts_under_score(posts, thresh):
    posts = []
    for post in posts:
        post = post['data']
        if post['ups'] >= thresh:
            posts.append(post)
    return posts
