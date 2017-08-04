# import json
import requests
import time
from datetime import datetime, timedelta


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


def trim_posts_under_score(posts, thresh):
    posts = []
    for post in posts:
        post = post['data']
        if post['ups'] >= thresh:
            posts.append(post)
    return posts
