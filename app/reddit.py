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


def scrape(subreddits, export_folder, verbose=False):
    """Perform reddit scrape routine."""

    # Retrieve reddit posts
    # TODO different date ranges
    reddit_posts = []
    with click.progressbar(subreddits, label='Scanning subreddits') as bar:
        for subreddit in bar:
            subreddit_posts = reddit_control.get_posts_by_date(
                subreddit=subreddit['name'],
                min_score=subreddit['min_karma'],
                days=7,
            )
            reddit_posts += subreddit_posts

    # Extract post data and download files
    post_num = 0
    post_info = ''

    with click.progressbar(reddit_posts, label='Downloading posts') as bar:
        for post in bar:
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
                    download_image_from_url(post_url, export_folder,
                                            str(post_num) + extension)
                else:
                    download_image_from_url(post_url, export_folder)

                post_info += "{:>3}\t{}\n{}\n{}\n\n".format(
                    post_num, post['author'],
                    post['permalink'].encode('utf-8'),
                    post_url)
            except (FileNotFoundError, OSError) as e:
                pass

    # Export post data
    # TODO sort posts by highest karma
    with open(os.path.join(export_folder, 'export_reddit.json'), 'w') as f:
        json.dump(reddit_posts, f, indent=4)

    # Export post_info
    with open(os.path.join(export_folder, 'export_reddit.txt'), 'w') as f:
        f.write(post_info)


def trim_posts_under_score(posts, thresh):
    posts = []
    for post in posts:
        post = post['data']
        if post['ups'] >= thresh:
            posts.append(post)
    return posts
